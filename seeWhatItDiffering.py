import pandas as pd
import plotly.graph_objects as go

# 读取实际值 CSV 文件
df_actual = pd.read_csv('predicts/FactData_5m.csv', header=0)
# df_actual = df_actual.iloc[0::5]

# 读取预测值 CSV 文件
df_predict = pd.read_csv('predicts/PredictNow0503-3.csv', header=0)
df_predict = df_predict.iloc[0::5] # 每5行读一行
df_predict = df_predict[df_predict['high_5m_confidence'] >= 0.8] # 置信度筛选
df_predict = df_predict[df_predict['low_5m_confidence'] >= 0.8] # 置信度筛选
df_predict = df_predict[df_predict['price_5m_confidence'] >= 0.8] # 置信度筛选

# 将 datatime 列转换类型
df_predict['datatime'] = pd.to_datetime(df_predict['datatime'], unit='ms')
df_actual['datatime'] = pd.to_datetime(df_actual['open_time'], unit='ms')

# 创建实际值 K 线图
candlestick1 = go.Candlestick(x=df_actual['datatime'],
                              open=df_actual['open'], high=df_actual['high'],
                              low=df_actual['low'], close=df_actual['close'],
                              name='Actual',
                              increasing_line_color='#5ECA8C',
                              decreasing_line_color='#E3314B',
                              opacity=1  # 设置为0可隐藏
                              )
start_time = min(df_actual['datatime']).strftime("%Y-%m-%d %H:%M:%S")
end_time = max(df_actual['datatime']).strftime("%Y-%m-%d %H:%M:%S")

# 创建预测值 K 线图
candlestick2 = go.Candlestick(x=df_predict['datatime'],
                              open=df_predict['currentPrice'], high=df_predict['high_5m'],
                              low=df_predict['low_5m'], close=df_predict['price_5m'],
                              name='Predict',
                              increasing_line_color='#F0D747',
                              decreasing_line_color='#306EA1',
                              opacity=1  # 设置为0可隐藏
                              )

fig = go.Figure(data=[candlestick1, candlestick2])
fig.update_layout(title=f"Data from {start_time} to {end_time}",
                  title_x=0.5,
                  title_y=0.95,
                  title_xanchor="center",
                  title_yanchor="top",
                  title_font=dict(size=18, family='sans-serif', weight='bold'),
                  title_xref="paper",
                  title_yref="paper",
                  margin=dict(t=50),
                  plot_bgcolor='#F8F8F8',
                  hovermode="x unified",
                  hoverlabel=dict(bgcolor="white", font_size=12))
fig.show()
