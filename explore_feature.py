# -*- coding:utf-8 -*-
'''
Created on 2018/8/24

@author: kongyangyang
'''

# 探索特征的分布
import sys
import platform
import yaml
import matplotlib

matplotlib.use('Agg')
from numpy import *
import numpy as np
import matplotlib.pyplot as plt

sys.path.append("../../")
from dsp.ctr.data_manager import DataManager

config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())


def explore_nonz(data_path):
    data_manager_instance.loadLabeledPoint(data_path)
    pos_samples = data_manager_instance.data["pos_samples"]["X"]
    neg_samples = data_manager_instance.data["neg_samples"]["X"]

    pos_columns = (pos_samples != 0).sum(0) / pos_samples.shape[0]
    neg_columns = (neg_samples != 0).sum(0) / neg_samples.shape[0]

    x = linspace(0, pos_columns.shape[0], pos_columns.shape[0])
    plt.plot(x, pos_columns, 'r', linewidth=2)
    # plt.plot(x, neg_columns, 'b', linewidth=2)
    plt.xlabel(r'feature', fontsize=16)
    plt.ylabel(r'nonzero ratio', fontsize=16)
    plt.savefig(config_param["workdir"][platform.system()] + "explore_nonz-pos.png")

    plt.figure()
    plt.plot(x, neg_columns, 'b', linewidth=2)
    plt.xlabel(r'feature', fontsize=16)
    plt.ylabel(r'nonzero ratio', fontsize=16)
    plt.savefig(config_param["workdir"][platform.system()] + "explore_nonz-neg.png")


if __name__ == "__main__":
    channelid = 4
    data_manager_instance = DataManager(channelid=channelid, workdir=config_param["workdir"][platform.system()])

    explore_nonz(config_param["workdir"][platform.system()] + "samples-optimization_{}.labeledpoint".format(channelid))
