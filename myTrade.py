import pandas as pd
from binance.um_futures import UMFutures
from datetime import datetime
from binance.error import ClientError
import time
import logging
from binance.lib.utils import config_logging

today = datetime.now().strftime('%Y-%m-%d')
log_file = f"log_{today}.txt"
config_logging(logging, logging.DEBUG, log_file=log_file)

# HMAC authentication with API key and secret
api = ""
secret = ""
hmac_client = UMFutures(key=api, secret=secret)

# 合约账户有多少钱
def get_balance_usdt(client_now):
    try:
        response = client_now.balance(recvWindow=6000)
        for elem in response:
            if elem['asset'] == 'USDT':
                return float(elem['balance'])

    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Getting all available symbols on the Futures ('BTCUSDT', 'ETHUSDT', ....) or one symbol
def get_tickers_usdt(client_now, symbol=None):
    try:
        tickers = []
        resp = client_now.ticker_price(symbol)
        if symbol == None:
            for elem in resp:
                if 'USDT' in elem['symbol']:
                    tickers.append(elem)
            return tickers
        else:
            tickers.append(resp)
            return tickers
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


# Set leverage for the needed symbol. You need this bcz different symbols can have different leverage
def set_leverage(client_now, symbol, level):
    try:
        response = client_now.change_leverage(
            symbol=symbol, leverage=level, recvWindow=6000
        )
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# The same for the margin type
def set_mode(client_now, symbol, type):
    # ISOLATED, CROSSED
    try:
        response = client_now.change_margin_type(
            symbol=symbol, marginType=type, recvWindow=6000
        )
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Price precision. BTC has 1, XRP has 4
def get_price_precision(client_now, symbol):
    try:
        resp = client_now.exchange_info()['symbols']
        for elem in resp:
            if elem['symbol'] == symbol:
                return elem['pricePrecision']
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


# Amount precision. BTC has 3, XRP has 1
def get_qty_precision(client_now, symbol):
    try:
        resp = client_now.exchange_info()['symbols']
        for elem in resp:
            if elem['symbol'] == symbol:
                return elem['quantityPrecision']
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


# Open new order with the last price, and set TP and SL:
def open_order(client_now, symbol, side, volume, tp, sl, price = None):
    price_get = float(client_now.ticker_price(symbol)['price'])
    if price == None:
        price = price_get
    qty_precision = get_qty_precision(client_now, symbol)
    price_precision = get_price_precision(client_now, symbol)
    qty = round(volume/price, qty_precision)
    if side == 'BUY':
        try:
            if price <= price_get: #买时一定低价买，否则会直接交易成功
                resp1 = client_now.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
                logging.info(f"{symbol},{side},placing order")
                logging.info(resp1)
                time.sleep(0.5)
                sl_price = round(price - price * sl, price_precision)
                resp2 = client_now.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
                logging.info(resp2)
                time.sleep(0.5)
                tp_price = round(price + price * tp, price_precision)
                resp3 = client_now.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC',
                                         stopPrice=tp_price)
                logging.info(resp3)
            else:
                logging.error(f"your setting buy price({price}) is higher than latest price({price_get})")
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
    if side == 'SELL':
        try:
            if price >= price_get: #卖时一定高价卖，否则会直接交易成功
                resp1 = client_now.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
                logging.info(symbol, side, "placing order")
                logging.info(resp1)
                time.sleep(0.5)
                sl_price = round(price + price*sl, price_precision)
                resp2 = client_now.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
                logging.info(resp2)
                time.sleep(0.5)
                tp_price = round(price - price * tp, price_precision)
                resp3 = client_now.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC',
                                         stopPrice=tp_price)
                logging.info(resp3)
            else:
                logging.error(f"your setting sell price({price}) is lower than latest price({price_get})")
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
# 只减仓订单
def open_order_reduceOnly(client_now, symbol, side, qty):
    if side == 'BUY':
        try:
            resp1 = client_now.new_order(symbol=symbol, side='BUY', type='MARKET', reduceOnly = 'true', quantity=qty, timeInForce='GTC')
            logging.info(f"{symbol},{side},placing order")
            logging.info(resp1)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
    if side == 'SELL':
        try:
            resp1 = client_now.new_order(symbol=symbol, side='SELL',type='MARKET', reduceOnly = 'true', quantity=qty, timeInForce='GTC')
            logging.info(symbol, side, "placing order")
            logging.info(resp1)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

