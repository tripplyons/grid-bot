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

buy_levels = []
sell_levels = []

orders_per_side = settings['orders'] // 2

for i in range(orders_per_side):
    buy_levels.append(settings['center'] - settings['spacing'] * (i + 0.5))
    sell_levels.append(settings['center'] + settings['spacing'] * (i + 0.5))

last_fill = ''

def get_price():
    return float(client.get_ticker(pair)['price'])

increment = 0

for i in client.get_symbols():
    if i['symbol'] == pair:
        increment = float(i['baseIncrement'])

decimals = int(np.log10(1 / increment))

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

def check_for_fills():
    orders = client.get_orders(pair, limit=settings['orders'] * 2, status='active')

    open_buy_orders = {}
    open_sell_orders = {}    

    for key in buy_levels:
        open_buy_orders[key] = False
    for key in sell_levels:
        open_sell_orders[key] = False

    for item in orders['items']:
        price = float(item['price'])
        if price > get_price():
            open_sell_orders[price] = True
        else:
            open_buy_orders[price] = True
    
    num_sell = len(list(filter(lambda x : float(x['price']) in sell_levels, orders['items'])))
    num_buy = len(list(filter(lambda x : float(x['price']) in buy_levels, orders['items'])))
    total = num_sell + num_buy
    error = orders_per_side * 2 - total

    if get_price() > sell_levels[0]:
        # refill buys
        for level in buy_levels:
            if not open_buy_orders[level]:
                open_buy(level)
                open_buy_orders[level] = True
        
        while error > 0:
            open_buy(buy_levels[0])
            error -= 1
    elif get_price() < buy_levels[0]:
        #refill sells
        for level in sell_levels:
            if not open_sell_orders[level]:
                open_sell(level)
                open_sell_orders[level] = True

        while error > 0:
            open_sell(sell_levels[0])
            error -= 1
    


def init_orders():
    client.cancel_all_orders(symbol=pair)
    for i in range(orders_per_side):
        open_buy(buy_levels[i])
        open_sell(sell_levels[i])

init_orders()

while True:
    time.sleep(10)
    check_for_fills()
