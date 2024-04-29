import API


# 使用前先加载环境，cd到ChibiTrades目录，然后控制台运行: source ./venv/bin/activate

# 测试网络网页客户端：https://testnet.binancefuture.com/en/futures/BTCUSDT
# 账号：ycui8444@gmail.com
# 密码：chibiTRADES123
# 网页客户端和api信息同步，下单之后可以直接看到

# 合约下单params参数文档
# https://binance-docs.github.io/apidocs/futures/en/#new-order-trade
# 现货下单params参数文档
# https://binance-docs.github.io/apidocs/spot/en/#new-order-trade

# 如果要使用真实账号：
# 获取同路径“keys.txt”文件中的api keys，格式如下
# apiKey = "your key" (记得加引号)
# secretKey = "your key" (记得加引号)



#登陆模拟的合约账户，如果要用真实账号，需要保证keys.txt文件里有账号信息
client = API.getFutureClient(isTest = True)

#获取两根一分钟的标记价格k线
print(client.getMarkKlines('BTCUSDT', '1m', 2))

#更改BTCUSDT的交易杠杆为5倍
print(client.changeLeverage('BTCUSDT', 5))

#下单买0.01个合约btc
print(client.placeOrder({
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': 0.01
}))

#平仓（即卖出0.01个合约btc), 已经成交的合约只能卖，不能取消
print(client.placeOrder({
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'MARKET',
    'quantity': 0.01
}))

#下限价单
print(client.placeOrder(params = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.002,
    'price': 61000
}))

#获取现有的交易
orders = client.getTrades('BTCUSDT')
print(orders)

#取消还没成交的限价单，id可以用getTrades查询，或者下单时返回的response里也有，也可以直接在客户端看
for order in orders:
    if order['status'] == 'NEW':
        id = order['orderId']
        print(client.cancelOrder('BTCUSDT', id))



