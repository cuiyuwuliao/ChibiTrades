import os
import pandas as pd
def ReadData(directory):
    # 指定目录路径
    # 读取目录下的所有文件名
    file_names = os.listdir(directory)
    # 初始化一个空的DataFrame
    combined_df = pd.DataFrame()
    # 逐个读取文件，并合并到combined_df中
    for file_name in file_names:
        if file_name.endswith('.csv'):
            file_path = os.path.join(directory, file_name)
            df = pd.read_csv(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # 打印合并后的DataFrame
    print(combined_df)
    return combined_df

direct1m = r'D:\Binance\BTCusdtData1m'
direct3m = r'D:\Binance\BTCusdtData3m'
direct15m = r'D:\Binance\BTCusdtData15m'
direct1h = r'D:\Binance\BTCusdtData1h'
direct4h = r'D:\Binance\BTCusdtData4h'
direct1d = r'D:\Binance\BTCusdtData1d'

data1m = ReadData(direct1m)
data3m = ReadData(direct3m)
data15m = ReadData(direct15m)
data1h = ReadData(direct1h)
data4h = ReadData(direct4h)
data1d = ReadData(direct1d)

import DataSelect
import random
import pandas as pd
# 随机生成时间戳
timestamps = [random.randint(1684108800, 1711324740) for _ in range(20000)]

# 将时间戳传递给SelectFitdata函数，并将返回的DataFrame收集到列表中
dfs = []
Xlist = []
Ylist = []
cnt = 0
for ts in timestamps:
    cnt = cnt + 1
    print(cnt)
    df, Xlist, Ylist = DataSelect.SelectFitdata(data1m, data3m, data15m, data1h, data4h, data1d, base_time=ts*1000)  # 假设SelectFitdata函数可以根据时间戳返回一个DataFrame
    dfs.append(df)
# 使用concat函数将所有DataFrame按行连接
print(Xlist)
print(Ylist)
result_df = pd.concat(dfs, ignore_index=True)
result_df.to_csv(r'D:\Binance\fitdata0423.csv')
