import pandas as pd
import plotly.graph_objects as go

# 读取实际值 CSV 文件
df_actual = pd.read_csv('predicts/FactData_5m.csv', header=0)

# 读取预测值 CSV 文件及预处理
df_predict = pd.read_csv('predicts/PredictNow_04.csv', skiprows=[1,1], header=0)
df_predict['currentPrice'] = df_predict['currentPrice'].shift(-1)
df_predict = df_predict.drop(df_predict.index[-1])

# 设置绘图起始行及步长
df_predict = df_predict.iloc[0::5]

# 筛选置信度达到阈值的行
valid_conf_level = 0.9
df_predict = df_predict[df_predict['high_5m_confidence']>=valid_conf_level]
df_predict = df_predict[df_predict['low_5m_confidence']>=valid_conf_level]
df_predict = df_predict[df_predict['price_5m_confidence']>=valid_conf_level]

# 计算价格波动幅度
df_predict['HighRate'] = (df_predict['high_5m'] - df_predict['currentPrice']) / df_predict['currentPrice']
df_predict['LowRate'] = (df_predict['low_5m'] - df_predict['currentPrice']) / df_predict['currentPrice']
df_actual['HighRate'] = (df_actual['high'] - df_actual['open']) / df_actual['open']
df_actual['LowRate'] = (df_actual['low'] - df_actual['open']) / df_actual['open']

# 将 datatime 列转换类型
df_predict['datatime'] = pd.to_datetime(df_predict['datatime']+60*1000, unit='ms')
df_actual['datatime'] = pd.to_datetime(df_actual['open_time'], unit='ms')

# 定义绘图颜色：实际值绿涨红跌，预测值黄涨蓝跌
green = '#5ECA8C'
red = '#E3314B'
yellow = '#F0D747'
blue = '#306EA1'
lightGrey = '#F8F8F8'

# 创建实际值 K 线图
candlestick1 = go.Candlestick(x=df_actual['datatime'],
                              open=df_actual['open'], high=df_actual['high'],
                              low=df_actual['low'], close=df_actual['close'],
                              name='Actual',
                              increasing_line_color=green,
                              decreasing_line_color=red)

# 获取实际值时间范围
start_time = min(df_actual['datatime']).strftime("%Y-%m-%d %H:%M")
end_time = max(df_actual['datatime']).strftime("%Y-%m-%d %H:%M")

# 创建预测值 K 线图
candlestick2 = go.Candlestick(x=df_predict['datatime'],
                              open=df_predict['currentPrice'], high=df_predict['high_5m'],
                              low=df_predict['low_5m'], close=df_predict['price_5m'],
                              name='Predict',
                              increasing_line_color=yellow,
                              decreasing_line_color=blue,
                              text=[f"hc: {hc:.4f}<br>lc: {lc:.4f}<br>pc: {pc:.4f}"
                                    f"<br>phr: {phr:.3%}<br>plr: {plr:.3%}"  # phr(predict high rate) 预测涨幅， plr(predict low rate) 预测跌幅
                                    f"<br>ahr: {ahr:.3%}<br>alr: {alr:.3%}"  # ahr(actual high rate) 实际涨幅， alr(actual low rate) 实际跌幅
                                    for hc, lc, pc, phr, plr, ahr, alr in zip(df_predict['high_5m_confidence'],
                                                                  df_predict['low_5m_confidence'],
                                                                  df_predict['price_5m_confidence'],
                                                                  df_predict['HighRate'],
                                                                  df_predict['LowRate'],
                                                                  df_actual['HighRate'],
                                                                  df_actual['LowRate']
                                                                  )]
                              )

# 绘制综合k线图
fig = go.Figure(data=[candlestick1, candlestick2])

fig.update_layout(title=f"Data from {start_time} to {end_time}",
                  title_x=0.5,
                  title_y=0.95,
                  title_xanchor="center",
                  title_yanchor="top",
                  title_font=dict(size=18, family='sans-serif', weight='bold'),
                  plot_bgcolor=lightGrey,
                  yaxis=dict(
                      title='Price',
                      title_font=dict(size=16, family='sans-serif', weight='bold'),
                      tickfont=dict(family='sans-serif', size=13)
                  ),
                  xaxis=dict(
                      title='Time',
                      title_font=dict(size=16, family='sans-serif', weight='bold'),
                      tickformat='%Y-%m-%d %H:%M',
                      tickfont=dict(family='sans-serif', size=13)
                  ),
                  hovermode="x",
                  hoverlabel=dict(font_size=13, font_family='sans-serif'))

# 添加实际价格最高价和最低价的注释
highest = max(df_actual['high'])
lowest = min(df_actual['low'])
fig.add_annotation(x=df_actual['datatime'][df_actual['high'].idxmax()], y=highest,
                   text=f'highest: {highest / 1000:.3f}k',
                   showarrow=True, bgcolor=yellow, arrowcolor=yellow, arrowhead=1, ax=0, ay=-40)
fig.add_annotation(x=df_actual['datatime'][df_actual['low'].idxmin()], y=lowest,
                   text=f'lowest: {lowest / 1000:.3f}k',
                   showarrow=True, bgcolor=yellow, arrowcolor=yellow, arrowhead=1, ax=0, ay=40)

fig.show()