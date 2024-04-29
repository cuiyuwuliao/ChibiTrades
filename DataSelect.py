import numpy as np

def SelectFitdata(data1minput,data3minput,data15minput,data1hinput,data4hinput,data1dinput, base_time = 1711324740000):
    import pandas as pd
    data1m = data1minput.copy()
    data3m = data3minput.copy()
    data15m = data15minput.copy()
    data1h = data1hinput.copy()
    data4h = data4hinput.copy()
    data1d = data1dinput.copy()

    # 新建DataFrame存储结果
    new_data = {}
    Xlist = []
    Ylist = []

    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data1m['open_time'] - base_time).argmin()
    closest_row = data1m.iloc[closest_index]
    base_time = int(closest_row['open_time'])
    new_data['base_time'] = base_time #此项用于数据检查



    # 预处理，将所有价格减去基准价格再除以基准价格
    current_price = data1m[data1m['open_time'] == base_time]['open'].iloc[0]
    new_data['current_price'] = current_price
    Xlist.append('current_price')
    data1m['open'] = (data1m['open'] - current_price)/current_price
    data1m['high'] = (data1m['high'] - current_price)/current_price
    data1m['low'] = (data1m['low'] - current_price)/current_price
    data1m['close'] = (data1m['close'] - current_price)/current_price
    data3m['open'] = (data3m['open'] - current_price)/current_price
    data3m['high'] = (data3m['high'] - current_price)/current_price
    data3m['low'] = (data3m['low'] - current_price)/current_price
    data3m['close'] = (data3m['close'] - current_price)/current_price
    data15m['open'] = (data15m['open'] - current_price)/current_price
    data15m['high'] = (data15m['high'] - current_price)/current_price
    data15m['low'] = (data15m['low'] - current_price)/current_price
    data15m['close'] = (data15m['close'] - current_price)/current_price
    data1h['open'] = (data1h['open'] - current_price)/current_price
    data1h['high'] = (data1h['high'] - current_price)/current_price
    data1h['low'] = (data1h['low'] - current_price)/current_price
    data1h['close'] = (data1h['close'] - current_price)/current_price
    data4h['open'] = (data4h['open'] - current_price)/current_price
    data4h['high'] = (data4h['high'] - current_price)/current_price
    data4h['low'] = (data4h['low'] - current_price)/current_price
    data4h['close'] = (data4h['close'] - current_price)/current_price
    data1d['open'] = (data1d['open'] - current_price)/current_price
    data1d['high'] = (data1d['high'] - current_price)/current_price
    data1d['low'] = (data1d['low'] - current_price)/current_price
    data1d['close'] = (data1d['close'] - current_price)/current_price

    # 循环处理每一分钟的数据
    for i in range(1, 61):
        # 计算当前分钟的时间戳，从现在到过去1小时
        current_time = base_time - i * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data1m[data1m['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_1_{i}'] = current_data['open']
        new_data[f'high_1_{i}'] = current_data['high']
        new_data[f'low_1_{i}'] = current_data['low']
        new_data[f'close_1_{i}'] = current_data['close']
        new_data[f'volume_1_{i}'] = current_data['volume']
        new_data[f'count_1_{i}'] = current_data['count']
        new_data[f'taker_buy_volume_1_{i}'] = current_data['taker_buy_volume']
        Xlist.append(f'open_1_{i}')
        Xlist.append(f'high_1_{i}')
        Xlist.append(f'low_1_{i}')
        Xlist.append(f'close_1_{i}')
        Xlist.append(f'volume_1_{i}')
        Xlist.append(f'count_1_{i}')
        Xlist.append(f'taker_buy_volume_1_{i}')

    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data3m['open_time'] - base_time - 60 * 60 * 1000).argmin()
    closest_row = data3m.iloc[closest_index]
    base_fixed_time = int(closest_row['open_time'])
    # 处理每3分钟、10分钟、24分钟、60分钟、120分钟的数据
    for i in range(1, 61):
        # 计算当前分钟的时间戳,从过去1小时到过去4小时
        current_time = base_fixed_time  - i * 3 * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data3m[data3m['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_3_{i}'] = current_data['open']
        new_data[f'high_3_{i}'] = current_data['high']
        new_data[f'low_3_{i}'] = current_data['low']
        new_data[f'volume_3_{i}'] = current_data['volume']
        new_data[f'count_3_{i}'] = current_data['count']
        new_data[f'taker_buy_volume_3_{i}'] = current_data['taker_buy_volume']
        Xlist.append(f'open_3_{i}')
        Xlist.append(f'high_3_{i}')
        Xlist.append(f'low_3_{i}')
        Xlist.append(f'volume_3_{i}')
        Xlist.append(f'count_3_{i}')
        Xlist.append(f'taker_buy_volume_3_{i}')


    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data15m['open_time'] - base_time - 60 * 60 * 1000 - 60 * 3 * 60 * 1000).argmin()
    closest_row = data15m.iloc[closest_index]
    base_fixed_time = int(closest_row['open_time'])
    for i in range(1, 17):
        # 计算当前分钟的时间戳,从u过去4小时到过去8小时
        current_time = base_fixed_time - i * 15 * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data15m[data15m['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_15_{i}'] = current_data['open']
        new_data[f'high_15_{i}'] = current_data['high']
        new_data[f'low_15_{i}'] = current_data['low']
        new_data[f'count_15_{i}'] = current_data['count']
        new_data[f'volume_15_{i}'] = current_data['volume']
        new_data[f'taker_buy_volume_15_{i}'] = current_data['taker_buy_volume']
        Xlist.append(f'open_15_{i}')
        Xlist.append(f'high_15_{i}')
        Xlist.append(f'low_15_{i}')
        Xlist.append(f'count_15_{i}')
        Xlist.append(f'volume_15_{i}')
        Xlist.append(f'taker_buy_volume_15_{i}')


    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data1h['open_time'] - base_time - 60 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000).argmin()
    closest_row = data1h.iloc[closest_index]
    base_fixed_time = int(closest_row['open_time'])
    for i in range(1, 17):
        # 计算当前分钟的时间戳,从u过去8小时到过去24小时
        current_time = base_fixed_time - i * 60 * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data1h[data1h['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_60_{i}'] = current_data['open']
        new_data[f'high_60_{i}'] = current_data['high']
        new_data[f'low_60_{i}'] = current_data['low']
        new_data[f'count_60_{i}'] = current_data['count']
        new_data[f'volume_60_{i}'] = current_data['volume']
        new_data[f'taker_buy_volume_60_{i}'] = current_data['taker_buy_volume']
        Xlist.append(f'open_60_{i}')
        Xlist.append(f'high_60_{i}')
        Xlist.append(f'low_60_{i}')
        Xlist.append(f'count_60_{i}')
        Xlist.append(f'volume_60_{i}')
        Xlist.append(f'taker_buy_volume_60_{i}')

    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data4h['open_time'] - base_time - 60 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000 - 16 * 60 * 60 * 1000).argmin()
    closest_row = data4h.iloc[closest_index]
    base_fixed_time = int(closest_row['open_time'])
    for i in range(1, 19):
        # 计算当前分钟的时间戳,从u过去24小时到过去96小时
        current_time = base_fixed_time - i * 240 * 60 * 1000
        #18号数据缺失 临时使用代码

        #临时代码结束
        # 获取对应时间戳的数据
        current_data = data4h[data4h['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_240_{i}'] = current_data['open']
        new_data[f'high_240_{i}'] = current_data['high']
        new_data[f'low_240_{i}'] = current_data['low']
        new_data[f'volume_240_{i}'] = current_data['volume']
        Xlist.append(f'open_240_{i}')
        Xlist.append(f'high_240_{i}')
        Xlist.append(f'low_240_{i}')
        Xlist.append(f'volume_240_{i}')

    # 找出与current_time最接近的值的索引,取得该数据中最接近basetime的time
    closest_index = np.abs(data1d['open_time'] - base_time - 60 * 60 * 1000 - 60 * 3 * 60 * 1000 - 16 * 15 * 60 * 1000 - 16 * 60 * 60 * 1000 - 18 * 240 * 60 * 1000).argmin()
    closest_row = data1d.iloc[closest_index]
    base_fixed_time = int(closest_row['open_time'])
    for i in range(1, 33):
        # 计算当前分钟的时间戳,从u过去96小时(4day)到过去36day
        current_time = base_fixed_time - i * 1440 * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data1d[data1d['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_1440_{i}'] = current_data['open']
        new_data[f'high_1440_{i}'] = current_data['high']
        new_data[f'low_1440_{i}'] = current_data['low']
        Xlist.append(f'open_1440_{i}')
        Xlist.append(f'high_1440_{i}')
        Xlist.append(f'low_1440_{i}')


    # 处理未来1-5分钟的1分钟数据
    high_y5 = -99999
    low_y5 = 99999
    for i in range(1, 6):
        # 计算当前分钟的时间戳，从现在到过去1小时
        current_time = base_time + i * 60 * 1000
        # 获取对应时间戳的数据
        current_data = data1m[data1m['open_time'] == current_time].iloc[0]
        # 将数据存入新的DataFrame中
        new_data[f'open_y1_{i}'] = current_data['open']
        new_data[f'high_y1_{i}'] = current_data['high']
        new_data[f'low_y1_{i}'] = current_data['low']
        new_data[f'close_y1_{i}'] = current_data['close']
        if (current_data['high'] > high_y5):
            high_y5 = current_data['high']
        if (current_data['low'] < low_y5):
            low_y5 = current_data['low']
        Ylist.append(f'open_y1_{i}')
        Ylist.append(f'high_y1_{i}')
        Ylist.append(f'low_y1_{i}')
        Ylist.append(f'close_y1_{i}')
    new_data['high_y5'] = high_y5 #添加未来5分钟内最大涨幅
    new_data['low_y5'] = low_y5 #添加未来5分钟内最大跌幅
    Ylist.append('high_y5')
    Ylist.append('low_y5')

    # 创建新的DataFrame
    new_df = pd.DataFrame([new_data])
    # 打印新的DataFrame
    #print(new_df)
    #return new_df,Xlist,Ylist
    return new_df

