# -*- coding:utf-8 -*-
'''
Created on 2018/7/30

@author: kongyangyang
'''
from sklearn.metrics import recall_score
from sklearn.ensemble import GradientBoostingClassifier
from sklearn2pmml.pipeline import PMMLPipeline
from sklearn import preprocessing

from sklearn.externals import joblib


class GbdtExperiment(object):
    def __init__(self):
        pass

    @staticmethod
    def train(X, Y, params):
        pipeline = PMMLPipeline([("gbtclassifier",
                                  GradientBoostingClassifier(**params))])
        pipeline.fit(X, Y)

        importance = list(pipeline.named_steps['gbtclassifier'].feature_importances_)
        # print(importance)
        max_importance = max(importance)
        # print(max(importance), importance.index(max_importance))
        return pipeline
