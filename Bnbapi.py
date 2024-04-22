from binance.spot import Spot
import re

#读取同路径下keys.txt文件里的key,文件需要包含以下两行
#apiKey = <your key>
#secretKey = <your key>
with open('keys.txt', 'r') as file:
    data = file.read()
apiKey = re.search(r'apiKey\s*=\s*"([^"]+)"', data).group(1)
secretKey = re.search(r'secretKey\s*=\s*"([^"]+)"', data).group(1)

# 登陆现货账号
client = Spot(api_key=apiKey, api_secret=secretKey)
#获取10G根btc的分钟k线
print(client.klines("BTCUSDT", "1m", limit = 10))


#下订单
#params字典参数文档：https://binance-docs.github.io/apidocs/spot/en/#new-order-trade
def placeOrder(params):
    response = client.new_order(**params)
    print(response)
    return response

params = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.002,
    'price': 9500
}

placeOrder(params)