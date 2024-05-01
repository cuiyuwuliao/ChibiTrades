#!/usr/bin/env python
import logging
from datetime import datetime
import pandas as pd
from binance.lib.utils import config_logging
from binance.um_futures import UMFutures
import time
import threading
import joblib
from binance.error import ClientError

rf_model_high_filedir = 'rfmodel_high_yh5_2024-04-29.pkl' #更改为模型文件 高价
rf_model_low_filedir = 'rfmodel_high_yl5_2024-04-29.pkl' #更改为模型文件 低价
rf_model_price_filedir = 'rfmodel_high_y5_2024-04-29.pkl' #更改为模型文件 收盘价

# 加载模型
rf_model_high = joblib.load(rf_model_high_filedir)
rf_model_low = joblib.load(rf_model_low_filedir)
rf_model_price = joblib.load(rf_model_price_filedir)

# HMAC authentication with API key and secret
key = ""
secret = ""
um_futures_client = UMFutures(key=key, secret=secret)



# 创建一个锁对象
file_lock1m = threading.Lock()
file_lock3m = threading.Lock()
file_lock15m = threading.Lock()
file_lock1h = threading.Lock()
file_lock4h = threading.Lock()
file_lock1d = threading.Lock()

#获得当前时间创建日志
today = datetime.now().strftime('%Y-%m-%d')
log_file = f"model_run_log_{today}.txt"
config_logging(logging, logging.DEBUG, log_file=log_file)

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

''' #订阅K线 后续再做
global_message = None
def message_handler(_, message):
    global global_message
    global_message = message
    print(message)

def ckline_subscribe(action=None, pair='btcusdt', interval='1m'):
    global myckline_client
    if action == 'start':
        myckline_client = UMFuturesWebsocketClient(on_message=message_handler)
        myckline_client.continuous_kline(
            pair=pair,
            id=1,
            contractType="perpetual",
            interval=interval,
        )
    if action == 'stop':
        logging.debug("closing ws connection")
        myckline_client.stop()


def get_umckline(um_futures_client, pair = 'BTCUSDT',contractType='PERPETUAL',interval='1m',startTime=0,endTime=0,limit=500):
    if (startTime != 0 and endTime != 0) and (startTime <= endTime):
        return um_futures_client.continuous_klines(pair=pair, contractType=contractType, interval=interval, startTime=startTime, endTime=endTime, limit=limit)
    else:
        return um_futures_client.continuous_klines(pair=pair, contractType=contractType, interval=interval, limit=limit)
'''