# Your current positions (returns the symbols list):
def get_pos(client_now,symbol = None):
    try:
        if symbol == None:
            resp = client_now.get_position_risk()
        else:
            resp = client_now.get_position_risk(symbol=symbol)
        pos = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos.append(elem['symbol'])
        return pos
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# 获得持仓数量，正数为多，负数为空
def get_pos_amt(client_now,symbol = None):
    try:
        if symbol == None:
            resp = client_now.get_position_risk()
        else:
            resp = client_now.get_position_risk(symbol=symbol)
        pos_amt = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos_amt.append(elem['positionAmt'])
        return pos_amt
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
def get_pos_entryPrice(client_now,symbol = None):
    try:
        if symbol == None:
            resp = client_now.get_position_risk()
        else:
            resp = client_now.get_position_risk(symbol=symbol)
        pos = []
        for elem in resp:
            if float(elem['positionAmt']) != 0:
                pos.append(elem['entryPrice'])
        return pos
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
def check_orders(client_now,symbol = None):
    try:
        if symbol == None:
            response = client_now.get_orders(recvWindow=6000)
        else:
            response = client_now.get_orders(symbol=symbol, recvWindow=6000)
        sym = []
        for elem in response:
            sym.append(elem['symbol'])
        return sym
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

# Close open orders for the needed symbol. If one stop order is executed and another one is still there
def close_open_orders(client_now, symbol):
    try:
        response = client_now.cancel_open_orders(symbol=symbol, recvWindow=6000)
        logging.info(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )

logging.info(get_balance_usdt(hmac_client))
logging.info(get_tickers_usdt(hmac_client,'BTCUSDT'))
logging.info(f"now position have:{get_pos(hmac_client)}")

tradeing = False
order_StartTime = None

