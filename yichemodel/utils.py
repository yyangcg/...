#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import csv
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


def get_appname(app_csv):
    '''

    :param app_csv:
    :return:
    '''
    with open(app_csv,'r',errors='ignore') as f:

        appname = []
        userid = []
        for line in f:
            row = line.split(',')
            try:
                appname.append(row[conf.app_col].strip())
                userid.append(row[conf.user_col].strip())
            except:
                pass
    return appname[1:],userid[1:]



def get_appdict(app_txt):
    app_interest = dict()
    # interest_app = dict()
    app = []
    with open(app_txt,'r',encoding='utf-8-sig',errors='ignore') as f:
        for line in f :
            try:
                row = line.strip('\n').split('\t')
                app_interest[row[0]] = row[1]
                app.append(row[0])
            except:
                pass
    return app_interest,app






if __name__ == '__main__':
    get_appdict(conf.app_interest_dir)
    # percentage('app2500.csv')


 