def klines(client, symbol, contractType, interval, startTime, endTime, limit):
    # PERPETUAL 永续合约 CURRENT_QUARTER 当季交割合约 NEXT_QUARTER 次季交割合约
    try:
        resp = pd.DataFrame(client.continuous_klines(pair=symbol,contractType=contractType,interval=interval, startTime=startTime, endTime=endTime, limit=limit))
        resp = resp.iloc[:,:]
        resp.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_volume', 'count', 'taker_buy_volume', 'taker_buy_quote_volume','ignore']
        resp = resp.set_index('open_time')
        resp = resp.astype(float)
        return resp
    except ClientError as error:
        print(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


#6个线程
thread_1min = None
thread_3min = None
thread_15min = None
thread_1hour = None
thread_4hour = None
thread_1day = None

def KlinedataUpdata(um_futures_client):
    global thread_1min, thread_3min, thread_15min, thread_1hour, thread_4hour, thread_1day
    def get_ckline_thread(interval, limit):
        while True:
            # 计算每个时间间隔的起始和结束时间戳
            current_timestamp = int(int(time.time()) * 1000)  # 当前时间戳 毫秒级
            oneminKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000
            threeminKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000 - 60 * 3 * 60 * 1000
            fifteenminKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000
            onehourKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000 - 16 * 60 * 60 * 1000
            fourhourKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000 - 16 * 60 * 60 * 1000 - 18 * 240 * 60 * 1000
            onedayKline_Start_timestamp = current_timestamp - 60 * 1 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000 - 16 * 60 * 60 * 1000 - 18 * 240 * 60 * 1000 - 32 * 1440 * 60 * 1000
            if interval == '1m':
                start_time = None
                end_time = None
            elif interval == '3m':
                start_time = threeminKline_Start_timestamp
                end_time = oneminKline_Start_timestamp - 1
            elif interval == '15m':
                start_time = fifteenminKline_Start_timestamp
                end_time = threeminKline_Start_timestamp - 1
            elif interval == '1h':
                start_time = onehourKline_Start_timestamp
                end_time = fifteenminKline_Start_timestamp - 1
            elif interval == '4h':
                start_time = fourhourKline_Start_timestamp
                end_time = onehourKline_Start_timestamp - 1
            elif interval == '1d':
                start_time = onedayKline_Start_timestamp
                end_time = fourhourKline_Start_timestamp - 1

            kline_data = klines(client=um_futures_client,
                                    symbol='BTCUSDT',
                                    contractType='PERPETUAL',
                                    interval=interval,
                                    startTime=start_time,
                                    endTime=end_time,
                                    limit=limit)
            # 处理kline_data
            time.sleep(interval_to_seconds(interval,kline_data))
    def interval_to_seconds(interval,data):
        if interval == '1m':
            file_lock1m.acquire()  #锁定文件
            data.to_csv('data1m.csv')
            file_lock1m.release() # 释放锁
            return 50
        elif interval == '3m':
            file_lock3m.acquire()  #锁定文件
            data.to_csv('data3m.csv')
            file_lock3m.release() # 释放锁
            return 180
        elif interval == '15m':
            file_lock15m.acquire()  #锁定文件
            data.to_csv('data15m.csv')
            file_lock15m.release() # 释放锁
            return 900
        elif interval == '1h':
            file_lock1h.acquire()  #锁定文件
            data.to_csv('data1h.csv')
            file_lock1h.release() # 释放锁
            return 3600
        elif interval == '4h':
            file_lock4h.acquire()  #锁定文件
            data.to_csv('data4h.csv')
            file_lock4h.release() # 释放锁
            return 14400
        elif interval == '1d':
            file_lock1d.acquire()  #锁定文件
            data.to_csv('data1d.csv')
            file_lock1d.release() # 释放锁
            return 86400
        else:
            logging.error("interval_to_seconds error！ interval dont exist")
     # 创建并启动线程
    thread_1min = threading.Thread(target=get_ckline_thread,
                                       args=('1m', 60))
    thread_3min = threading.Thread(target=get_ckline_thread,
                                       args=('3m', 60))
    thread_15min = threading.Thread(target=get_ckline_thread,
                                        args=('15m', 16))
    thread_1hour = threading.Thread(target=get_ckline_thread,
                                        args=('1h', 16))
    thread_4hour = threading.Thread(target=get_ckline_thread,
                                        args=('4h', 18))
    thread_1day = threading.Thread(target=get_ckline_thread,
                                       args=('1d', 32))
    thread_1min.start()
    thread_3min.start()
    thread_15min.start()
    thread_1hour.start()
    thread_4hour.start()
    thread_1day.start()

KlinedataUpdata(um_futures_client)
time.sleep(20)
PredictCSV = {
    'currentPrice': 0,
    'datatime': 0,
    'high_5m': 0,
    'low_5m': 0,
    'price_5m': 0,
    'high_5m_confidence': 0,
    'low_5m_confidence': 0,
    'price_5m_confidence': 0
}
PredictCSV = pd.DataFrame.from_dict(PredictCSV, orient='index').T
PredictCSV.to_csv(r'PredictNow.csv',index=False)


while True:
    timestamp_TradeStart = int(time.time())
    #读入k线数据
    current_price = get_tickers_usdt(um_futures_client, 'BTCUSDT')[0]['price']
    current_price = float(current_price)
    file_lock1m.acquire() #文件锁
    data1m = pd.read_csv('data1m.csv')
    file_lock1m.release() #释放锁

    file_lock3m.acquire()
    data3m = pd.read_csv('data3m.csv')
    file_lock3m.release()

    file_lock15m.acquire()
    data15m = pd.read_csv('data15m.csv')
    file_lock15m.release()

    file_lock1h.acquire()
    data1h = pd.read_csv('data1h.csv')
    file_lock1h.release()

    file_lock4h.acquire()
    data4h = pd.read_csv('data4h.csv')
    file_lock4h.release()

    file_lock1d.acquire()
    data1d = pd.read_csv('data1d.csv')
    file_lock1d.release()

    data1m['open'] = (data1m['open'] - current_price) / current_price
    data1m['high'] = (data1m['high'] - current_price) / current_price
    data1m['low'] = (data1m['low'] - current_price) / current_price
    data1m['close'] = (data1m['close'] - current_price) / current_price
    data3m['open'] = (data3m['open'] - current_price) / current_price
    data3m['high'] = (data3m['high'] - current_price) / current_price
    data3m['low'] = (data3m['low'] - current_price) / current_price
    data3m['close'] = (data3m['close'] - current_price) / current_price
    data15m['open'] = (data15m['open'] - current_price) / current_price
    data15m['high'] = (data15m['high'] - current_price) / current_price
    data15m['low'] = (data15m['low'] - current_price) / current_price
    data15m['close'] = (data15m['close'] - current_price) / current_price
    data1h['open'] = (data1h['open'] - current_price) / current_price
    data1h['high'] = (data1h['high'] - current_price) / current_price
    data1h['low'] = (data1h['low'] - current_price) / current_price
    data1h['close'] = (data1h['close'] - current_price) / current_price
    data4h['open'] = (data4h['open'] - current_price) / current_price
    data4h['high'] = (data4h['high'] - current_price) / current_price
    data4h['low'] = (data4h['low'] - current_price) / current_price
    data4h['close'] = (data4h['close'] - current_price) / current_price
    data1d['open'] = (data1d['open'] - current_price) / current_price
    data1d['high'] = (data1d['high'] - current_price) / current_price
    data1d['low'] = (data1d['low'] - current_price) / current_price
    data1d['close'] = (data1d['close'] - current_price) / current_price
    data1m = data1m.sort_values('open_time', ascending=False)
    data3m = data3m.sort_values('open_time', ascending=False)
    data15m = data15m.sort_values('open_time', ascending=False)
    data1h = data1h.sort_values('open_time', ascending=False)
    data4h = data4h.sort_values('open_time', ascending=False)
    data1d = data1d.sort_values('open_time', ascending=False)

    Xdata = {}
    datatime = float(data1m['open_time'].max())+60*1000  #最新的行情是上一分钟的事情，获取的现价是这分钟的现价，预测也是这分钟的，所以+1min
    # 循环处理每一分钟的数据
    for i in range(1, 61):
        # 将数据存入新的DataFrame中
        Xdata[f'open_1_{i}'] = data1m.loc[i-1]['open']
        Xdata[f'high_1_{i}'] = data1m.loc[i-1]['high']
        Xdata[f'low_1_{i}'] = data1m.loc[i-1]['low']
        Xdata[f'close_1_{i}'] = data1m.loc[i-1]['close']
        Xdata[f'volume_1_{i}'] = data1m.loc[i-1]['volume']
        Xdata[f'count_1_{i}'] = data1m.loc[i-1]['count']
        Xdata[f'taker_buy_volume_1_{i}'] = data1m.loc[i-1]['taker_buy_volume']
    for i in range(1, 61):
        # 将数据存入新的DataFrame中
        Xdata[f'open_3_{i}'] = data3m.loc[i-1]['open']
        Xdata[f'high_3_{i}'] = data3m.loc[i-1]['high']
        Xdata[f'low_3_{i}'] = data3m.loc[i-1]['low']
        Xdata[f'volume_3_{i}'] = data3m.loc[i-1]['volume']
        Xdata[f'count_3_{i}'] = data3m.loc[i-1]['count']
        Xdata[f'taker_buy_volume_3_{i}'] = data3m.loc[i-1]['taker_buy_volume']
    for i in range(1, 17):
        Xdata[f'open_15_{i}'] = data15m.loc[i-1]['open']
        Xdata[f'high_15_{i}'] = data15m.loc[i-1]['high']
        Xdata[f'low_15_{i}'] = data15m.loc[i-1]['low']
        Xdata[f'count_15_{i}'] = data15m.loc[i-1]['count']
        Xdata[f'volume_15_{i}'] = data15m.loc[i-1]['volume']
        Xdata[f'taker_buy_volume_15_{i}'] = data15m.loc[i-1]['taker_buy_volume']
    for i in range(1, 17):
        Xdata[f'open_60_{i}'] = data1h.loc[i-1]['open']
        Xdata[f'high_60_{i}'] = data1h.loc[i-1]['high']
        Xdata[f'low_60_{i}'] = data1h.loc[i-1]['low']
        Xdata[f'count_60_{i}'] = data1h.loc[i-1]['count']
        Xdata[f'volume_60_{i}'] = data1h.loc[i-1]['volume']
        Xdata[f'taker_buy_volume_60_{i}'] = data1h.loc[i-1]['taker_buy_volume']
    for i in range(1, 19):
        Xdata[f'open_240_{i}'] = data4h.loc[i-1]['open']
        Xdata[f'high_240_{i}'] = data4h.loc[i-1]['high']
        Xdata[f'low_240_{i}'] = data4h.loc[i-1]['low']
        Xdata[f'volume_240_{i}'] = data4h.loc[i-1]['volume']
    for i in range(1, 33):
        Xdata[f'open_1440_{i}'] = data1d.loc[i-1]['open']
        Xdata[f'high_1440_{i}'] = data1d.loc[i-1]['high']
        Xdata[f'low_1440_{i}'] = data1d.loc[i-1]['low']
    Xdata = pd.DataFrame.from_dict(Xdata, orient='index').T

    PredictNow = {
        'currentPrice': current_price,
        'datatime' : datatime,
        'high_5m':0,
        'low_5m' : 0,
        'price_5m' : 0,
        'high_5m_confidence' : 0,
        'low_5m_confidence' : 0,
        'price_5m_confidence' : 0
    }
    # 使用加载的模型进行预测等操作
    Xlistall = ['current_price', 'open_1_1', 'high_1_1', 'low_1_1', 'close_1_1', 'volume_1_1', 'count_1_1', 'taker_buy_volume_1_1', 'open_1_2', 'high_1_2', 'low_1_2', 'close_1_2', 'volume_1_2', 'count_1_2', 'taker_buy_volume_1_2', 'open_1_3', 'high_1_3', 'low_1_3', 'close_1_3', 'volume_1_3', 'count_1_3', 'taker_buy_volume_1_3', 'open_1_4', 'high_1_4', 'low_1_4', 'close_1_4', 'volume_1_4', 'count_1_4', 'taker_buy_volume_1_4', 'open_1_5', 'high_1_5', 'low_1_5', 'close_1_5', 'volume_1_5', 'count_1_5', 'taker_buy_volume_1_5', 'open_1_6', 'high_1_6', 'low_1_6', 'close_1_6', 'volume_1_6', 'count_1_6', 'taker_buy_volume_1_6', 'open_1_7', 'high_1_7', 'low_1_7', 'close_1_7', 'volume_1_7', 'count_1_7', 'taker_buy_volume_1_7', 'open_1_8', 'high_1_8', 'low_1_8', 'close_1_8', 'volume_1_8', 'count_1_8', 'taker_buy_volume_1_8', 'open_1_9', 'high_1_9', 'low_1_9', 'close_1_9', 'volume_1_9', 'count_1_9', 'taker_buy_volume_1_9', 'open_1_10', 'high_1_10', 'low_1_10', 'close_1_10', 'volume_1_10', 'count_1_10', 'taker_buy_volume_1_10', 'open_1_11', 'high_1_11', 'low_1_11', 'close_1_11', 'volume_1_11', 'count_1_11', 'taker_buy_volume_1_11', 'open_1_12', 'high_1_12', 'low_1_12', 'close_1_12', 'volume_1_12', 'count_1_12', 'taker_buy_volume_1_12', 'open_1_13', 'high_1_13', 'low_1_13', 'close_1_13', 'volume_1_13', 'count_1_13', 'taker_buy_volume_1_13', 'open_1_14', 'high_1_14', 'low_1_14', 'close_1_14', 'volume_1_14', 'count_1_14', 'taker_buy_volume_1_14', 'open_1_15', 'high_1_15', 'low_1_15', 'close_1_15', 'volume_1_15', 'count_1_15', 'taker_buy_volume_1_15', 'open_1_16', 'high_1_16', 'low_1_16', 'close_1_16', 'volume_1_16', 'count_1_16', 'taker_buy_volume_1_16', 'open_1_17', 'high_1_17', 'low_1_17', 'close_1_17', 'volume_1_17', 'count_1_17', 'taker_buy_volume_1_17', 'open_1_18', 'high_1_18', 'low_1_18', 'close_1_18', 'volume_1_18', 'count_1_18', 'taker_buy_volume_1_18', 'open_1_19', 'high_1_19', 'low_1_19', 'close_1_19', 'volume_1_19', 'count_1_19', 'taker_buy_volume_1_19', 'open_1_20', 'high_1_20', 'low_1_20', 'close_1_20', 'volume_1_20', 'count_1_20', 'taker_buy_volume_1_20', 'open_1_21', 'high_1_21', 'low_1_21', 'close_1_21', 'volume_1_21', 'count_1_21', 'taker_buy_volume_1_21', 'open_1_22', 'high_1_22', 'low_1_22', 'close_1_22', 'volume_1_22', 'count_1_22', 'taker_buy_volume_1_22', 'open_1_23', 'high_1_23', 'low_1_23', 'close_1_23', 'volume_1_23', 'count_1_23', 'taker_buy_volume_1_23', 'open_1_24', 'high_1_24', 'low_1_24', 'close_1_24', 'volume_1_24', 'count_1_24', 'taker_buy_volume_1_24', 'open_1_25', 'high_1_25', 'low_1_25', 'close_1_25', 'volume_1_25', 'count_1_25', 'taker_buy_volume_1_25', 'open_1_26', 'high_1_26', 'low_1_26', 'close_1_26', 'volume_1_26', 'count_1_26', 'taker_buy_volume_1_26', 'open_1_27', 'high_1_27', 'low_1_27', 'close_1_27', 'volume_1_27', 'count_1_27', 'taker_buy_volume_1_27', 'open_1_28', 'high_1_28', 'low_1_28', 'close_1_28', 'volume_1_28', 'count_1_28', 'taker_buy_volume_1_28', 'open_1_29', 'high_1_29', 'low_1_29', 'close_1_29', 'volume_1_29', 'count_1_29', 'taker_buy_volume_1_29', 'open_1_30', 'high_1_30', 'low_1_30', 'close_1_30', 'volume_1_30', 'count_1_30', 'taker_buy_volume_1_30', 'open_1_31', 'high_1_31', 'low_1_31', 'close_1_31', 'volume_1_31', 'count_1_31', 'taker_buy_volume_1_31', 'open_1_32', 'high_1_32', 'low_1_32', 'close_1_32', 'volume_1_32', 'count_1_32', 'taker_buy_volume_1_32', 'open_1_33', 'high_1_33', 'low_1_33', 'close_1_33', 'volume_1_33', 'count_1_33', 'taker_buy_volume_1_33', 'open_1_34', 'high_1_34', 'low_1_34', 'close_1_34', 'volume_1_34', 'count_1_34', 'taker_buy_volume_1_34', 'open_1_35', 'high_1_35', 'low_1_35', 'close_1_35', 'volume_1_35', 'count_1_35', 'taker_buy_volume_1_35', 'open_1_36', 'high_1_36', 'low_1_36', 'close_1_36', 'volume_1_36', 'count_1_36', 'taker_buy_volume_1_36', 'open_1_37', 'high_1_37', 'low_1_37', 'close_1_37', 'volume_1_37', 'count_1_37', 'taker_buy_volume_1_37', 'open_1_38', 'high_1_38', 'low_1_38', 'close_1_38', 'volume_1_38', 'count_1_38', 'taker_buy_volume_1_38', 'open_1_39', 'high_1_39', 'low_1_39', 'close_1_39', 'volume_1_39', 'count_1_39', 'taker_buy_volume_1_39', 'open_1_40', 'high_1_40', 'low_1_40', 'close_1_40', 'volume_1_40', 'count_1_40', 'taker_buy_volume_1_40', 'open_1_41', 'high_1_41', 'low_1_41', 'close_1_41', 'volume_1_41', 'count_1_41', 'taker_buy_volume_1_41', 'open_1_42', 'high_1_42', 'low_1_42', 'close_1_42', 'volume_1_42', 'count_1_42', 'taker_buy_volume_1_42', 'open_1_43', 'high_1_43', 'low_1_43', 'close_1_43', 'volume_1_43', 'count_1_43', 'taker_buy_volume_1_43', 'open_1_44', 'high_1_44', 'low_1_44', 'close_1_44', 'volume_1_44', 'count_1_44', 'taker_buy_volume_1_44', 'open_1_45', 'high_1_45', 'low_1_45', 'close_1_45', 'volume_1_45', 'count_1_45', 'taker_buy_volume_1_45', 'open_1_46', 'high_1_46', 'low_1_46', 'close_1_46', 'volume_1_46', 'count_1_46', 'taker_buy_volume_1_46', 'open_1_47', 'high_1_47', 'low_1_47', 'close_1_47', 'volume_1_47', 'count_1_47', 'taker_buy_volume_1_47', 'open_1_48', 'high_1_48', 'low_1_48', 'close_1_48', 'volume_1_48', 'count_1_48', 'taker_buy_volume_1_48', 'open_1_49', 'high_1_49', 'low_1_49', 'close_1_49', 'volume_1_49', 'count_1_49', 'taker_buy_volume_1_49', 'open_1_50', 'high_1_50', 'low_1_50', 'close_1_50', 'volume_1_50', 'count_1_50', 'taker_buy_volume_1_50', 'open_1_51', 'high_1_51', 'low_1_51', 'close_1_51', 'volume_1_51', 'count_1_51', 'taker_buy_volume_1_51', 'open_1_52', 'high_1_52', 'low_1_52', 'close_1_52', 'volume_1_52', 'count_1_52', 'taker_buy_volume_1_52', 'open_1_53', 'high_1_53', 'low_1_53', 'close_1_53', 'volume_1_53', 'count_1_53', 'taker_buy_volume_1_53', 'open_1_54', 'high_1_54', 'low_1_54', 'close_1_54', 'volume_1_54', 'count_1_54', 'taker_buy_volume_1_54', 'open_1_55', 'high_1_55', 'low_1_55', 'close_1_55', 'volume_1_55', 'count_1_55', 'taker_buy_volume_1_55', 'open_1_56', 'high_1_56', 'low_1_56', 'close_1_56', 'volume_1_56', 'count_1_56', 'taker_buy_volume_1_56', 'open_1_57', 'high_1_57', 'low_1_57', 'close_1_57', 'volume_1_57', 'count_1_57', 'taker_buy_volume_1_57', 'open_1_58', 'high_1_58', 'low_1_58', 'close_1_58', 'volume_1_58', 'count_1_58', 'taker_buy_volume_1_58', 'open_1_59', 'high_1_59', 'low_1_59', 'close_1_59', 'volume_1_59', 'count_1_59', 'taker_buy_volume_1_59', 'open_1_60', 'high_1_60', 'low_1_60', 'close_1_60', 'volume_1_60', 'count_1_60', 'taker_buy_volume_1_60', 'open_3_1', 'high_3_1', 'low_3_1', 'volume_3_1', 'count_3_1', 'taker_buy_volume_3_1', 'open_3_2', 'high_3_2', 'low_3_2', 'volume_3_2', 'count_3_2', 'taker_buy_volume_3_2', 'open_3_3', 'high_3_3', 'low_3_3', 'volume_3_3', 'count_3_3', 'taker_buy_volume_3_3', 'open_3_4', 'high_3_4', 'low_3_4', 'volume_3_4', 'count_3_4', 'taker_buy_volume_3_4', 'open_3_5', 'high_3_5', 'low_3_5', 'volume_3_5', 'count_3_5', 'taker_buy_volume_3_5', 'open_3_6', 'high_3_6', 'low_3_6', 'volume_3_6', 'count_3_6', 'taker_buy_volume_3_6', 'open_3_7', 'high_3_7', 'low_3_7', 'volume_3_7', 'count_3_7', 'taker_buy_volume_3_7', 'open_3_8', 'high_3_8', 'low_3_8', 'volume_3_8', 'count_3_8', 'taker_buy_volume_3_8', 'open_3_9', 'high_3_9', 'low_3_9', 'volume_3_9', 'count_3_9', 'taker_buy_volume_3_9', 'open_3_10', 'high_3_10', 'low_3_10', 'volume_3_10', 'count_3_10', 'taker_buy_volume_3_10', 'open_3_11', 'high_3_11', 'low_3_11', 'volume_3_11', 'count_3_11', 'taker_buy_volume_3_11', 'open_3_12', 'high_3_12', 'low_3_12', 'volume_3_12', 'count_3_12', 'taker_buy_volume_3_12', 'open_3_13', 'high_3_13', 'low_3_13', 'volume_3_13', 'count_3_13', 'taker_buy_volume_3_13', 'open_3_14', 'high_3_14', 'low_3_14', 'volume_3_14', 'count_3_14', 'taker_buy_volume_3_14', 'open_3_15', 'high_3_15', 'low_3_15', 'volume_3_15', 'count_3_15', 'taker_buy_volume_3_15', 'open_3_16', 'high_3_16', 'low_3_16', 'volume_3_16', 'count_3_16', 'taker_buy_volume_3_16', 'open_3_17', 'high_3_17', 'low_3_17', 'volume_3_17', 'count_3_17', 'taker_buy_volume_3_17', 'open_3_18', 'high_3_18', 'low_3_18', 'volume_3_18', 'count_3_18', 'taker_buy_volume_3_18', 'open_3_19', 'high_3_19', 'low_3_19', 'volume_3_19', 'count_3_19', 'taker_buy_volume_3_19', 'open_3_20', 'high_3_20', 'low_3_20', 'volume_3_20', 'count_3_20', 'taker_buy_volume_3_20', 'open_3_21', 'high_3_21', 'low_3_21', 'volume_3_21', 'count_3_21', 'taker_buy_volume_3_21', 'open_3_22', 'high_3_22', 'low_3_22', 'volume_3_22', 'count_3_22', 'taker_buy_volume_3_22', 'open_3_23', 'high_3_23', 'low_3_23', 'volume_3_23', 'count_3_23', 'taker_buy_volume_3_23', 'open_3_24', 'high_3_24', 'low_3_24', 'volume_3_24', 'count_3_24', 'taker_buy_volume_3_24', 'open_3_25', 'high_3_25', 'low_3_25', 'volume_3_25', 'count_3_25', 'taker_buy_volume_3_25', 'open_3_26', 'high_3_26', 'low_3_26', 'volume_3_26', 'count_3_26', 'taker_buy_volume_3_26', 'open_3_27', 'high_3_27', 'low_3_27', 'volume_3_27', 'count_3_27', 'taker_buy_volume_3_27', 'open_3_28', 'high_3_28', 'low_3_28', 'volume_3_28', 'count_3_28', 'taker_buy_volume_3_28', 'open_3_29', 'high_3_29', 'low_3_29', 'volume_3_29', 'count_3_29', 'taker_buy_volume_3_29', 'open_3_30', 'high_3_30', 'low_3_30', 'volume_3_30', 'count_3_30', 'taker_buy_volume_3_30', 'open_3_31', 'high_3_31', 'low_3_31', 'volume_3_31', 'count_3_31', 'taker_buy_volume_3_31', 'open_3_32', 'high_3_32', 'low_3_32', 'volume_3_32', 'count_3_32', 'taker_buy_volume_3_32', 'open_3_33', 'high_3_33', 'low_3_33', 'volume_3_33', 'count_3_33', 'taker_buy_volume_3_33', 'open_3_34', 'high_3_34', 'low_3_34', 'volume_3_34', 'count_3_34', 'taker_buy_volume_3_34', 'open_3_35', 'high_3_35', 'low_3_35', 'volume_3_35', 'count_3_35', 'taker_buy_volume_3_35', 'open_3_36', 'high_3_36', 'low_3_36', 'volume_3_36', 'count_3_36', 'taker_buy_volume_3_36', 'open_3_37', 'high_3_37', 'low_3_37', 'volume_3_37', 'count_3_37', 'taker_buy_volume_3_37', 'open_3_38', 'high_3_38', 'low_3_38', 'volume_3_38', 'count_3_38', 'taker_buy_volume_3_38', 'open_3_39', 'high_3_39', 'low_3_39', 'volume_3_39', 'count_3_39', 'taker_buy_volume_3_39', 'open_3_40', 'high_3_40', 'low_3_40', 'volume_3_40', 'count_3_40', 'taker_buy_volume_3_40', 'open_3_41', 'high_3_41', 'low_3_41', 'volume_3_41', 'count_3_41', 'taker_buy_volume_3_41', 'open_3_42', 'high_3_42', 'low_3_42', 'volume_3_42', 'count_3_42', 'taker_buy_volume_3_42', 'open_3_43', 'high_3_43', 'low_3_43', 'volume_3_43', 'count_3_43', 'taker_buy_volume_3_43', 'open_3_44', 'high_3_44', 'low_3_44', 'volume_3_44', 'count_3_44', 'taker_buy_volume_3_44', 'open_3_45', 'high_3_45', 'low_3_45', 'volume_3_45', 'count_3_45', 'taker_buy_volume_3_45', 'open_3_46', 'high_3_46', 'low_3_46', 'volume_3_46', 'count_3_46', 'taker_buy_volume_3_46', 'open_3_47', 'high_3_47', 'low_3_47', 'volume_3_47', 'count_3_47', 'taker_buy_volume_3_47', 'open_3_48', 'high_3_48', 'low_3_48', 'volume_3_48', 'count_3_48', 'taker_buy_volume_3_48', 'open_3_49', 'high_3_49', 'low_3_49', 'volume_3_49', 'count_3_49', 'taker_buy_volume_3_49', 'open_3_50', 'high_3_50', 'low_3_50', 'volume_3_50', 'count_3_50', 'taker_buy_volume_3_50', 'open_3_51', 'high_3_51', 'low_3_51', 'volume_3_51', 'count_3_51', 'taker_buy_volume_3_51', 'open_3_52', 'high_3_52', 'low_3_52', 'volume_3_52', 'count_3_52', 'taker_buy_volume_3_52', 'open_3_53', 'high_3_53', 'low_3_53', 'volume_3_53', 'count_3_53', 'taker_buy_volume_3_53', 'open_3_54', 'high_3_54', 'low_3_54', 'volume_3_54', 'count_3_54', 'taker_buy_volume_3_54', 'open_3_55', 'high_3_55', 'low_3_55', 'volume_3_55', 'count_3_55', 'taker_buy_volume_3_55', 'open_3_56', 'high_3_56', 'low_3_56', 'volume_3_56', 'count_3_56', 'taker_buy_volume_3_56', 'open_3_57', 'high_3_57', 'low_3_57', 'volume_3_57', 'count_3_57', 'taker_buy_volume_3_57', 'open_3_58', 'high_3_58', 'low_3_58', 'volume_3_58', 'count_3_58', 'taker_buy_volume_3_58', 'open_3_59', 'high_3_59', 'low_3_59', 'volume_3_59', 'count_3_59', 'taker_buy_volume_3_59', 'open_3_60', 'high_3_60', 'low_3_60', 'volume_3_60', 'count_3_60', 'taker_buy_volume_3_60', 'open_15_1', 'high_15_1', 'low_15_1', 'count_15_1', 'volume_15_1', 'taker_buy_volume_15_1', 'open_15_2', 'high_15_2', 'low_15_2', 'count_15_2', 'volume_15_2', 'taker_buy_volume_15_2', 'open_15_3', 'high_15_3', 'low_15_3', 'count_15_3', 'volume_15_3', 'taker_buy_volume_15_3', 'open_15_4', 'high_15_4', 'low_15_4', 'count_15_4', 'volume_15_4', 'taker_buy_volume_15_4', 'open_15_5', 'high_15_5', 'low_15_5', 'count_15_5', 'volume_15_5', 'taker_buy_volume_15_5', 'open_15_6', 'high_15_6', 'low_15_6', 'count_15_6', 'volume_15_6', 'taker_buy_volume_15_6', 'open_15_7', 'high_15_7', 'low_15_7', 'count_15_7', 'volume_15_7', 'taker_buy_volume_15_7', 'open_15_8', 'high_15_8', 'low_15_8', 'count_15_8', 'volume_15_8', 'taker_buy_volume_15_8', 'open_15_9', 'high_15_9', 'low_15_9', 'count_15_9', 'volume_15_9', 'taker_buy_volume_15_9', 'open_15_10', 'high_15_10', 'low_15_10', 'count_15_10', 'volume_15_10', 'taker_buy_volume_15_10', 'open_15_11', 'high_15_11', 'low_15_11', 'count_15_11', 'volume_15_11', 'taker_buy_volume_15_11', 'open_15_12', 'high_15_12', 'low_15_12', 'count_15_12', 'volume_15_12', 'taker_buy_volume_15_12', 'open_15_13', 'high_15_13', 'low_15_13', 'count_15_13', 'volume_15_13', 'taker_buy_volume_15_13', 'open_15_14', 'high_15_14', 'low_15_14', 'count_15_14', 'volume_15_14', 'taker_buy_volume_15_14', 'open_15_15', 'high_15_15', 'low_15_15', 'count_15_15', 'volume_15_15', 'taker_buy_volume_15_15', 'open_15_16', 'high_15_16', 'low_15_16', 'count_15_16', 'volume_15_16', 'taker_buy_volume_15_16', 'open_60_1', 'high_60_1', 'low_60_1', 'count_60_1', 'volume_60_1', 'taker_buy_volume_60_1', 'open_60_2', 'high_60_2', 'low_60_2', 'count_60_2', 'volume_60_2', 'taker_buy_volume_60_2', 'open_60_3', 'high_60_3', 'low_60_3', 'count_60_3', 'volume_60_3', 'taker_buy_volume_60_3', 'open_60_4', 'high_60_4', 'low_60_4', 'count_60_4', 'volume_60_4', 'taker_buy_volume_60_4', 'open_60_5', 'high_60_5', 'low_60_5', 'count_60_5', 'volume_60_5', 'taker_buy_volume_60_5', 'open_60_6', 'high_60_6', 'low_60_6', 'count_60_6', 'volume_60_6', 'taker_buy_volume_60_6', 'open_60_7', 'high_60_7', 'low_60_7', 'count_60_7', 'volume_60_7', 'taker_buy_volume_60_7', 'open_60_8', 'high_60_8', 'low_60_8', 'count_60_8', 'volume_60_8', 'taker_buy_volume_60_8', 'open_60_9', 'high_60_9', 'low_60_9', 'count_60_9', 'volume_60_9', 'taker_buy_volume_60_9', 'open_60_10', 'high_60_10', 'low_60_10', 'count_60_10', 'volume_60_10', 'taker_buy_volume_60_10', 'open_60_11', 'high_60_11', 'low_60_11', 'count_60_11', 'volume_60_11', 'taker_buy_volume_60_11', 'open_60_12', 'high_60_12', 'low_60_12', 'count_60_12', 'volume_60_12', 'taker_buy_volume_60_12', 'open_60_13', 'high_60_13', 'low_60_13', 'count_60_13', 'volume_60_13', 'taker_buy_volume_60_13', 'open_60_14', 'high_60_14', 'low_60_14', 'count_60_14', 'volume_60_14', 'taker_buy_volume_60_14', 'open_60_15', 'high_60_15', 'low_60_15', 'count_60_15', 'volume_60_15', 'taker_buy_volume_60_15', 'open_60_16', 'high_60_16', 'low_60_16', 'count_60_16', 'volume_60_16', 'taker_buy_volume_60_16', 'open_240_1', 'high_240_1', 'low_240_1', 'volume_240_1', 'open_240_2', 'high_240_2', 'low_240_2', 'volume_240_2', 'open_240_3', 'high_240_3', 'low_240_3', 'volume_240_3', 'open_240_4', 'high_240_4', 'low_240_4', 'volume_240_4', 'open_240_5', 'high_240_5', 'low_240_5', 'volume_240_5', 'open_240_6', 'high_240_6', 'low_240_6', 'volume_240_6', 'open_240_7', 'high_240_7', 'low_240_7', 'volume_240_7', 'open_240_8', 'high_240_8', 'low_240_8', 'volume_240_8', 'open_240_9', 'high_240_9', 'low_240_9', 'volume_240_9', 'open_240_10', 'high_240_10', 'low_240_10', 'volume_240_10', 'open_240_11', 'high_240_11', 'low_240_11', 'volume_240_11', 'open_240_12', 'high_240_12', 'low_240_12', 'volume_240_12', 'open_240_13', 'high_240_13', 'low_240_13', 'volume_240_13', 'open_240_14', 'high_240_14', 'low_240_14', 'volume_240_14', 'open_240_15', 'high_240_15', 'low_240_15', 'volume_240_15', 'open_240_16', 'high_240_16', 'low_240_16', 'volume_240_16', 'open_240_17', 'high_240_17', 'low_240_17', 'volume_240_17', 'open_240_18', 'high_240_18', 'low_240_18', 'volume_240_18', 'open_1440_1', 'high_1440_1', 'low_1440_1', 'open_1440_2', 'high_1440_2', 'low_1440_2', 'open_1440_3', 'high_1440_3', 'low_1440_3', 'open_1440_4', 'high_1440_4', 'low_1440_4', 'open_1440_5', 'high_1440_5', 'low_1440_5', 'open_1440_6', 'high_1440_6', 'low_1440_6', 'open_1440_7', 'high_1440_7', 'low_1440_7', 'open_1440_8', 'high_1440_8', 'low_1440_8', 'open_1440_9', 'high_1440_9', 'low_1440_9', 'open_1440_10', 'high_1440_10', 'low_1440_10', 'open_1440_11', 'high_1440_11', 'low_1440_11', 'open_1440_12', 'high_1440_12', 'low_1440_12', 'open_1440_13', 'high_1440_13', 'low_1440_13', 'open_1440_14', 'high_1440_14', 'low_1440_14', 'open_1440_15', 'high_1440_15', 'low_1440_15', 'open_1440_16', 'high_1440_16', 'low_1440_16', 'open_1440_17', 'high_1440_17', 'low_1440_17', 'open_1440_18', 'high_1440_18', 'low_1440_18', 'open_1440_19', 'high_1440_19', 'low_1440_19', 'open_1440_20', 'high_1440_20', 'low_1440_20', 'open_1440_21', 'high_1440_21', 'low_1440_21', 'open_1440_22', 'high_1440_22', 'low_1440_22', 'open_1440_23', 'high_1440_23', 'low_1440_23', 'open_1440_24', 'high_1440_24', 'low_1440_24', 'open_1440_25', 'high_1440_25', 'low_1440_25', 'open_1440_26', 'high_1440_26', 'low_1440_26', 'open_1440_27', 'high_1440_27', 'low_1440_27', 'open_1440_28', 'high_1440_28', 'low_1440_28', 'open_1440_29', 'high_1440_29', 'low_1440_29', 'open_1440_30', 'high_1440_30', 'low_1440_30', 'open_1440_31', 'high_1440_31', 'low_1440_31', 'open_1440_32', 'high_1440_32', 'low_1440_32']
    Ylistall = ['open_y1_1', 'high_y1_1', 'low_y1_1', 'close_y1_1', 'open_y1_2', 'high_y1_2', 'low_y1_2', 'close_y1_2', 'open_y1_3', 'high_y1_3', 'low_y1_3', 'close_y1_3', 'open_y1_4', 'high_y1_4', 'low_y1_4', 'close_y1_4', 'open_y1_5', 'high_y1_5', 'low_y1_5', 'close_y1_5', 'high_y5', 'low_y5']
    PredictNow['high_5m'] = (rf_model_high.predict(Xdata[Xlistall[1:800]])[0]+1)*current_price
    PredictNow['low_5m'] = (rf_model_low.predict(Xdata[Xlistall[1:800]])[0]+1)*current_price
    PredictNow['price_5m'] = (rf_model_price.predict(Xdata[Xlistall[1:800]])[0]+1)*current_price
    import numpy as np
    # 获取所有树的预测值
    model_high_tree_predictions = []
    for tree in rf_model_high.estimators_:
        tree_prediction = tree.predict(Xdata[Xlistall[1:800]])[0]
        model_high_tree_predictions.append(tree_prediction)
    # 计算所有树的预测值的标准差
    model_high_std_dev = np.std(model_high_tree_predictions)
    PredictNow['high_5m_confidence'] = 1-(model_high_std_dev*10000000/PredictNow['high_5m'])
    model_low_tree_predictions = []
    for tree in rf_model_low.estimators_:
        tree_prediction = tree.predict(Xdata[Xlistall[1:800]])[0]
        model_low_tree_predictions.append(tree_prediction)
    # 计算所有树的预测值的标准差
    model_low_std_dev = np.std(model_low_tree_predictions)
    PredictNow['low_5m_confidence'] = 1-(model_low_std_dev*10000000/PredictNow['low_5m'])
    model_price_tree_predictions = []
    for tree in rf_model_price.estimators_:
        tree_prediction = tree.predict(Xdata[Xlistall[1:800]])[0]
        model_price_tree_predictions.append(tree_prediction)
    # 计算所有树的预测值的标准差
    model_price_std_dev = np.std(model_price_tree_predictions)
    PredictNow['price_5m_confidence'] = 1-(model_price_std_dev*10000000/PredictNow['price_5m'])
    PredictNow = pd.DataFrame.from_dict(PredictNow, orient='index').T
    # 在这里进行文件写入操作
    PredictNow.to_csv("PredictNow.csv",mode='a', header=False, index=False)

    timestamp_TradeStop = int(time.time())
    if (timestamp_TradeStop - timestamp_TradeStart) <= 60:
        print('当前一次循环耗时：',timestamp_TradeStop - timestamp_TradeStart)
        time.sleep(60 - (timestamp_TradeStop - timestamp_TradeStart))
    else:
        logging.error("预测模型循环内运行时间过长！！！！")

