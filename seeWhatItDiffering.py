import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
import pandas as pd
import numpy as np

df1 = pd.read_csv()
df2 = pd.read_csv()


# 添加一个整数索引列
df['index'] = np.arange(len(df))

# 绘制K线图
fig, ax = plt.subplots()

candlestick_ohlc(ax, zip(df['index'], df['Open'], df['High'], df['Low'], df['Close']), width=0.6, colorup='g', colordown='r')

# 设置X轴的刻度为日期
ax.set_xticks(df['index'])
ax.set_xticklabels(df['date'], rotation=45)

# 绘制预测价格
for i, row in df.iterrows():
    if i % 2 != 0:  # 偶数行是预测价格
        ax.plot([row['index'], row['index']], [row['Open'], row['Close']], color='blue', linestyle='--')

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Comparison of Actual and Predicted Prices')

plt.tight_layout()
plt.show()
