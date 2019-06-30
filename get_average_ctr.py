# -*- coding:utf-8 -*-
'''
Created on 2018/8/21

@author: kongyangyang
'''
import yaml
import platform
import sys
import numpy as np
import pickle
from sklearn import preprocessing

sys.path.append("../../")
from dsp.ctr.data_manager import DataManager


# 统计 观察到的ctr的平均值， 以及预测的ctr的平均值

def get_avg_ctr():
    samples = data_manager.data
    X = np.vstack((samples["pos_samples"]["X"], samples["neg_samples"]["X"]))
    # Y = np.vstack((samples["pos_samples"]["Y"], samples["neg_samples"]["Y"]))

    print("ctr_true = ", samples["pos_samples"]["Y"].shape[0] / (
            samples["pos_samples"]["Y"].shape[0] + samples["neg_samples"]["Y"].shape[0]))

    scaler = preprocessing.StandardScaler().fit(X)
    x_scaler = scaler.transform(X)

    pipelineModel = pickle.load(open(workdir + "xgboost_4.pkl", "rb"))

    y_pre_train = pipelineModel.named_steps['xgbclassifier'].predict_proba(x_scaler)

    pred_click_num = sum([1 if y_pre_train[i][1] >= 0.5 else 0 for i in range(y_pre_train.shape[0])])

    print("ctr_pre_avg = ", pred_click_num / y_pre_train.shape[0])


if __name__ == "__main__":
    workdir = "E:/Work/jobs/data/DSP/CTR预估/samples/"
    if platform.system() == "Linux":
        workdir = "/data/kongyy/ctr/"
    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())

    channelid = '4'

    data_manager = DataManager(channelid=channelid, workdir=workdir)
    data_manager.loadLabeledPoint(workdir + "samples-optimization_labeledpoint_{}".format(channelid))
    get_avg_ctr()
