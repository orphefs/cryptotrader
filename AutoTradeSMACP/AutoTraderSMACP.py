from binance.client import Client
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

"""
Auto Trade SMA/EMA v0.1
By Jordan Schlak
"""
"""
This code takes historical Cryptocurrency candle values and live data
in order to compute good buying and selling prices. Currently the
relation between the current price and the last closing candle
EMA value in order to determine if the value is temperarily
"heading up/down" and it uses the closing SMA values from one
candle ago vs the closing value two candles ago in order to
compute a more long term trending direction.

I understand this is simple and I would like to add more indicators
and complexity to future iterations

Still need to find good rule of thumb for money to put into he system.
I think I will start with fixed value of 100 dollars the bot can trade.
I have tested the documented api buy/sell orders and they are effective
and easy to work with.

Might be a good idea to append SMA with current value before doing computation
Might throw off indices for graphs and other calculations though

Add x and y labels to graph
"""


"""
Suggested variables to change
"""
"""
p period    -number of candles you would like to average over
d delay     -how long in second you would like the code to sleep between iterations
mini/maxi   -minimum and maximum candles you would like to plot, from 0-499
NEOUSDT      I am trading NEO, feel free to add your own curency
a           -amount you would like to trade
"""


"""
#User Input
"""

pl=60
ps=10
d=10
SMA=[0]*(pl-1)
EMA=[0]*(pl-1)
buy=[]
sell=[]
prof=[]
bought=0
money=0


#Modifiable On/Off text file reading
txt = open('onoff.txt','r')
onoff = int(txt.read(1))

#Binance login
while onoff == 1:
    api_key = "<enter api key>"
    api_secret = "<enter secret key>"
    client = Client(api_key, api_secret)

    #obtain candles
    candles = client.get_klines(symbol='NEOUSDT', interval=Client.KLINE_INTERVAL_30MINUTE)
    trades = client.get_recent_trades(symbol='NEOUSDT',limit = 1)

    #extract of closing candle values and current value
    candles = list(map(float,np.array(candles)[:,4]))
    cv = float(trades[0]['price'])

    #function computes SMA and EMA based on period fed to it
    def fSMA(p,candles):
        for i in range(p-1,len(candles)):
            M = 2/(p+1)
            SMA.append((sum(candles[i-p+1:i+1]))/p)
            EMA.append((candles[i]-(EMA[i-1]))*M+EMA[i-1])

    #Running function in order to extract long term SMA and short term EMA 
    fSMA(pl,candles)
    SMA60=SMA
    fSMA(10,candles)
    EMA10=EMA

    """
    Plotting
    """
    """
    red    = SMA(60)
    yellow = EMA(10)
    """
    plt.close()
    t = list(range(0,500))
    mini = 450
    maxi = 500
    plt.plot(t[mini:maxi],candles[mini:maxi], 'bo', t[mini:maxi], candles[mini:maxi], 'g-', t[mini:maxi],EMA10[mini:maxi], 'y-', t[mini:maxi], SMA60[mini:maxi], 'r-')
    plt.show(block=False)
    
    """
    Trading Logic
    """
    """
    If the price is trending down and heading up, it is a good time to buy
    If the price is trending up and heading down, it is a good time to sell

    Run this code in real time in order to save profit values and eventually
    enable the buy and sell orders
    """
    trend = SMA60[499]-SMA60[498]
    head = cv-EMA10[499]

    money = cv

    #Trends
    if trend > 0:
        strend = "Uptrend"
    else:
        strend = "Downtrend"
        
    #Headings
    if head > 0:
        shead = 'Heading Up'
    else:
        shead = 'Heading Down'
        
    #Decision Making
    if strend == "Uptrend" and shead == "Heading Up" and bought==0:
        if bought == 1:
            print('Current price is {}'.format(cv))
            print('Uptrend at {}, Heading Up at {}\n'.format(trend, head))
        elif bought == 0:
            print('Uptrend at {}, Heading Up at {}'.format(trend, head))
            buy.append(cv)
            bought=1
            print('bought at {}]n'.format(cv))

    if strend == "Uptrend" and shead == "Heading Down" and bought ==1:
        if bought == 0:
            print('Current price is {}'.format(cv))
            print('Uptrend at {}, Heading Down at {}\n'.format(trend, head))
        elif bought == 1:
            sell.append(cv)
            bought=0
            print('Uptrend at {}, Heading Down at {}\n'.format(trend, head))
            print('sold at {}'.format(cv))
            prof.append(sell[len(sell)-1]-buy[len(buy)-1]-money*cv)
            print()
            print('bought at {}, sold at {}'.format(buy(len(buy-1))))
            print('trade profit is {}, total profit is {}\n'.format(prof[len(prof)]), sum(prof))
            
    if strend == "Downtrend" and shead == "Heading Down":
        if bought == 0:
            print('Current price is {}'.format(cv))
            print('Downtrend at {}, Heading Down at {}\n'.format(trend, head))

        elif bought ==1:
            print('Downtrend {}, Heading Down {}\n'.format(trend, head))
            print('new sell at {}'.format(cv))
            sell.append(cv)
            prof.append(sell[len(sell)-1]-buy[len(buy)-1]-money*cv)
            bought=0
            print('bought at {}, sold at {}'.format(buy(len(buy-1))))
            print('trade profit is {}, total profit is {}\n'.format(prof[len(prof)]), sum(prof))
                
    if strend == "Downtrend" and shead == "Heading Up":
        if bought == 1:
            print('Current price is {}'.format(cv))
            print('Downtrend at {}, Heading Up at {}\n'.format(trend, head))

        elif bought == 0:
            buy.append(cv)
            print('Downtrend at {}, Heading Up {}\n'.format(trend, head))
            print('new buy at {}'.format(cv))
            bought=1
            
    time.sleep(d)


