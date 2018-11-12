#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config as conf
from utils import get_youkudata
from get_movie_dict import get_momviedict

# 储存到text
def save_to_text(user,matchlist,file):
    with open(conf.pwd_path + '/output/' +file,'w',encoding='utf-8') as f:
        for i in range(len(matchlist)):
            f.write(''.join(user[i]))
            f.write('\t')
            f.write(','.join([str(l) for l in matchlist[i]]))
            f.write('\n')
        f.close()


def get_all_list(outputfile):
    # get user_id, mediadata
    mediadata,useridraw = get_youkudata(conf.data_dir)
    movie_dict = get_momviedict(conf.movie_dict)
    userid = list(set(useridraw))
    result = []
    match_movielist = [movie_dict.get(mediadata[i]) for i in range(len(mediadata))]
    if len(useridraw) > len(userid):
        for j in range(len(userid)):
            tmp = set()
            for i in range(len(useridraw)):
                if useridraw[i] == userid[j]:
                    for movie in match_movielist[i]:
                        tmp.add(movie)
            result.append(tmp)
        save_to_text(userid, result, outputfile)

    else:
        save_to_text(userid, match_movielist, outputfile)
    return match_movielist,userid

if __name__ == '__main__':
    # 生成匹配的名称存入text
    get_all_list(conf.match_output)


