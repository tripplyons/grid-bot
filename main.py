from kucoin.client import Client
import time
import json
import numpy as np

with open('keys.json', 'r') as f:
    keys = json.load(f)

with open('settings.json', 'r') as f:
    settings = json.load(f)

# the trading pair on KuCoin
pair = '{}-{}'.format(settings['coin'], settings['base'])

client = Client(keys["API_KEY"], keys["API_SECRET"], keys["API_PASSPHRASE"])

# current unix timestamp, in seconds (must convert to ms for KuCoin API calls)
def now():
    return int(time.time())

levels = []

decimals = settings['decimals']

max_orders = settings['orders']

for i in range(max_orders // 2):
    levels.append(round(settings['center'] - settings['spacing'] * (i + 0.5), decimals))
    levels.append(round(settings['center'] + settings['spacing'] * (i + 0.5), decimals))

levels = np.sort(levels)

def get_price():
    return float(client.get_ticker(pair)['price'])

def open_buy(level):
    print('Buy order at {}'.format(level))
    client.create_limit_order(pair, Client.SIDE_BUY, str(level), str(
        round(settings['order_size'] / level, decimals)
    ))

def open_sell(level):
    print('Sell order at {}'.format(level))
    client.create_limit_order(pair, Client.SIDE_SELL, str(level), str(
        round(settings['order_size'] / level, decimals)
    ))

def check_and_order():
    price = get_price()
    orders = client.get_orders(pair, limit=max_orders * 2, status='active')

    open_buy_orders = {}
    open_sell_orders = {}    

    for key in levels:
        open_buy_orders[key] = False
    for key in levels:
        open_sell_orders[key] = False

    for item in orders['items']:
        level = float(item['price'])
        if item['side'] == 'sell':
            open_sell_orders[level] = True
        else:
            open_buy_orders[level] = True

    profit_per_trade = 1
    
    for i in range(len(levels) - profit_per_trade):
        if levels[i + profit_per_trade] < price:
            if not open_buy_orders[levels[i]]:
                open_buy(levels[i])
    for i in range(profit_per_trade, len(levels)):
        if levels[i - profit_per_trade] > price:
            if not open_sell_orders[levels[i]]:
                open_sell(levels[i])

# client.cancel_all_orders(symbol=pair)

while True:
    check_and_order()
    time.sleep(20)
