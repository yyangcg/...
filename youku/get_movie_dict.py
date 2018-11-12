#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/24 16:03
# @Author  : Yang Yuhan
from utils import *
import difflib


# def movie_match(moviename,candidates):
#     suggestions = set()
#     pattern = '.*'.join(moviename)  # Converts 'djm' to 'd.*j.*m'
#     regex = re.compile(pattern)  # Compiles a regex.
#     for item in candidates:
#         match = regex.search(item)  # Checks if the current item matches the regex.
#         if match:
#             suggestions.add(item)
#         if item == moviename:
#             suggestions.add(item)
#
#     return suggestions

# 储存到text
def save_matchlist(matchlist,file):
    with open(conf.pwd_path + '/output/' +file,'w',encoding='utf-8') as f:
        for i in range(len(matchlist)):
            f.write(''.join([str(l) for l in matchlist[i][0]]))
            f.write('\t')
            f.write(''.join([str(l) for l in matchlist[i][1]]))
            f.write('\n')
        f.close()


def get_similat(a,b):
    seq = difflib.SequenceMatcher(None, a, b)
    ratio = seq.ratio()
    return ratio


def movie_match(moviename,candidates):
    similarity = []
    for i in range(len(candidates)):
        similarity.append(get_similat(candidates[i],moviename))
    if max(similarity) > 0.5:
        position = similarity.index(max(similarity))
        suggestion = candidates[position]
        return moviename,suggestion
    else:
        return moviename,None
    # return suggestion


def get_youku_movie(movielist,name):
    sugg = []
    movie_list = []
    for movie in movielist:
        similarity = []
        for i in range(len(name)):
            similarity.append(get_similat(name[i], movie))
        if max(similarity) > 0.5:
            position = similarity.index(max(similarity))
            suggestion = name[position]
            sugg.append(suggestion)
            movie_list.append(movie)
    return sugg,movie_list


def get_matchlist(outputfile):
    '''
    优酷title中和爱奇艺影片的匹配结果
    :param outputfile: 保存的文件名
    :return:
    '''
    # get user_id, mediadata
    mediadata,userid = get_youkudata(conf.data_dir)
    title_splitlist = get_movielist(mediadata)
    # 优化
    name, ages, genders, interests, edu, constellation = get_data(conf.aiqiyi_dir)
    matchlist = []
    for each in title_splitlist:
        title = each[0]
        matched_movie = set()
        for movie in each[1]:
            for i in range(len(name)):
                if movie in name[i] or name[i] in movie:
                    matched_movie.add(name[i])
        matchlist.append((title,matched_movie))
    save_matchlist(matchlist, outputfile)
    return matchlist,userid


def get_momviedict(file):
    with open(conf.pwd_path + '/output/' + file, 'r',encoding='utf-8',errors='ignore') as f:
        movie_dict = {}
        for line in f:
            items = line.strip('\n').split('\t')
            movie_dict[items[0]] = items[1].split(',')
    return movie_dict


if __name__ == '__main__':
    # 生成匹配的名称存入text
    get_matchlist(conf.movie_dict)