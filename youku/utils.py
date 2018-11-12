#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/10 16:14
# @Author  : Yang Yuhan
import csv
from string import digits
import config as conf
import re

# 储存到text
def writer_to_text(user,matchlist,file):
    with open(conf.pwd_path + '/output/' +file,'w',encoding='utf-8') as f:
        for i in range(len(matchlist)):
            f.write(''.join(user[i]))
            f.write('\t')
            f.write(''.join([str(l) for l in matchlist[i]]))
            f.write('\n')
        f.close()


# 读取userID mediadata
def get_youkudata(file):
    '''
    :param app_csv: cols: [user_id, mediadata]
    :return:
    '''
    with open(file, 'r', errors='ignore') as f:
        mediadata = []
        userid = []
        for line in f:
            # 以','为分隔符，分割一次
            row = line.split(',', 1)
            info = row[1].strip('\n').strip('"')
            title_info = info.split('keyword')[0]
            if title_info != '{""title"":"""",""':
                mediadata.append(title_info)
                userid.append(row[0].strip())
    return mediadata[1:], userid[1:]


def get_data(file):
    """

    :param file:
    :return:
    """
    f = csv.reader(open(file,'r',errors='ignore'))
    name = []
    ages = []
    interests = []
    genders = []
    edu = []
    constellation = []
    for row in f:
        name.append(row[0])
        ages.append(row[2])
        interests.append(row[5])
        genders.append(row[1])
        edu.append(row[4])
        constellation.append(row[3])
    return name,ages,genders,interests,edu,constellation


def get_movielist(mediadata):
    movielist = []
    movie_raw = list(set(mediadata))
    for i in range(len(movie_raw)):
        try:
            title = movie_raw[i].replace('"','').replace('{title:','').strip()
            remove_digits = str.maketrans('', '', digits)
            title = title.translate(remove_digits).strip()
            title = re.split(r"[,\s]",title)
            title = [item for item in filter(lambda x:x != '',title)]
            movielist.append((movie_raw[i],title))
        except:
            pass
    return movielist


def get_match_output(file):
    with open(file,'r',encoding='utf-8') as f:
        userid = []
        movielist = []
        for line in f:
            items = line.strip('\n').split('\t')
            userid.append(items[0])
            movielist.append(items[1].strip(',').split(','))
    return movielist,userid

if __name__ == '__main__':
    get_data(conf.aiqiyi_dir)

