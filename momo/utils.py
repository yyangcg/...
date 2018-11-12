#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config as conf
import re

# 储存到text
def writer_to_text(user,interest_list,file):
    with open(conf.pwd_path + '/output/' + file,'a',encoding='utf-8') as f:
        for i in range(len(interest_list)):
            f.write(''.join(user[i]))
            f.write('\t')
            f.write(''.join([str(l) for l in interest_list[i]]))
            f.write('\n')
        f.close()


# 读取momo数据
def get_momo_csv(file):
    '''

    :param app_csv: cols: [user_id, mediadata]
    :return:
    '''
    with open(file,'r',errors='ignore') as f:
        mediadata = []
        userid = []
        for line in f:
            # 以','为分隔符，分割一次
            row = line.split(',',1)
            info = re.findall('usertag(.*)ageMax', row[1])
            info = re.findall('100\d{2}', str(info))
            mediadata.append(info)
            userid.append(row[0].strip())
    return mediadata[1:],userid[1:]


# 根据momo兴趣获得对应的车慧兴趣
def predict(momolist,userid):
    '''
    '''
    interests = []
    userraw = []
    for i in range(len(momolist)):
        for ele in momolist[i]:
            userraw.append(userid[i])
            pred = conf.momo_dict.get(ele,None)
            interests.append(pred)
    return userraw,interests


# 生成0，1标签
def get_user_label(userid, user_intere,label):
    '''

    :param userid_raw:
    :param appname_raw:
    :param label:
    :return:
    '''
    label_dict = {}
    for user in userid:
        label_dict[user] = 0
    for i in range(len(user_intere)):
        if user_intere[i][1] == label:
            label_dict[user_intere[i][0]] = 1
    return label_dict

