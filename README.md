# Grid Bot

Automates a grid trading strategy for crypto

# Setup

Set up `keys.json` with your KuCoin API keys. There is an example for how to do this in `keys.json.example`. Make sure that the API key that you use has trading permissions.

# Example Settings

Edit the settings in `settings.json`. Here are the parameters:

- `coin: string` - the symbol of cryptocurrency that you are trading (ex. BTC, ETH)
- `base: string` - the symbol of what you are using to trade with (ex. USDT, BTC)
- `orders: int` - the number of order that you would like to be placed at once (should be even, half above the center and half below)
- `order_size: float` - the amount of units in the base currency to buy or sell at each order
- `center_float: float` - the price of the coin in units of the base in the middle of the trading range
- `spacing: float` - how far to space out each order
