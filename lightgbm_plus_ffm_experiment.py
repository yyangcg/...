# -*- coding:utf-8 -*-
'''
Created on 2018/8/22

@author: kongyangyang
'''
import numpy as np
from sklearn.preprocessing import OneHotEncoder
import lightgbm as lgb
import xlearn as xl
import os
import sys
import platform
from sklearn import preprocessing
from dsp.ctr.report import Report
from dsp.ctr.resample_by_cluster import *
from sklearn.model_selection import train_test_split
from dsp.ctr.experiment.ffm_experiment import FFMExperiment
from dsp.ctr.evaluation import evaluation_for_xlearn

sys.path.append("../../")


class LightGbmPlusFFMExperiment(FFMExperiment):
    def __init__(self, config_params):
        super(LightGbmPlusFFMExperiment, self).__init__(config_params)
        self.config_params = config_params
        self.algo = "lightgbm_plus_ffm"
        self.params_gbm = self.config_params[self.algo]["lightgbm"]

    def prepare_for_ffm(self, dataframe):
        train_x, train_y, test_x, test_y, header = LightGbmPlusFFMExperiment.scale_and_split(dataframe)
        print("train_x_before_lgbm.shape = ", train_x.shape)
        print("test_x_before_lgbm.shape = ", test_x.shape)
        self.generate_feature(train_x, train_y, test_x, test_y, header)

    def experiment(self, dataframe=None):
        super(LightGbmPlusFFMExperiment, self).experiment(dataframe, self.algo)

    def generate_feature(self, train_x, train_y, test_x, test_y, header):
        train_x_transform, test_x_transform = self.feature_transformer(train_x, train_y, test_x,
                                                                       test_y)

        self.generate_train_test_valid_data(train_x, train_y, header[1:], "ffm_train_python.txt", train_x_transform)
        self.generate_train_test_valid_data(test_x, test_y, header[1:], "ffm_test_python.txt", test_x_transform)

    def feature_transformer(self, x_train, y_train, x_test, y_test):
        gbm = lgb.LGBMClassifier(**self.params_gbm).fit(x_train, y_train)  # early_stopping_rounds=5)

        gbt_enc = OneHotEncoder()
        leaf_index_train = gbm.predict(x_train, pred_leaf=True)
        gbt_enc.fit(leaf_index_train)
        train_x_transform = gbt_enc.transform(leaf_index_train)
        test_x_transform = gbt_enc.transform(gbm.predict(x_test, pred_leaf=True))

        gbm.booster_.save_model(self.config_params["workdir"][platform.system()] + "lightgbm.txt")

        # pipelineModel = PMMLPipeline([("xgboost", XGBClassifier(**params))])
        # pipelineModel.fit(x_train, y_train)
        # sklearn2pmml(pipelineModel, "/data/kongyy/ctr_online/model/xgboost_feature.pmml", with_repr=True)

        return train_x_transform, test_x_transform

    def generate_train_test_valid_data(self, x, y, column_names, filename, *train_transform):
        col2field_id = {}
        field_name_dict = {}
        train_transform = train_transform[0]
        for idx, name in enumerate(column_names):
            items = name.split(":")
            if len(items) == 3:
                field = ":".join(items[:2])
            else:
                field = items[0]
            if field not in field_name_dict:
                field_name_dict[field] = len(field_name_dict)
            col2field_id[idx] = field_name_dict[field]

        if not os.path.exists(self.config_params["workdir"][platform.system()] + "ffm"):
            os.mkdir(self.config_params["workdir"][platform.system()] + "/ffm")

        with open(self.config_params["workdir"][platform.system()] + "ffm/{}".format(filename), "w",
                  encoding="utf-8") as file_write:
            axis_pos = x.nonzero()
            cur_r = 0
            cur_sampele = []
            for i in range(axis_pos[0].shape[0]):
                r, l = axis_pos[0][i], axis_pos[1][i]
                if r == 0 and len(cur_sampele) == 0:
                    cur_sampele = [str(y[0])]
                if r == cur_r:
                    cur_sampele.append(":".join([str(col2field_id[l]), str(l), str(x[r, l])]))
                else:
                    leaf = train_transform[cur_r - 1, :]
                    col_start = x.shape[1]
                    cur_sampele += [
                        ":".join([str(len(field_name_dict) + i), str(col_start + leaf.indices[i]), str(1.0)]) for i in
                        range(leaf.indices.shape[0])]
                    file_write.write(" ".join(cur_sampele) + "\n")
                    cur_sampele = [str(y[r]), ":".join([str(col2field_id[l]), str(l), str(x[r, l])])]
                cur_r = r


if __name__ == "__main__":
    pass
    # config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    # workdir = config_param["workdir"][platform.system()]
    # xgboost_plus_ffm = XgboostPlusFFMExperiment()
    # xgboost_plus_ffm.train_ffm()
