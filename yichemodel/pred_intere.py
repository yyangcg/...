#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 16:41
# @Author  : Yang Yuhan

from utils import get_appdict
from config import app_interest_dir
from collections import Counter


def counter(interests,num):
    '''
    interests : app对应的兴趣列表
    :param num: 选择出现频率最高的num个
    :return:
    '''
    preds = []
    tmp = Counter(interests).most_common(num)
    for ele in tmp:
        preds.append(ele[0])
    return preds



def predictlist(applist,appdict):

    interest = []
    for i in range(len(applist)):
        pred = appdict.get(applist[i],'其他')
        interest.append(pred)
    return interest



def predict(predlist,n):
    '''

    :param appdict: app对应的interest
    :param applist: app列表
    :param n: 预测兴趣top n
    :return:
    '''
    # interests = predictlist(applist,appdict)
    pred = counter(predlist, n)
    return pred


if __name__ == '__main__':
    appdict, _ = get_appdict(app_interest_dir)
    applist = ['汽车报价大全', '微信', 'QQ', 'others']
    predlist = predictlist(applist,appdict)
    pred = predict(predlist,3)
    print(pred)

