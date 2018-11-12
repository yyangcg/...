#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import numpy as np
import config as conf
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from utils import get_appdict
from pred_intere import predictlist

def data_split(data):
    data_train = csv.reader(open(data, 'r', errors='ignore'))
    with open(conf.data_dir, 'w',newline ='') as myFile:
        myWriter = csv.writer(myFile)
        myList = []
        for row in data_train:
            if row[18] != 'NULL':
                myWriter.writerow(row)
        print(len(myList))


def stratify_sample(data, ratio, label, rnd):
    # stratify dataset with 0/1
    # ratio: # of large dataset/ # of small dataset
    # lb_name: label colname
    # return: x, y, xtarget, ytarget

    import pandas as pd

    data_1 = data[data[label] == 1]
    data_0 = data[data[label] == 0]
    n1 = len(data_1)
    n0 = len(data_0)
    if n0 > n1:
        data_sample = data_0.sample(n=n1 * ratio, random_state=rnd)
        data_final = pd.concat([data_1, data_sample], axis=0)
        data_final.reset_index(inplace=True)
        data_final.drop(['index'], axis=1, inplace=True)
    elif n1 > n0:
        data_sample = data_1.sample(n=n0 * ratio, random_state=rnd)
        data_final = pd.concat([data_0, data_sample], axis=0)
        data_final.reset_index(inplace=True)
        data_final.drop(['index'], axis=1, inplace=True)
    else:
        data_final = data

    return data_final


if __name__ == '__main__':
    data_split(conf.data_raw_dir)

