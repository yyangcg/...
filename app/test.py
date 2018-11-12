#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 17:37
# @Author  : Yang Yuhan

from utils import *
import config as conf
import pandas as pd


def test(labelList):
    # read user_id, applist
    applist,useridraw = get_app_csv(conf.data_dir)
    # get interest from applist
    user_intere = get_interest(useridraw,applist)
    label_all = []
    # create user_id, interests table
    df = pd.DataFrame()
    userid = list(set(useridraw))
    df['user_id'] = userid
    for label in labelList:
        user_label = get_user_label(userid, user_intere,label)
        Y = [user_label.get(userid[i]) for i in range(len(userid))]
        label_all.append(Y)
        df[label] = Y
    df.to_csv(conf.pwd_path + '/output/pred_interest11.csv', encoding='utf-8',index=False)


if __name__ == '__main__':
    test(conf.labelList)



