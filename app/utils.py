#!/usr/bin/env python
# -*- coding: utf-8 -*-
import config as conf

# 储存到text
def writer_to_text(user,interest_list,file):
    with open(conf.pwd_path + '/output/' + file,'a',encoding='utf-8') as f:
        for i in interest_list:
            f.write(''.join(user))
            f.write('\t')
            f.write(''.join([str(l) for l in i]))
            f.write('\n')
        f.close()


# 读取app装机列表数据
def get_app_csv(file):
    '''

    :param app_csv: cols: [user_id, mediadata]
    :return:
    '''
    with open(file,'r',errors='ignore') as f:
        apps = []
        userid = []
        for line in f:
            # 以','为分隔符，分割一次
            row = line.split(',',1)
            apps.append(row[1].strip('\n'))
            userid.append(row[0].strip())
    return apps[1:],userid[1:]


# 读取app对应的兴趣
def get_appdict(app_txt):
    app_interest = dict()
    with open(app_txt,'r',encoding='utf-8-sig',errors='ignore') as f:
        for line in f :
            try:
                row = line.strip('\n').split('\t')
                app_interest[row[0]] = row[1]
            except:
                pass
    return app_interest


def get_interest(userid,appname):
    app_interest = get_appdict(conf.app_interest_dir)
    interests = [app_interest.get(appname[i],'None') for i in range(len(appname))]
    # 去重
    user_intere = list(set(zip(userid,interests)))
    return user_intere


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


if __name__ == '__main__':
    get_appdict(conf.app_interest_dir)


 
