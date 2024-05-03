from binance.um_futures import UMFutures
from binance.error import ClientError
import pandas as pd
# HMAC authentication with API key and secret
key = "fdada3ea1313b8c6f7f433e2f63c9fa4a7394daf07cf611d8069079bb152fab7"
secret = "b4676e625617b7b78592f12192967a90c90f08f394560345ea76b720706eedb2"

client = UMFutures(key=key, secret=secret)
interval = '1d' #1m 3m 15m  1h 4h 1d

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
data = klines(client=client,contractType='PERPETUAL',
              symbol='BTCUSDT',interval=interval,
              starttime=1714521600000,endtime=1714521600000+24*3600*1000-1,limit=1) #1m:1440 3m:480 15m:96 1h:24 4h:6 1d:1
data.to_csv(f'20240501_{interval}.csv')