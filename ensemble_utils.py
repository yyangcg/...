# -*- coding:utf-8 -*-
"""
file name: ensemble_utils.py
Created on 2018/11/20
@author: kyy_b
@desc:
"""

import numpy as np


def get_y_pred(flist):
    pred_list = [np.loadtxt(f) for f in flist]
    return pred_list


def inverse(pred, eps=0.00001):
    new_x = (np.log(pred) - np.log(1 - pred + eps))
    return new_x


def ensemble_pred(pred_list):
    tmp = [inverse(pred) for pred in pred_list]
    x = np.mean(tmp, axis=0)
    en_pred = 1 / (1 + np.exp(-x))
    return en_pred


if __name__ == "__main__":
    pass
