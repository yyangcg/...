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


def get_interest(userid,appname):
    app_interest, app = get_appdict(conf.app_interest_dir)
    interests = predictlist(appname, app_interest)
    # 去重
    user_intere = list(zip(userid,interests))
    user_intere = list(set(user_intere))
    users = [user_intere[i][0] for i in range(len(user_intere))]
    interests = [user_intere[i][1] for i in range(len(user_intere))]
    print(interests)
    return users,interests


def get_user_label(userid, interest,label):
    '''

    :param userid_raw:
    :param appname_raw:
    :param label:
    :return:
    '''
    label_dict = {}
    for user in userid:
        label_dict[user] = 0
    for i in range(len(interest)):
        if interest[i] == label:
            label_dict[userid[i]] = 1
    return label_dict


# def get_labels(userid_raw,appname_raw):
#     userid, interest = get_interest(userid_raw, appname_raw)
#     # Process categorical features
#     le_fea = LabelEncoder().fit(['健康', '其他', '娱乐', '教育', '旅游', '汽车', '游戏', '生活', '电影', '自拍', '财经', '资讯', '音乐'])
#     # print(list(le_fea.classes_))
#     # ['健康', '其他', '娱乐', '教育', '旅游', '汽车', '游戏', '生活', '电影', '自拍', '财经', '资讯', '音乐']
#     cat_to_num = le_fea.transform(interest)
#     ohe_fea = OneHotEncoder(sparse=False).fit(cat_to_num.reshape(-1, 1))
#     label = ohe_fea.transform(cat_to_num.reshape(-1, 1)).T.tolist()
#     user_label = np.vstack((userid, label))
#
#     return user_label


def get_labels(userid,user_label):
    Y = []
    for i in range(len(userid)):
        label = user_label.get(userid[i])
        Y.append(label)
    return Y


def get_features(data):
    '''
    :param data:
    :return:
    '''
    userid = []
    cityid = []
    provinceid = []
    lau = []
    lou = []
    os = []
    acty_bn = []
    osv = []
    appname = []
    for row in data:
        userid.append(row[0])
        appname.append(row[1])
        cityid.append(str(row[3]))
        provinceid.append(str(row[4]))
        lau.append(row[6])
        lou.append(row[7])
        os.append(row[14])
        acty_bn.append(row[15] +','+ row[16])
        osv.append(str(row[17]))
    print(len(cityid))
    numeric_features = [lau,lou]
    categorical_features = [cityid,provinceid,os,acty_bn,osv]
    # numeric_features = [lau[1:],lou[1:]]
    # categorical_features = [cityid[1:],provinceid[1:],os[1:],acty_bn[1:],osv[1:]]
    # return userid[1:],appname[1:],numeric_features,categorical_features
    return userid,appname,numeric_features,categorical_features


def numeric_agg(userid,userid_raw,feature):
    '''
    一个user_id对应多条数据整合成一个user_id对应一条特征
    :param data:
    :return:
    '''
    value_min, value_max, value_mean = [None]*len(userid),[None]*len(userid),[None]*len(userid)
    for i in range(len(userid)):
        value_list = [feature[j] for j in range(len(userid_raw)) if userid_raw[j] == userid[i] ]
        value_min[i] = min(value_list)
        value_max[i] = max(value_list)
        value_mean[i] = sum(value_list)/len(value_list)
    return value_min,value_max,value_mean


def numeric_process(feature):
    # Process numeric features
    # Fill NA using 9999
    feature_fillna = [float(9999) if x in 'NULL' else float(x) for x in feature]
    return feature_fillna


def categorical_agg(userid,userid_raw,feature):
    '''
    一个user_id对应多条数据整合成一个user_id对应一条特征
    :param data:
    :return:
    '''
    value_sum = [None]*len(userid)
    # # 去重
    # user_fea = list(zip(userid_raw,feature))
    # user_fea = list(set(user_fea))
    # userid_raw = [user_fea[i][0] for i in range(len(user_fea))]
    # feature = np.array([user_fea[i][1] for i in range(len(user_fea))]).T
    feature = np.array(feature).T

    for i in range(len(userid)):
        value_list = [feature[j] for j in range(len(userid_raw)) if userid_raw[j] == userid[i]]
        value_sum[i] = np.sum(value_list,axis = 0)
    value = np.array(value_sum).T.tolist()

    return value


def categorical_process(userid,userid_raw,feature):
    # 去重
    user_fea = list(zip(userid_raw,feature))
    user_fea = list(set(user_fea))
    userid_raw = [user_fea[i][0] for i in range(len(user_fea))]
    feature = np.array([user_fea[i][1] for i in range(len(user_fea))]).T
    # user_fea = userid_raw+feature
    # user_fea = np.array(list(set([tuple(t) for t in userid_raw+feature])))

    # Process categorical features
    le_fea = LabelEncoder().fit(list(set(feature)))
    cat_to_num = le_fea.transform(feature)
    ohe_fea = OneHotEncoder(sparse=False).fit(cat_to_num.reshape(-1, 1))
    cat_fea = ohe_fea.transform(cat_to_num.reshape(-1, 1)).T.tolist()
    cat_fea = categorical_agg(userid, userid_raw, cat_fea)

    return cat_fea


def feature_transform(userid,userid_raw,categorical_features,numeric_features):
    # Process numeric features
    feature_all = []
    for fea in numeric_features:
        # fillna with 9999
        fea = numeric_process(fea)
        # feature aggregation
        fea = numeric_agg(userid,userid_raw,fea)
        feature_all += fea
    # Process categorical features
    for cat_fea in categorical_features:
        cat_fea = categorical_process(userid,userid_raw,cat_fea)
        feature_all += cat_fea
        print(len(feature_all))
    feature_all = np.array(feature_all).T
    return feature_all


if __name__ == '__main__':
    # data_train, data_test = get_data(conf.data_dir,conf.data_dir)
    data_train = get_data(conf.data_dir)
    # userid_raw,appname_raw,cityid_raw, provinceid_raw, lau_raw, lou_raw, os_raw, acty_bn_raw, osv_raw = get_features(data_train)
    # numeric_features = [lau_raw, lou_raw]
    # categorical_features = [cityid_raw, provinceid_raw, os_raw, acty_bn_raw, osv_raw]
    # print(set(cityid_raw), set(provinceid_raw), set(os_raw), set(lau_raw), set(lou_raw), set(osv_raw), set(acty_bn_raw))
    userid_raw,appname_raw,numeric_features,categorical_features = get_features(data_train)
    userid = list(set(userid_raw))
    # feature transform
    Xtrain = feature_transform(userid,userid_raw,categorical_features,numeric_features)

    # get label 去重
    userid, interest = get_interest(userid_raw, appname_raw)
    user_label = get_user_label(userid, interest,label= '母婴育儿')
    Ytrain = get_labels(userid,user_label)
    # print(Ytrain)
    print(len(Ytrain))
