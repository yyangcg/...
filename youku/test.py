#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 17:53
# @Author  : Yang Yuhan
from predict import *
from utils import get_match_output
from preprocessing import *
import pandas as pd

def pred_labels(match_output):
    matchlist,userid = get_match_output(match_output)
    name, age, gender, interests, edu, constellation = get_data(conf.aiqiyi_dir)
    genderList = ['男','女']
    ageList = ['1-17', '18-24', '25-30', '31-35', '36-40', '40+']
    eduList = ['小学', '初中', '高中-中专', '大专', '本科', '硕士以上']
    constellationList = ['白羊座', '金牛座', '双子座', '巨蟹座', '狮子座', '处女座', '天秤座', '天蝎座', '射手座', '摩羯座', '水瓶座', '双鱼座']
    labelList = [(gender,genderList,'gender'),(age,ageList,'age'),(edu,eduList,'edu'),(constellation,constellationList,'constellation')]

    name_toidx, idx_toname = name_index(name)
    result = [userid]
    df = pd.DataFrame()
    df['user_id'] = userid
    for each in labelList:
        pred = []
        pct = get_label_pct(name, each[0])
        for i in range(len(matchlist)):
            idx_list = [name_toidx.get(i) for i in matchlist[i]]
            cnt = cal_cnt(idx_list, len(name))
            if np.sum(cnt) != 0:
                label = get_label(cnt,pct,each[1],1)
                pred.append(list(label)[0])
            else:
                label = None
                pred.append(label)
        df[each[2]] = pred
        print(pred)
        result.append(pred)
    df.to_csv(conf.pwd_path + '/output/pred_info.csv', encoding='utf-8',index=False)

    print(result)


def pred_interest(match_output):
    matchlist,useridraw = get_match_output(match_output)
    name, age, gender, interests, edu, constellation = get_data(conf.aiqiyi_dir)
    interestlist = ['娱乐', '科技', '购物', '生活', '商务', '时尚', '旅行', '游戏', '财经', '生活', '体育', '自拍', '汽车']
    name_toidx, idx_toname = name_index(name)
    pred = []
    pct = get_label_pct(name, interests)
    for i in range(len(matchlist)):
        idx_list = [name_toidx.get(ele) for ele in matchlist[i]]
        cnt = cal_cnt(idx_list, len(name))
        if np.sum(cnt) != 0:
            label = get_label(cnt,pct,interestlist,2)
        else:
            label = None
        pred.append(label)
    # 去重
    # label_all = []
    df = pd.DataFrame()
    userid = list(set(useridraw))
    df['user_id'] = userid
    for label in conf.labelList:
        user_label = get_user_label(userid, pred,label)
        # label_all.append(user_label)
        df[label] = user_label
    df.to_csv(conf.pwd_path + '/output/pred_interest11.csv', encoding='utf-8',index=False)


def get_user_label(userid, pred,label):
    '''
    :param userid_raw:
    :param label:
    :return:
    '''
    label_pred = [0]*len(userid)
    for i in range(len(pred)):
        try:
            if label in pred[i]:
                label_pred[i] = 1
        except:
            pass
    return label_pred


#
# def predBykeywords(file):
#     mediadata,userid = get_youkudata(conf.data_dir)
#     wordlist = get_key(mediadata)
#     youku_key_interest = youku_dict()
#     print(wordlist,userid)
#     interests = []
#     for i in range(len(userid)):
#         interest = set()
#         for word in wordlist[i]:
#             tmp = youku_key_interest.get(word,'其他')
#             interest.add(tmp)
#         interests.append(list(interest))
#     print(interests)
#     return userid,interests


if __name__ == '__main__':

    # pred_interest(conf.pwd_path + '/output/' + conf.match_output)
    pred_labels(conf.pwd_path + '/output/' + conf.match_output)
