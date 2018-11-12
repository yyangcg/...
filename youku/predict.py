#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import config as conf
from utils import get_data

def cal_cnt(idx_list,row_num):
    """
    :param namelist: 观看记录
    :return: 每个观看记录的次数
    """
    cnt = np.zeros((row_num,1))
    for i in idx_list:
        if i != None:
            cnt[i] += 1
    return cnt


def name_index(name):
    name_toidx = dict()
    idx_toname = dict()
    for i in range(len(name)):
        name_toidx[name[i]] = i
        idx_toname[i] = name[i]
    return name_toidx, idx_toname


def get_label_pct(name,label):
    '''
    每个影片的label的每个值对应的占比
    :param name:
    :param label: name, ages, genders, interests, edu, constellation
    :return:
    ages: ['1-17', '18-24', '25-30', '31-35', '36-40', '40+']
    genders: [ '帅哥','美女']
    interests: [ '追星族', '数码达人', '网购达人', '美食达人', '商务人士', '时尚达人', '旅行达人', '游戏达人', '理财达人', '家庭主妇', '运动达人', '摄影达人', '玩车一族']
    edu: [ '小学', '初中', '高中-中专', '大专', '本科', '硕士以上']
    constellation: [ '白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
    '''
    data = []
    for i in range(len(name)):
        items = label[i].split(',')
        percentages = []
        for item in items:
            per = item.split(':')[1].strip().strip('}')
            try:
                percentages.append(float(per))
            except:
                percentages.append(0)
        data.append(percentages)
    pct = np.array(data).T
    return pct


def cal_label(cnt,pct):
    '''
    计算label每个值的分数
    cnt ：观看次数矩阵 [影片总个数 * 1]
    pct ：label值分布矩阵 [label值个数 * 影片总个数]
    score ：label值分数矩阵 = pct * cnt = [label值个数 * 1]
    :param namelist:
    :param label:
    :return:
    '''
    tmp = pct.dot(cnt)
    score = tmp/sum(tmp)
    return score


def get_label(cnt,pct,labelList,n):
    '''
    预测年龄、性别、星座、学历
    :param score:
    :return: 兴趣分值最高的n个兴趣
    '''

    score = cal_label(cnt.astype('float64'),pct.astype('float64'))
    score = score.tolist()
    n_top = sorted(range(len(score)), key=lambda i: score[i], reverse=True)[:n]
    labels= set(labelList[index] for index in n_top)
    return labels


if __name__ == '__main__':
    name, age, gender, interests, edu, constellation = get_data(conf.aiqiyi_dir)
    genderList = ['男','女']
    ageList = ['1-17', '18-24', '25-30', '31-35', '36-40', '40+']
    eduList = ['小学', '初中', '高中-中专', '大专', '本科', '硕士以上']
    constellationList = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
    labelList = [(gender,genderList),(age,ageList),(edu,eduList),(constellation,constellationList)]

    name_toidx, idx_toname = name_index(name)

    namelist = ['热血狂篮', '亲爱的活祖宗', '芈月传奇番外篇之邪恶游戏', '热血狂篮', 'others']
    namelists = [namelist,namelist]
    for each in labelList:
        pct = get_label_pct(name, each[0])
        for namelist in namelists:
            idx_list = [name_toidx.get(i) for i in namelist]
            cnt = cal_cnt(idx_list, len(name))
            if np.sum(cnt) != 0:
                label = get_label(cnt,pct,each[1])
                print(label)
            else:
                label = None