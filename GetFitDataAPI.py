from binance.um_futures import UMFutures
from binance.error import ClientError
import pandas as pd
# HMAC authentication with API key and secret
key = ''
secret = ''

client = UMFutures(key=key, secret=secret)
interval = '1m' #1m 3m 15m  1h 4h 1d

def klines(client,contractType,symbol, interval, starttime, endtime, limit):
    # PERPETUAL 永续合约 CURRENT_QUARTER 当季交割合约 NEXT_QUARTER 次季交割合约

    try:
        resp = pd.DataFrame(client.continuous_klines(pair=symbol,contractType=contractType,interval=interval, stratTime=starttime, endTime=endtime, limit=limit))
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
# 用来获取不能从Binance直接下载，但是可以用api拉取的行情
data = klines(client,'PERPETUAL','BTCUSDT',interval,None,None,1440) #1m:1440 3m:480 15m:96 1h:24 4h:6 1d:1
data.to_csv(f'20240430_in_{interval}.csv')