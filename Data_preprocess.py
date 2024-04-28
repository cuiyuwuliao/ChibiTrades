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

import threading
import random
import DataSelect

# 当前数据中最新时间戳 最老时间戳
base_time_latest = int(data1m['open_time'].max()/1000)
base_time_fix_latest = base_time_latest - 5*60 - 1 #回退5分钟

base_time_oldest = int(data1m['open_time'].min()/1000)
base_time_fix_oldest = base_time_oldest + 36*24*3600 + 1 #增加36天

# 随机生成时间戳
timestamp1 = [random.randint(base_time_fix_latest-15*24*3600, base_time_fix_latest) for _ in range(5000)] #注意此处用秒为单位 而不是毫秒
timestamp2 = [random.randint(base_time_fix_oldest, base_time_fix_latest) for _ in range(15000)]
timestamps = timestamp1+timestamp2


# 分成10个子列表
timestamps_per_thread = len(timestamps) // 10
timestamp_chunks = [timestamps[i:i+timestamps_per_thread] for i in range(0, len(timestamps), timestamps_per_thread)]

# 定义线程类
class MyThread(threading.Thread):
    def __init__(self, timestamps):
        super().__init__()
        self.timestamps = timestamps

    def run(self):
        global Xlist
        global Ylist
        dfs = []
        for ts in self.timestamps:
            df, Xlist, Ylist = DataSelect.SelectFitdata(data1m, data3m, data15m, data1h, data4h, data1d, base_time=ts*1000)
            dfs.append(df)
        with lock:
            results.extend(dfs)

# 创建锁
lock = threading.Lock()

# 定义全局变量
results = []
Xlist = []
Ylist = []

# 创建并启动线程
threads = []
for chunk in timestamp_chunks:
    thread = MyThread(chunk)
    thread.start()
    threads.append(thread)

# 等待所有线程结束
for thread in threads:
    thread.join()

# 使用concat函数将所有DataFrame按行连接
result_df = pd.concat(results, ignore_index=True)

# 输出为csv
result_df.to_csv(r'D:\Binance\fitdata0428_2.csv')

print(Xlist)
print(Ylist)

