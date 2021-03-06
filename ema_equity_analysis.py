from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.timeseries import TimeSeries
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters
import numpy as np
from PIL import Image
import math
from datetime import date
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpl_finance import volume_overlay
import matplotlib.ticker as mticker
from matplotlib import ticker
from mpl_finance import candlestick2_ohlc
import seaborn as sns
import pylab
from discord_webhook import DiscordWebhook, DiscordEmbed
from scipy.stats import linregress
from roughsr2 import find_resistance, find_support

pd.options.mode.chained_assignment = None 


sns.set(style='darkgrid', context='talk', palette='Dark2')

#Enter Ticker Symbol
Ticker = ''

df = Ticker


for xx in df:
    ################## Set knowledge of what channel to send to
    now = datetime.datetime.now()
    today = date.today()   
    ################## Call api and properly set up dataset    
    try:
        ts = TimeSeries(key='-----------',output_format='pandas')
        data, meta_data = ts.get_intraday(symbol= xx,interval='30min', outputsize='full')
        data.sort_values('date', inplace=True, ascending=True)
    except ValueError as bash:
        data = bash
        continue
        
    ################## Carry out calculations
    ema_short_rolling = data.ewm(span=20, adjust=False).mean()
    ema_long_rolling = data.ewm(span=100, adjust=False).mean()
    mb = data.ewm(span=60, adjust=False).mean()
    ub = mb + (data['4. close'].std() / 2)
    lb = mb - (data['4. close'].std() / 2)
    ################## Put in knowledge of yay or nay
    sums = ema_short_rolling.tail(1)
    suml = ema_long_rolling.tail(1)
    ################## Put in knowledge of yay or nay
    sums = sums['1. open'].sum(axis = 0, skipna = True)
    suml = suml['1. open'].sum(axis = 0, skipna = True)
    ###################
    maxx = ub['4. close'].tail(600).max(axis = 0, skipna = True)
    minn = lb['4. close'].tail(600).min(axis = 0, skipna = True)
    ###################
    pctsig = sums / suml


    if .999 <= pctsig <= 1.001:
    
    '''use for testing'''
    #if pctsig == pctsig:
    
    ###################
        low = data['4. close'].tail(600)
        high = data['1. open'].tail(600)
        min_touches = 2
        stat_likeness_percent = 15
        bounce_percent = 0
    
        """
        ** Note **
            If you want to calculate support and resistance without regard for
            candle shadows, pass close values for both low and high.
        Returns:
            sup: level of support or None (if no level)
            res: level of resistance or None (if no level)
        """
    # Setting default values for support and resistance to None
        sup = None
        res = None
    
    # Identifying local high and local low
        maxima = high.max()
        minima = low.min()
    
    # Calculating distance between max and min (total price movement)
        move_range = maxima - minima
    
    # Calculating bounce distance and allowable margin of error for likeness
        move_allowance = move_range * (stat_likeness_percent / 100)
        bounce_distance = move_range * (bounce_percent / 100)
    
    # Test resistance by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(high)):
            if abs(maxima - high[x]) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(maxima - high[x]) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            res = maxima
        else:
            pass
        
    # Test support by iterating through data to check for touches delimited by bounces
        touchdown = 0
        awaiting_bounce = False
        for x in range(0, len(low)):
            if abs(low[x] - minima) < move_allowance and not awaiting_bounce:
                touchdown = touchdown + 1
                awaiting_bounce = True
            elif abs(low[x] - minima) > bounce_distance:
                awaiting_bounce = False
        if touchdown >= min_touches:
            sup = minima
        else:
            pass
    
    ###################
    
        data2 = data.tail(600)
        data2.reset_index(level=0,inplace=True)
        data2['date'] = pd.to_datetime(data2['date'])
        data2['date'] = data2['date'].apply(mdates.date2num)


    ###################
    # high trend line

        data1 = data2

        while len(data1)>12:

            reg = linregress(
                        x=data1.index,
                        y=data1['1. open'],
                        )
            data1 = data1.loc[data1['1. open'] > reg[0] * data1.index + reg[1]]

            reg = linregress(
                        x=data1.index,
                        y=data1['1. open'],
                        )

            data2['high_trend'] = reg[0] * data2.index + reg[1]

    # low trend line

        data1 = data2
        while len(data1)>12:
            reg = linregress(
                        x=data1.index,
                        y=data1['4. close'],
                        )
            data1 = data1.loc[data1['4. close'] < reg[0] * data1.index + reg[1]]

            lreg = linregress(
                        x=data1.index,
                        y=data1['4. close'],
                        )

            data2['low_trend'] = reg[0] * data2.index + reg[1]
    
    ###################
    
        fig, (ax1,ax2) = plt.subplots(2,sharex=True,figsize=(24,12),gridspec_kw={'height_ratios':[5,2]})

        data = data.tail(400)

                
        candlestick2_ohlc(ax1, data['1. open'],data['2. high'],data['3. low'],data['4. close'], width=0.3, colorup='g', colordown='r');
        ema_short_rolling['1. open'].tail(400).plot(ax=ax1, grid = True, color = 'r', linewidth=.5)
        ema_long_rolling['1. open'].tail(400).plot(ax=ax1, grid = True, color = 'green', linewidth=.5)

        volume_overlay(ax2,data['1. open'],data['4. close'], data['5. volume'], colorup='g',colordown='r', width=1, alpha = .5) 

        try:
            res = res
            ax1.axhline(y = res, linewidth = '.5', color = 'black')
            ax1.annotate(res,(data2.index[-1]+.08 ,res))
        except: pass

        try:
            sup = sup
            ax1.axhline(y = sup, linewidth = '.5', color = 'black')
            ax1.annotate(sup,(data2.index[-1]+.08 ,sup))
        except: pass

        ax1.axhline(y=maxx, linewidth = '.5', color='black')
        ax1.axhline(y=minn, linewidth = '.5', color='black')

        data2['high_trend'].tail(400).plot(ax=ax1, grid = True, color = 'black', linewidth=.5)
        data2['low_trend'].tail(400).plot(ax=ax1, grid = True, color = 'black', linewidth=.5)

        ax1.fill_between(data2.index, data2['low_trend'],data2['high_trend'],facecolor='b', alpha = .1)

        ax1.annotate(sup,(data2.index[-1]+.08 ,sup))
        ax1.annotate(data['4. close'].iloc[-1],(data2.index[-1]+.08 ,data['2. high'].tail(1)))

        vol = data['5. volume'].iloc[-1]
        ax2.annotate(f'{vol:,}',(data2.index[-1]+.06 ,data['5. volume'].iloc[-1]))


        xdate = data.index
        def mydate(x, pos):
            try:
                return xdate[int(x)]
            except IndexError:
                return ''

        def millions(x, pos):
            'The two args are the value and tick position'
            return '$%1.1fM' % (x * 1e-6)


        formatter = ticker.FuncFormatter(millions)

        ax2.yaxis.set_major_formatter(formatter)

        ax2.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
        plt.xticks(rotation=0)

        dt = date.today()

        plt.tight_layout()
        ax1.set_title(xx, loc='left', fontsize=35)
        ax1.set_title(str('Interval: 30M'), loc='right', fontsize=20)
        ax1.set_title(str('Date: ')+now.strftime("%Y-%m-%d %I:%M:%S")+str('   ')+str('O: ')+str(data['1. open'].iloc[-1])+
                      str('    ')+str('H: ')+str(data['2. high'].iloc[-1])+str('    ')+str('L: ')+
                      str(data['3. low'].iloc[-1])+str('    ')+str('C: ')+
                      str(data['4. close'].iloc[-1]), fontsize=18)
        
        ax1.grid(linewidth=1)
        ax2.grid(linewidth=1)
        ax1.set_facecolor('lightgrey')
        ax2.set_facecolor('lightgrey')
        ax2.set_ylabel("Vol")
        ax1.set_ylabel("Price")
        plt.tight_layout()

        dt = date.today()

                
        '''save image'''
        plt.savefig('C:/------/' + xx +'_'+ str(date.today()) + '.jpg',facecolor = 'lightgrey')
        
        webhook = DiscordWebhook(url='')
        
        #create embed object for webhook
        embed = DiscordEmbed(title= xx, description='EMA - Alert'+' '+now.strftime("%Y-%m-%d %I:%M:%S"), color=242424)
        
        # set image
        
        with open('C:/--------/' + xx +'_'+ str(date.today()) + '.jpg', "rb") as f:
            webhook.add_file(file=f.read(), filename= xx +'_'+ str(date.today()) + '.jpg')
            
        # add embed object to webhook
        webhook.add_embed(embed)
        webhook.execute()
            
        plt.close()

    else:
        plt.close()
        pass
