#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 17:37
# @Author  : Yang Yuhan
import numpy as np
import config as conf
import csv
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
from utils import get_appdict
from pred_intere import predictlist

def get_data(training_filename, testing_filename = None):
    if testing_filename is not None:
        print("Loading data...")
        data_train = csv.reader(open(training_filename,'r',errors='ignore'))
        data_test = csv.reader(open(testing_filename,'r',errors='ignore'))
        print("Finished loading data.")
        return data_train, data_test
    else:
        print("Loading data...")
        data_train = csv.reader(open(training_filename,'r',errors='ignore'))
        print("Finished loading data.")
        return data_train


def get_features(data):
    userid = []
    cityid = []
    provinceid = []
    hour = []
    devicetype = []
    mobiletype = []
    nettype = []
    appname = []
    for row in data:
        userid.append(row[1])
        appname.append(row[0])
        cityid.append(str(row[8]))
        provinceid.append(str(row[7]))
        hour.append(row[5])
        devicetype.append(row[18])
        mobiletype.append(row[19])
        nettype.append(str(row[20]))
    print(len(cityid))

    return userid[1:],appname[1:],cityid[1:],provinceid[1:],hour[1:],devicetype[1:],mobiletype[1:],nettype[1:]




def get_interest(appname):
    app_interest, app = get_appdict(conf.app_interest_dir)
    interests = predictlist(appname, app_interest)
    return interests


def get_labels(interest):

    # Process categorical features
    le_fea = LabelEncoder().fit(list(set(interest)))
    print(list(le_fea.classes_))
    # ['健康', '其他', '娱乐', '旅游', '生活', '电影', '自拍']
    cat_to_num = le_fea.transform(interest)
    ohe_fea = OneHotEncoder(sparse=False).fit(cat_to_num.reshape(-1, 1))
    label = ohe_fea.transform(cat_to_num.reshape(-1, 1)).T.tolist()
    return label


def numeric_process(feature):
    # Process numeric features
    # Fill NA using 9999
    feature_fillna = [float(9999) if x in 'NULL' else float(x) for x in feature]
    return feature_fillna



def categorical_process(feature):
    # Process categorical features
    le_fea = LabelEncoder().fit(list(set(feature)))
    cat_to_num = le_fea.transform(feature)
    ohe_fea = OneHotEncoder(sparse=False).fit(cat_to_num.reshape(-1, 1))
    cat_fea = ohe_fea.transform(cat_to_num.reshape(-1, 1)).T.tolist()

    return cat_fea


def feature_transform(categorical_features,numeric_features):
    # Process numeric features
    feature_all = []
    for fea in numeric_features:
        fea = numeric_process(fea)
        feature_all.append(fea)
    # Process categorical features
    for cat_fea in categorical_features:
        cat_fea = categorical_process(cat_fea)
        feature_all += cat_fea
        print(len(feature_all))
    feature_all = np.array(feature_all).T
    return feature_all


if __name__ == '__main__':
    # data_train, data_test = get_data(conf.data_dir,conf.data_dir)
    data_train = get_data(conf.data_dir)
    userid,appname,cityid, provinceid, hour, devicetype, mobiletype, nettype = get_features(data_train)
    numeric_features = [hour]
    categorical_features = [cityid, provinceid, devicetype,mobiletype,nettype]
    print(set(cityid),set(provinceid),set(devicetype),set(hour),set(mobiletype),set(nettype))
    # feature transform
    Xtrain = feature_transform(categorical_features,numeric_features)

    # get label
    interest = get_interest(appname)
    Ytrain = get_labels(interest)
    print(len(Ytrain))

