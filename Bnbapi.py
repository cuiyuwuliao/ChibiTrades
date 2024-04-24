from binance.spot import Spot
import re

#默认使用测试账号,自带余额
#如果要使用真实账号，在同路径下创建“keys.txt”文件，文件需要包含以下两行
#apiKey = "<your key>"(记得加引号)
#secretKey = "<your key>"(记得加引号)

#使用测试账号
test = True
#测试账号
keys = {
    "apiKey" : "qgXWbFgv2IjtW0E2tixQTAozATBWLK45kz2h7Gyc18l5jEPT1zsPokWxlVDfMOgr",
    "secreteKey": "ArCRb4CJgIlFf01L7a3N5brg5h7KmaGZNpUAnwu26i20nvfNBkJ0DMrk6J5Bxq4f"
}
client = Spot(api_key = keys["apiKey"], api_secret = keys["secreteKey"], base_url='https://testnet.binance.vision')

#使用真实账号
if not test:
    with open('keys.txt', 'r') as file:
        data = file.read()
    keys["apiKey"] = re.search(r'apiKey\s*=\s*"([^"]+)"', data).group(1)
    keys["secreteKey"] = re.search(r'secretKey\s*=\s*"([^"]+)"', data).group(1)
    client = Spot(api_key = keys["apiKey"], api_secret = keys["secreteKey"])

accountInfo = {}


def refreshAccountInfo():
    global accountInfo
    accountInfo = client.account()
    return accountInfo

def checkBalance(symbol):
    global accountInfo
    balanceList = accountInfo['balances']
    for crypto in balanceList:
        if crypto['asset'] == symbol:
            return [crypto['free'], crypto['locked']]
    return None
        

#获取1根btc的分钟k线
print(client.klines("BTCUSDT", "1m", limit = 1))
#获取账号所有币种余额
refreshAccountInfo()
print(checkBalance('USDT'))




#获取正在进行的交易单
print(client.my_trades('BTCUSDT'))

#下订单
#真实账号下订单之前，网页登陆币安，在“账户-api管理”界面添加当前的ip地址，然后勾选允许现货交易，否则无法交易
#参考文档：https://binance-connector.readthedocs.io/en/latest/binance.spot.trade.html?highlight=new_order
def placeOrder(params):
    response = client.new_order(**params)
    print(response)
    return response


# params = {
#     'symbol': 'ETHUSDT',
#     'side': 'BUY',
#     'type': 'MARKET',
#     'quantity': 0.01
#     # 'timeInForce': 'GTC',
#     # 'price': 70000
# }

params = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.002,
    'price': 64000
}

placeOrder(params)
refreshAccountInfo()
print(checkBalance('USDT'))
print(client.my_trades('BTCUSDT'))

