#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/18 9:49
# @Author  : Yang Yuhan
iqiyi_tags = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '运动', '摄影', '汽车']
with open('E:\project\\201810\youku\youkudata\iqiyi.txt',encoding='utf-8') as f:
    tag = []
    for line in f:
        tmp = []
        items = line.split('\t')
        tmp.append(items[0])
        for i in range(len(iqiyi_tags)):
            tmp.append(eval(items[5]).get(iqiyi_tags[i]))
        tag.append(tmp)


# 储存到text
# def writer_to_text(user,matchlist,file):
#     with open(conf.pwd_path + '/output/' +file,'w',encoding='utf-8') as f:
#         for i in range(len(matchlist)):
#             f.write(''.join(user[i]))
#             f.write('\t')
#             f.write(''.join([str(l) for l in matchlist[i]]))
#             f.write('\n')
#         f.close()



with open('iqy.txt','w',encoding='utf-8') as f:
    for ele in tag:
        for j in range(len(ele)):
            a = ele[j]
            f.write(''.join(str(a)))
            f.write(',')
        f.write('\n')
    f.close()