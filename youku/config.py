#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

pwd_path = os.path.abspath(os.path.dirname(__file__))
aiqiyi_dir = pwd_path + '/youkudata/aiqiyi_label.csv'
data_dir = pwd_path + '/youkudata/example.csv'
youku_dir = pwd_path + '/youkudata/interest_label.txt'

movie_dict = 'match_dict'
match_output = 'user_matched'
labelList = ['财经', '电影', '搞笑', '健康', '教育', '旅游', '美容', '母婴育儿', '女性', '汽车', '生活', '时尚', '体育', '音乐', '游戏', '娱乐', '资讯', '自拍', '科技']
