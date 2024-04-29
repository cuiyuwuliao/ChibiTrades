from binance.spot import Spot
from binance.cm_futures import CMFutures #币本位
from binance.um_futures import UMFutures #U本位，默认用U本位
import re
import sys

#测试账号和url
testnet_future = 'https://testnet.binancefuture.com'
testnet_spot = 'https://testnet.binance.vision'
mainnet = 'https://api.binance.com/api'
keys_spot = {
    "apiKey" : "qgXWbFgv2IjtW0E2tixQTAozATBWLK45kz2h7Gyc18l5jEPT1zsPokWxlVDfMOgr",
    "secretKey": "ArCRb4CJgIlFf01L7a3N5brg5h7KmaGZNpUAnwu26i20nvfNBkJ0DMrk6J5Bxq4f"
}
keys_future = {
    "apiKey" : "fdada3ea1313b8c6f7f433e2f63c9fa4a7394daf07cf611d8069079bb152fab7",
    "secretKey": "b4676e625617b7b78592f12192967a90c90f08f394560345ea76b720706eedb2"
}

#最长等待response时长
recvWindow = 10000 #10秒

#获取同路径“keys.txt”文件中的api keys，格式如下
#apiKey = "your key" (记得加引号)
#secretKey = "your key" (记得加引号)
def getKeys():
    with open('keys.txt', 'r') as file:
        data = file.read()
    keys = {}
    keys["apiKey"] = re.search(r'apiKey\s*=\s*"([^"]+)"', data).group(1)
    keys["secretKey"] = re.search(r'secretKey\s*=\s*"([^"]+)"', data).group(1)
    return keys

class ChibiClient:
    def __init__(self, **kwargs):
        self.mode = kwargs.get('accountType')
        self.isTest = kwargs.get('test')
        self.keys = kwargs.get('keys')
        self.client = None

        if self.mode == 'future':
            self.url = testnet_future if self.isTest else mainnet
            self.client = UMFutures(key=self.keys["apiKey"], secret=self.keys["secretKey"], base_url=self.url)
        elif self.mode == 'spot':
            self.url = testnet_spot if self.isTest else mainnet
            self.client = Spot(api_key=self.keys["apiKey"], api_secret=self.keys["secretKey"], base_url=self.url)
        self.accountInfo = {}
        try:
            self.accountInfo = self.getAccountInfo()
        except Exception as e:
            print(e)
            print("登陆失败,检查keys和url是否正确, 检查有没有挂vpn")
            sys.exit()

    def getAccountInfo(self):
        self.accountInfo = self.client.account(recvWindow = recvWindow)
        return self.accountInfo

    #symbol = None时返回所有币的余额
    def getkBalance(self, symbol):
        if(self.mode) == 'spot':
            balanceList = self.getAccountInfo()['balances']
            if symbol == None: #如果不指定币，就返回所有币
                return balanceList 
            for crypto in balanceList:
                if crypto['asset'] == symbol:
                    return [crypto['free'], crypto['locked']] #挂单之后余额会被归类于locked，不能再交易
        if(self.mode) == 'future':
            balanceList = self.client.balance(recvWindow = recvWindow)
            if symbol == None: #如果不指定币，就返回所有币
                return balanceList 
            for crypto in balanceList:
                if crypto['asset'] == symbol:
                    return crypto['balance']
        return None
    
    #返回binance现货市场价格的k线
    def getKlines(self, symbol, timeUnit, limit):
        return self.client.klines(symbol, timeUnit, limit = limit, recvWindow = recvWindow)
    
    #返回平均现货市场价格的k线
    def getIndexKlines(self, symbol, timeUnit, limit):
        if(self.mode) == 'spot': #现货账户看不到，所以返回binance现货市价线
            return self.client.klines(symbol, timeUnit, limit = limit, recvWindow = recvWindow)
        return self.client.index_price_klines(symbol, timeUnit, limit = limit)
    
    #返回合约标记价格的k线
    def getMarkKlines(self, symbol, timeUnit, limit):
        if(self.mode) == 'spot': #现货账户看不到，所以返回binance现货市价线
            return self.client.klines(symbol, timeUnit, limit = limit, recvWindow = recvWindow)
        return self.client.mark_price_klines(symbol, timeUnit, limit = limit)
    
    def getTrades(self, symbol):
        if(self.mode) == 'spot':
            return self.client.my_trades(symbol, recvWindow = recvWindow)
        return self.client.get_all_orders(symbol)
    
    def placeOrder(self, params):
        return self.client.new_order(**params, recvWindow = recvWindow)
    
    def changeLeverage(self, symbol, leverage):
        response = self.client.change_leverage(symbol, leverage, recvWindow = recvWindow)
        return response
        
def getSpotClient(isTest):
    client = ChibiClient(accountType = 'spot', test = isTest, keys = keys_spot if isTest else getKeys())
    return client

def getFutureClient(isTest):
    client = ChibiClient(accountType = 'future', test = isTest, keys = keys_future if isTest else getKeys())
    return client




# params = {
#     'symbol': 'ETHUSDT',
#     'side': 'BUY',
#     'type': 'MARKET',
#     'quantity': 0.1
# }

# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 64000
# }

# client = getFutureClient(isTest = True)
# print(client.getMarkKlines('BTCUSDT', '1d', 5))
# print(client.getTrades('BTCUSDT'))
# print(client.changeLeverage('BTCUSDT', 5))
# print(client.placeOrder(**params))







# 合约下单params参数文档
# https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
# 现货下单params参数文档
# https://binance-docs.github.io/apidocs/spot/en/#new-order-trade


# #获取1根btc的分钟k线
# print(client.klines("BTCUSDT", "1m", limit = 1))

# #获取正在进行的交易单
# print(client.my_trades('BTCUSDT'))


