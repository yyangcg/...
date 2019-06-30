# -*- coding:utf-8 -*-
'''
Created on 2018/7/30

@author: kongyangyang
'''
import xgboost as xgb
from xgboost.sklearn import XGBClassifier
from sklearn2pmml.pipeline import PMMLPipeline
import matplotlib

matplotlib.use('Agg')
from numpy import *
import matplotlib.pyplot as plt


class XgboostExperiment(object):
    def __init__(self):
        pass

    @staticmethod
    def experiment(X, Y, params):
        pipelineModel = XgboostExperiment.train(X, Y, params)
        xgb.plot_importance(pipelineModel.named_steps['xgbclassifier'], max_num_features=30)
        plt.savefig("/data/kongyy/ctr/" + "xgboost_feature_importance_30")

        return pipelineModel

    @staticmethod
    def train(X, Y, params):
        """
        params = {
            'booster': 'gbtree',
            'objective': 'binary:logistic',
            'subsample': 0.6,
            'colsample_bytree': 0.8,
            'eta': 0.1,
            'max_depth': 1,
            'min_child_weight': 1,
            'gamma': 0.0,
            'silent': 0,
            'eval_metric': 'error'
        }

        params = {
            'booster': 'gbtree',
            'objective': 'multi:softmax',  # 多分类的问题
            'num_class': 10,               # 类别数，与 multisoftmax 并用
            'gamma': 0.1,                  # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2这样子。
            'max_depth': 12,               # 构建树的深度，越大越容易过拟合
            'lambda': 2,                   # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合。
            'subsample': 0.7,              # 随机采样训练样本
            'colsample_bytree': 0.7,       # 生成树时进行的列采样
            'min_child_weight': 3,
            'silent': 1,                   # 设置成1则没有运行信息输出，最好是设置为0.
            'eta': 0.007,                  # 如同学习率
            'seed': 1000,
            'nthread': 4,                  # cpu 线程数
        }

        :param X:
        :param Y:
        :param params:
        :return:
        """
        classifier = XGBClassifier(**params)
        # dtrain = xgb.DMatrix(X, Y)
        pipeline = PMMLPipeline([("xgbclassifier", classifier)])
        # xgb.train(params, dtrain, num_boost_round))])
        pipeline.fit(X, Y)
        return pipeline
