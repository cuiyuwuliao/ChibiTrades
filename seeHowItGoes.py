import pandas as pd
import grapher as gp
import os

proj_dir = os.path.dirname(os.path.abspath(__file__))
preds = pd.read_csv(os.path.join(proj_dir, 'predicts','predictNow0503-2.csv'))

l = len(preds)

pred_5ms = preds['price_5m'].iloc[1:l-5]
reals = preds['currentPrice'].iloc[6:l]
highs = preds['high_5m'].iloc[1:l-5]
lows = preds['low_5m'].iloc[1:l-5]


table_pred_5ms = pred_5ms.values
table_reals = reals.values
table_highs = highs.values
table_lows = lows.values

gp.draw([table_pred_5ms, table_reals, table_highs, table_lows], labels=['预测曲线','实际曲线', '预测高价', '预测低价'], lines=4, grid=True)

