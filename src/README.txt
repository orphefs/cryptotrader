
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
p period    -number of closing_prices you would like to average over
d delay     -how long in second you would like the code to sleep between iterations
mini/maxi   -minimum and maximum closing_prices you would like to plot, from 0-499
NEOUSDT      I am trading NEO, feel free to add your own curency
a           -amount you would like to trade
"""
