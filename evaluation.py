# -*- coding:utf-8 -*-
'''
Created on 2018/8/22

@author: kongyangyang
'''
from sklearn.metrics import classification_report
import matplotlib
from numpy import *
import numpy as np
import matplotlib.pyplot as plt
from sklearn import metrics
import pandas as pd
matplotlib.use('Agg')


def evaluateOnTrainAndTest(y_train, y_test, y_pre_train, y_pre_test):
    train_report = classification_report(y_train, [1 if y >= 0.5 else 0 for y in y_pre_train],
                                         target_names=["exposure", "click"])
    test_report = classification_report(y_test, [1 if y >= 0.5 else 0 for y in y_pre_test],
                                        target_names=["exposure", "click"])
    print(train_report)
    print(test_report)
    print("=" * 10 + " auc-test " + "=" * 10)
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pre_test, pos_label=1)
    auc_test = metrics.auc(fpr, tpr)
    print(auc_test)
    train_logloss = metrics.log_loss(y_train, y_pre_train)
    test_logloss = metrics.log_loss(y_test, y_pre_test)
    print("train logloss:", train_logloss)
    print("test logloss:", test_logloss)
    return {"classification_report_train": train_report,
            "classification_report_test": test_report,
            "logloss_train": str(train_logloss),
            "logloss_test": str(test_logloss),
            "auc_test": str(auc_test)
            }

def evaluateOnTest_yyh( y_test, y_pre_test):
    test_report = classification_report(y_test, [1 if y >= 0.5 else 0 for y in y_pre_test],
                                        target_names=["exposure", "click"])
    print(test_report)
    print("=" * 10 + " auc-test " + "=" * 10)
    fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pre_test, pos_label=1)
    auc_test = metrics.auc(fpr, tpr)
    print(auc_test)
    test_logloss = metrics.log_loss(y_test, y_pre_test)
    print("test logloss:", test_logloss)
    return {"classification_report_test": test_report,
            "logloss_test": str(test_logloss),
            "auc_test": str(auc_test)
            }

def evaluation_for_xlearn_yyh(train_real_path, test_real_path, train_predict_path, test_predict_path, w_pos, w_neg):
    """
        :param train_real_path:
        :param test_real_path:
        :param train_predict_path:
        :param test_predict_path:
        :return:
    """
    # y_pre_test = np.loadtxt(test_predict_path, dtype=np.float)
    # with open(test_real_path, "r", encoding="utf-8") as file_read:
    #     y_test = [float(line.strip().split(" ")[0]) for line in file_read]
    # evaluateOnTest_yyh( y_test, y_pre_test)
    y_pre_test = np.loadtxt(test_predict_path, dtype=np.float)
    y_pre_train = np.loadtxt(train_predict_path, dtype=np.float)
    with open(test_real_path, "r", encoding="utf-8") as file_read:
        y_test = [float(line.strip().split(" ")[0]) for line in file_read]
    with open(train_real_path, "r", encoding="utf-8") as file_read:
        y_train = [float(line.strip().split(" ")[0]) for line in file_read]
    evaluateOnTrainAndTest(y_train, y_test, y_pre_train, y_pre_test)
    data = pd.DataFrame()
    data['predictiom'] = y_pre_train
    data['label'] = y_train
    ks_cont, population, bad_number, bad_rate = calc_continus_ks(data)
    print('============ trainning ks value=========')
    print(max(ks_cont),population, bad_number, bad_rate)
    data.to_csv('/data/yangyuhan/workspace/ctr/hdfs_ctr/ffm/train_res.csv',encoding='utf-8',index=False)
    data = pd.DataFrame()
    data['predictiom'] = y_pre_test
    data['label'] = y_test
    ks_cont, population, bad_number, bad_rate = calc_continus_ks(data)
    print('============ testing ks value=========')
    print(max(ks_cont),population, bad_number, bad_rate)
    data.to_csv('/data/yangyuhan/workspace/ctr/hdfs_ctr/ffm/train_res.csv',encoding='utf-8',index=False)


def evaluation_for_xlearn(train_real_path, test_real_path, train_predict_path, test_predict_path):
    """
        :param train_real_path:
        :param test_real_path:
        :param train_predict_path:
        :param test_predict_path:
        :return:
    """
    y_pre_test = np.loadtxt(test_predict_path, dtype=np.float)
    y_pre_train = np.loadtxt(train_predict_path, dtype=np.float)

    with open(test_real_path, "r", encoding="utf-8") as file_read:
        y_test = [float(line.strip().split(" ")[0]) for line in file_read]

    with open(train_real_path, "r", encoding="utf-8") as file_read:
        y_train = [float(line.strip().split(" ")[0]) for line in file_read]

    evaluateOnTrainAndTest(y_train, y_test, y_pre_train, y_pre_test)


def plot_prob_curve(y_ture, y_pred_prob):
    zipped = zip(y_ture, y_pred_prob)
    result = list(sorted(zipped, key=lambda x: (x[0], x[1])))
    y_true = [r[0] for r in result]
    y_pred_prob = [r[1] for r in result]
    fig = plt.figure()
    x = linspace(0, y_ture.shape[0], y_ture.shape[0])
    plt.plot(x, y_ture, 'r', linewidth=2)
    plt.plot(x, y_pred_prob, 'b', linewidth=2)
    plt.xlabel('sample', fontsize=16)
    plt.ylabel('prob', fontsize=16)
    plt.savefig("prob_cuve.png")


def calc_continus_ks(self, data, prediction="prediction", label="label"):
    """

    :param data:
    :param prediction:
    :param label:
    :return:
    """
    data = data.sort_values (prediction, ascending=False)
    count = data.groupby (prediction, sort=False)[label].agg ({'bad': np.count_nonzero, 'obs': np.size})
    count["good"] = count["obs"] - count["bad"]
    t_bad = np.sum (count["bad"])
    t_good = np.sum (count["good"])
    ks_vector = np.abs (np.cumsum (count["bad"]) / t_bad - np.cumsum (count["good"]) / t_good)
    population = np.sum (count["obs"])
    bad_number = np.sum (count["bad"])
    bad_rate = bad_number / population
    return ks_vector, population, bad_number, bad_rate

if __name__ == "__main__":
    pass
