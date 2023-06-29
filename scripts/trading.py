import math
from time import sleep

import binance


class TradingStable:
    def __init__(self):
        API_KEY = "DSDjeZxUOTv12eZKsIbdEJzqMhm5WGdCDdia09nKAkDnUEU9IQ1uzqXVdP6gcE7g"
        SECRET_KEY = "kVKJP2QfNhCHmKw2OD7JXyQyMKfAJZwqODESCdDOqqph93nVESWFvUXwwVWuM8Hu"
        self.client = binance.Client(API_KEY, SECRET_KEY)
        self.usdt = 0.0
        self.tusd = 0.0

    def get_open_orders(self, symbol):
        open_orders = self.client.get_open_orders(symbol=symbol)
        return open_orders

    def getTrades(self, symbol):
        return self.client.get_recent_trades(symbol=symbol)

    def getLast10Minutes(self, symbol):
        klines = self.client.get_klines(symbol=symbol, interval=binance.Client.KLINE_INTERVAL_1MINUTE, limit=10)
        closes = [float(kline[2]) for kline in klines]
        sum=0
        for i in closes:
            sum+= i
        previous_close = round((sum/len(closes)),4)
        current_close = closes[-1]
        if current_close > previous_close:
            return "UP"
        elif current_close < previous_close:
            return "DOWN"
        else:
            return "SIDEWAYS"

    def recalibrateOrders(self, symbol, current_price):
        open_orders = self.get_open_orders(symbol=symbol)

        for order in open_orders:
            if order['side'] == 'BUY':
                buy_price = float(order['price'])
                if current_price < buy_price:
                    sell_price = round(current_price - 0.0001, 4)
                    sell_quantity = float(order['executedQty'])
                    self.placeOrder(symbol, 'SELL', sell_price, sell_quantity)
                    self.client.cancel_order(symbol=symbol, orderId=order['orderId'])
            elif order['side'] == 'SELL':
                sell_price = float(order['price'])
                if current_price > sell_price:
                    buy_price = round(current_price + 0.0001, 4)
                    buy_quantity = float(order['executedQty'])
                    self.placeOrder(symbol, 'BUY', buy_price, buy_quantity)
                    self.client.cancel_order(symbol=symbol, orderId=order['orderId'])

    def placeOrder(self, symbol, side, price, quantity):
        symbol_info = self.client.get_symbol_info(symbol)
        lot_size_filter = next(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))
        step_size = float(lot_size_filter['stepSize'])
        quantity = int(quantity / step_size) * step_size  # Ensure only full tokens are used for quantity

        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            timeInForce="GTC",
            price=price,
            quantity=quantity
        )
        print(f"Placed {side} order: Quantity={quantity}, Price={price}")

    def logic(self, symbol):
        current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])+0.0001
        self.available()
        if self.tusd >= 1:
            self.placeOrder(symbol,"SELL",current_price,quantity=self.tusd)
        while True:
            sleep(10)
            current_price = float(self.client.get_symbol_ticker(symbol=symbol)['price'])
            direction = self.getLast10Minutes(symbol)
            print(f"Current direction: {direction}, Current price: {current_price}")
            self.available()
            self.recalibrateOrders(symbol, current_price)

    def available(self):
        self.usdt = float(self.client.get_asset_balance("USDT")["free"])
        self.tusd = float(self.client.get_asset_balance("TUSD")["free"])


tds = TradingStable()
tds.logic("TUSDUSDT")