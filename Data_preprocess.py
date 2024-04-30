import os
import pandas as pd
import multiple as mtp
import time
import random
import DataSelect
from datetime import datetime;

# 项目目录
proj_dir = os.path.dirname(os.path.abspath(__file__))

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

direct1m = os.path.join(proj_dir, 'BTCusdtData1m')
direct3m = os.path.join(proj_dir, 'BTCusdtData3m')
direct15m = os.path.join(proj_dir, 'BTCusdtData15m')
direct1h = os.path.join(proj_dir, 'BTCusdtData1h')
direct4h = os.path.join(proj_dir, 'BTCusdtData4h')
direct1d = os.path.join(proj_dir, 'BTCusdtData1d')

data1m = ReadData(direct1m)
data3m = ReadData(direct3m)
data15m = ReadData(direct15m)
data1h = ReadData(direct1h)
data4h = ReadData(direct4h)
data1d = ReadData(direct1d)

# 当前数据中最新时间戳 最老时间戳
base_time_latest = int(data1m['open_time'].max()/1000)
base_time_fix_latest = base_time_latest - 5*60 - 1 #回退5分钟

base_time_oldest = int(data1m['open_time'].min()/1000)
base_time_fix_oldest = base_time_oldest + 36*24*3600 + 1 #增加36天

# 随机生成时间戳
timestamp1 = [random.randint(base_time_fix_latest-15*24*3600, base_time_fix_latest) for _ in range(5000)] #注意此处用秒为单位 而不是毫秒
timestamp2 = [random.randint(base_time_fix_oldest, base_time_fix_latest) for _ in range(15000)]
timestamps = timestamp1+timestamp2

# 定义全局变量
#Xlist = []
#Ylist = []

# 处理数据的进程
def processDFS(q, cnt, a, b):
    #global Xlist
    #global Ylist
    dfs = []
    for idx in range(a, b):
        ts = timestamps[idx]
        cnt.value += 1
        print('cnt='+str(cnt.value)+',idx='+str(idx))
        #df, Xlist, Ylist = DataSelect.SelectFitdata(data1m, data3m, data15m, data1h, data4h, data1d, base_time=ts*1000)  # 假设SelectFitdata函数可以根据时间戳返回一个DataFrame
        df = DataSelect.SelectFitdata(data1m, data3m, data15m, data1h, data4h, data1d, base_time=ts*1000)
        dfs.append(df)
    q.put(dfs)

if __name__ == '__main__':  
    startTime = time.time()
    # 使用多进程进行数据预处理
    res = mtp.mtpcs(8, 20000, processDFS)
    print('res的长度')
    print(len(res))
    endTime = time.time()
    runTime = endTime - startTime
    print('运行时间：'+str(runTime)+'s')
    # 使用concat函数将所有DataFrame按行连接
    #print(Xlist)
    #print(Ylist)
    result_df = pd.concat(res, ignore_index=True)
    # 输出为csv
    date = datetime.today().strftime("%m%d")
    directory = os.path.join(proj_dir,'fitdata')
    if not os.path.exists(directory):
        os.makedirs(directory)
    result_df.to_csv(os.path.join(directory, f'fitdata{date}all.csv'))
