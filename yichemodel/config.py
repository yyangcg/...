#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 17:37
# @Author  : Yang Yuhan
import os

pwd_path = os.path.abspath(os.path.dirname(__file__))
app_interest_dir = pwd_path + '/appdata/app_interest.txt'
# data_dir = pwd_path + '/appdata/example.csv'

# file = 'results.csv'
file = '07_08.csv'
data_raw_dir = pwd_path + '/appdata/'+file
data_dir = pwd_path + '/appdata/data_raw.csv'
Xtrainfile = pwd_path + '/appdata/data/data_train.txt'
Ytrainfile = pwd_path + '/appdata/data/'

labelList = ['财经', '电影', '搞笑', '健康', '教育', '旅游', '美容', '母婴育儿', '女性', '汽车', '生活', '时尚', '体育', '音乐', '游戏', '娱乐', '资讯', '自拍']
user_col = 0
app_col = 1