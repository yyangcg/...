# -*- coding:utf-8 -*-
'''
Created on 2018/8/14

@author: kongyangyang
'''
from sklearn import preprocessing
import numpy as np
import platform
from imblearn.under_sampling import RandomUnderSampler
import sys
import pickle

sys.path.append("../../")
from dsp.ctr.data_manager import DataManager


def resamples(samples):
    X = np.vstack((samples["pos_samples"]["X"], samples["neg_samples"]["X"]))
    Y = np.vstack((samples["pos_samples"]["Y"], samples["neg_samples"]["Y"]))
    rus = RandomUnderSampler(random_state=42)
    X_res, Y_res = rus.fit_sample(X, Y)

    return X_res, Y_res


def get_standardscaler(samples_path, channelid):
    data_manager = DataManager(channelid=channelid)
    data_manager.loadLabeledPoint(samples_path)
    X_res, Y_res = resamples(data_manager.data)
    scaler = preprocessing.StandardScaler().fit(X_res)
    pickle.dumps(open(workdir + "scaler_{}.pkl".format(channelid)), "wb")
    return scaler


if __name__ == "__main__":
    workdir = "E:/Work/jobs/data/DSP/CTR预估/samples/"
    if platform.system() == "Linux":
        workdir = "/data/kongyy/ctr/"

    featureValuesIndexDict = pickle.load(open(workdir + "featureValuesIndexDict.pkl", 'rb'))
    with open(workdir + "scaler.txt", "w", encoding="utf-8") as file_write:
        for channelid in featureValuesIndexDict.keys():
            if str(channelid) not in ["13", "14"]:
                scaler = get_standardscaler(workdir + "samples-optimization_labeledpoint_{}".format(channelid),
                                            channelid=channelid)
                file_write.write(str(channelid) + "\t" + "mean\t" + ",".join([str(i) for i in scaler.mean_]) + "\n")
                file_write.write(str(channelid) + "\t" + "std\t" + ",".join([str(i) for i in scaler.scale_]) + "\n")
