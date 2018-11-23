sell_order = {'symbol': 'TRXBNB',
              'orderId': 2005748,
              'clientOrderId': 'SvTTKARz43tDkb9D3asy5m',
              'transactTime': 1542930505233,
              'price': '0.00000000',
              'origQty': '500.00000000',
              'executedQty': '500.00000000',
              'cummulativeQuoteQty': '1.20450000',
              'status': 'FILLED',
              'timeInForce': 'GTC',
              'type': 'MARKET',
              'side': 'SELL',
              'fills': [
                  {'price': '0.00240900',
                   'qty': '500.00000000',
                   'commission': '0.00090337',
                   'commissionAsset': 'BNB',
                   'tradeId': 238156}]}

buy_order = {'symbol': 'TRXBNB',
             'orderId': 2005885,
             'clientOrderId': 'KIw7jvRhLej15vfKoUE7yD',
             'transactTime': 1542930822823,
             'price': '0.00000000',
             'origQty': '500.00000000',
             'executedQty': '500.00000000',
             'cummulativeQuoteQty': '1.21050000',
             'status': 'FILLED',
             'timeInForce': 'GTC',
             'type': 'MARKET',
             'side': 'BUY',
             'fills': [
                 {'price': '0.00242100',
                  'qty': '500.00000000',
                  'commission': '0.00090210',
                  'commissionAsset': 'BNB',
                  'tradeId': 238171}]}

print(buy_order)
print(sell_order)