while True:
    position_hold = []
    order_hold = []
    high_confi = False
    low_confi = False
    price_confi = False
    timestamp_TradeStart = int(time.time())
    Current_price = get_tickers_usdt(hmac_client, 'BTCUSDT')['price']
    if tradeing == True: #有订单或有仓位的状态
        position_hold = get_pos(hmac_client,'BTCUSDT') #如果有持仓 返回['BTCUDST']，如果没持仓，返回空列表
        order_hold = check_orders(hmac_client,'BTCUSDT') #如果有订单 返回['BTCUDST']，如果没订单，返回空列表
        while len(position_hold) == 0 and len(order_hold) != 0: #没有仓位但是有订单，因此撤销所有委托单子。
            close_open_orders(hmac_client,'BTCUDST')  #取消所有订单
            position_hold = get_pos(hmac_client,'BTCUSDT')
            order_hold = check_orders(hmac_client, 'BTCUSDT')
            time.sleep(1)
        # 意外情况:有仓位但是没止盈止损订单，立即平仓
        while len(position_hold) != 0 and len(order_hold) < 2:
            position_amt = get_pos_amt(hmac_client, 'BTCUDST')
            volume = get_tickers_usdt(hmac_client, 'BTCUSDT')
            if position_amt > 0:
                open_order_reduceOnly(hmac_client, 'BTCUSDT', 'SELL', position_amt)
            elif position_amt < 0:
                open_order_reduceOnly(hmac_client, 'BTCUSDT', 'BUY', position_amt)
            position_hold = get_pos(hmac_client, 'BTCUSDT')
            order_hold = check_orders(hmac_client, 'BTCUSDT')
            time.sleep(1)
        # 根据预测进行止盈止损修正，没写
        # 到5分钟了，没触发止盈止损，立即市价平仓，取消所有订单
        while ((timestamp_TradeStart - order_StartTime >= 300) and len(position_hold)>0):
            position_amt = get_pos_amt(hmac_client, 'BTCUDST')
            volume = get_tickers_usdt(hmac_client, 'BTCUSDT')
            if position_amt > 0:
                open_order_reduceOnly(hmac_client, 'BTCUSDT', 'SELL', position_amt)
            elif position_amt < 0:
                open_order_reduceOnly(hmac_client, 'BTCUSDT', 'BUY', position_amt)
            time.sleep(1)
            close_open_orders(hmac_client, 'BTCUDST')  # 取消所有订单
            time.sleep(1)
            position_hold = get_pos(hmac_client, 'BTCUSDT')
            order_hold = check_orders(hmac_client, 'BTCUSDT')
            print("模型预测的止盈止损在5分钟内未达到！！")

        #最终检查，是否可以进行新交易了
        if len(position_hold) == 0 and len(order_hold) == 0: #没仓位又没订单，则恢复状态为未处于交易状态
            order_StartTime = None
            tradeing = False


    PredictNow = pd.read_csv("PredictNow.csv")
    #获取模型预测信息
    high_5m_confidence = PredictNow['high_5m_confidence']
    low_5m_confidence = PredictNow['low_5m_confidence']
    price_5m_confidence = PredictNow['pirce_5m_confidence']
    high_5m = PredictNow['high_5m']
    low_5m = PredictNow['low_5m']
    price_5m = PredictNow['price_5m']
    datatime = PredictNow['datatime']

    if tradeing == False:
        timestamp_1 = int(time.time())*1000 #毫秒单位unix时间
        if (timestamp_1- datatime) >= 90*1000: #现在时间已经比预测时晚了90秒以上
            print("交易模块读取到的预测信息延迟过大！！延迟为：",timestamp_1 - datatime)
            continue
        confi_threshold = 0.9  #可以相信的信心阈值
        high_confi = False
        low_confi = False
        price_confi = False

        if high_5m_confidence >= confi_threshold:
            high_confi = True
        if low_5m_confidence >= confi_threshold:
            low_confi = True
        if price_5m_confidence >= confi_threshold:
            price_confi = True

        aver_price = (high_5m+low_5m)/2  #预测区间的均值

        if Current_price > aver_price: #如果现价大于预测区间均价，且最低价信心很高，则开空，止盈止损是现价到预测之间距离的80%，百倍杠杆时至少做0.1%以上的振幅
            if low_confi == True:
                if ((price_confi == True) and (price_5m < high_5m)) or price_confi == False:
                    tp = (Current_price - low_5m) / Current_price * 0.8
                    sl = tp
                    volume = get_balance_usdt(hmac_client)
                    if tp > 0.0015:
                        open_order(hmac_client, 'BTCUSDT', 'SELL', volume, tp, sl)
                        order_StartTime = int(time.time())
                        tradeing = True

        if Current_price < aver_price: #如果现价低于预测区间均价，且最高价信心很高，则开多，止盈止损是现价到预测之间距离的80%，百倍杠杆时至少做0.1%以上的振幅
            if high_confi == True:
                if ((price_confi == True) and (price_5m > low_5m)) or price_confi == False:
                    tp = (high_5m - Current_price) / Current_price * 0.8
                    sl = tp
                    volume = get_balance_usdt(hmac_client)
                    if tp > 0.0015:
                        open_order(hmac_client, 'BTCUSDT', 'BUY', volume, tp, sl)
                        order_StartTime = int(time.time())
                        tradeing = True

    timestamp_TradeStop = int(time.time())
    if (timestamp_TradeStop-timestamp_TradeStart) <= 60:
        time.sleep(60-(timestamp_TradeStop-timestamp_TradeStart))
    else:
        logging.error("交易循环内运行时间过长！！！！")