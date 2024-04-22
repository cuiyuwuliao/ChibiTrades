from binance.spot import Spot
import re


#读取同路径下keys.txt文件里的key,文件需要包含以下两行
#apiKey = <your key>
#secretKey = <your key>
with open('keys.txt', 'r') as file:
    data = file.read()
apiKey = re.search(r'apiKey\s*=\s*"([^"]+)"', data).group(1)
secretKey = re.search(r'secretKey\s*=\s*"([^"]+)"', data).group(1)

# 登陆现货账号，默认连接到正式网络
client = Spot(api_key=apiKey, api_secret=secretKey)

# # 连接到测试网络（测试网络使用方式看文档）
# client = Spot(base_url='https://testnet.binance.vision')

#获取10G根btc的分钟k线
print(client.klines("BTCUSDT", "1m", limit = 1))


#下订单
#下订单之前，网页登陆币安，在“账户-api管理”界面添加当前的ip地址，然后勾选允许现货交易，否则无法交易
#参考文档：https://binance-connector.readthedocs.io/en/latest/binance.spot.trade.html?highlight=new_order
def placeOrder(params):
    response = client.new_order(**params)
    print(response)
    return response

# # 显示账户余额
# print(client.account())

params = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.002,
    'price': 9500
}

placeOrder(params)