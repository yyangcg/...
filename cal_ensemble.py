#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/11/12 15:30
# @Author  : Yang Yuhan

import numpy as np

def get_y_pred(flist):
    pred_list = [np.loadtxt(f) for f in flist]
    return pred_list


def inverse(pred, eps=0.00001):
    new_x = (np.log(pred) - np.log(1 - pred + eps))
    return new_x


def ensemble_pred(pred_list):
    tmp = [inverse(pred) for pred in pred_list]
    x =  np.mean(tmp,axis=0)
    en_pred = 1/(1 + np.exp(-x))
    return en_pred


def save(en_pred,save_path):
    with open(save_path, "w", encoding="utf-8") as f:
        f.write('\n'.join([str(item) for item in en_pred]))


if __name__ == '__main__':
    flist = ['train_predict.txt','train_predict.txt','train_predict.txt']
    pred_list = get_y_pred(flist)
    en_pred = ensemble_pred(pred_list)
    print(ensemble_pred(pred_list))
    print(ensemble_pred([0.1,0.15,0.08]))
    save(en_pred,'en_pred.txt')
