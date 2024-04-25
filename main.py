import Predict
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