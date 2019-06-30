# -*- coding:utf-8 -*-
'''
Created on 2018/8/22

@author: kongyangyang
'''
from sklearn.ensemble import GradientBoostingClassifier
from sklearn2pmml.pipeline import PMMLPipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.externals import joblib
import sys
import os
from sklearn_pandas import DataFrameMapper
from sklearn.feature_selection import SelectKBest
from sklearn.model_selection import train_test_split

sys.path.append("../../../")
from dsp.ctr.evaluation import *


class GbdtPlusLrExperiment(object):
    def __init__(self):
        pass

    @staticmethod
    def experiment(X_train, X_test, y_train, y_test, params):
        grd_lm, gbt, gbt_enc = GbdtPlusLrExperiment.train(X_train, y_train, params)
        GbdtPlusLrExperiment.evalution(grd_lm, gbt, gbt_enc, X_train, X_test, y_train, y_test)

        return None

    @staticmethod
    def train(X_train, y_train, params):
        # It is important to train the ensemble of trees on a different subset
        # of the training data than the linear regression model to avoid
        # overfitting, in particular if the total number of leaves is
        # similar to the number of training samples
        X_train, X_train_lr, y_train, y_train_lr = train_test_split(X_train, y_train, test_size=0.5)

        gbt = GradientBoostingClassifier(**params)
        gbt.fit(X_train, y_train)
        gbt_enc = OneHotEncoder()
        gbt_enc.fit(gbt.apply(X_train)[:, :, 0])

        grd_lm = LogisticRegression(max_iter=300)
        grd_lm.fit(gbt_enc.transform(gbt.apply(X_train_lr)[:, :, 0]),
                   y_train_lr)

        return grd_lm, gbt, gbt_enc

    @staticmethod
    def evalution(grd_lm, gbt, gbt_enc, X_train, X_test, y_train, y_test):
        y_pred_train = grd_lm.predict(
            gbt_enc.transform(gbt.apply(X_train)[:, :, 0]))  # [:, 1]
        y_pred_test = grd_lm.predict(
            gbt_enc.transform(gbt.apply(X_test)[:, :, 0]))  # [:, 1]
        print(classification_report(y_train, y_pred_train, target_names=["exposure", "click"]))
        print(classification_report(y_test, y_pred_test, target_names=["exposure", "click"]))
