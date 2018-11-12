#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

pwd_path = os.path.abspath(os.path.dirname(__file__))

data_dir = pwd_path + '/momodata/20180719.csv'
labelList = ['财经', '电影', '搞笑', '健康', '教育', '旅游', '美容', '母婴育儿', '女性', '汽车', '生活', '时尚', '体育', '音乐', '游戏', '娱乐', '资讯', '自拍','科技']

# 生成陌陌兴趣和车慧兴趣对应字典
momo_dict = {
        '10001': '游戏',
        '10002': '汽车',
        '10003': '旅游',
        '10004': '生活',
        '10005': '娱乐',
        '10006': '体育',
        '10007': '电影',
        '10008': '时尚',
        '10009': '科技',
        '10010': '教育',
        '10011': '教育',
        '10012': '教育',
        '10013': '生活',
        '10014': '购物',
    }