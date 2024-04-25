import joblib
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np

model_h5_file_path = 'rfmodel_high_yh5_2024-04-24.pkl'
model_l5_file_path = 'rfmodel_high_yl5_2024-04-24.pkl'
model_o5_file_path = 'rfmodel_high_y5_2024-04-24.pkl'

# 加载模型文件
model_h5 = joblib.load(model_h5_file_path)
model_l5 = joblib.load(model_l5_file_path)
model_o5 = joblib.load(model_o5_file_path)


def Model_o5_Predict(Xdata):
    # 使用加载的模型进行预测
    o5prediction = model_o5.predict(Xdata)
    # 获取所有树的预测值
    all_tree_predictions = np.stack([estimator.predict(Xdata) for estimator in model_o5.estimators_])
    # 计算标准差和平均值
    predictions_std = np.std(all_tree_predictions, axis=0)
    predictions_mean = np.mean(all_tree_predictions, axis=0)
    # 计算当前预测结果的可信程度
    predictions_trust = predictions_mean / predictions_std 
    return o5prediction,predictions_trust

def Model_h5_Predict(Xdata):
    # 使用加载的模型进行预测
    h5prediction = model_h5.predict(Xdata)
    # 获取所有树的预测值
    all_tree_predictions = np.stack([estimator.predict(Xdata) for estimator in model_h5.estimators_])
    # 计算标准差和平均值
    predictions_std = np.std(all_tree_predictions, axis=0)
    predictions_mean = np.mean(all_tree_predictions, axis=0)
    # 计算当前预测结果的可信程度
    predictions_trust = predictions_mean / predictions_std 
    return h5prediction,predictions_trust

def Model_l5_Predict(Xdata):
    # 使用加载的模型进行预测
    l5prediction = model_l5.predict(Xdata)
    # 获取所有树的预测值
    all_tree_predictions = np.stack([estimator.predict(Xdata) for estimator in model_l5.estimators_])
    # 计算标准差和平均值
    predictions_std = np.std(all_tree_predictions, axis=0)
    predictions_mean = np.mean(all_tree_predictions, axis=0)
    # 计算当前预测结果的可信程度
    predictions_trust = predictions_mean / predictions_std 
    return l5prediction,predictions_trust

