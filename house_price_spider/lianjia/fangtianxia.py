#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/29 10:23
# @Author  : Yang Yuhan
from urllib.request import urlopen, quote
import numpy as np
import time
def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'vCGr7NmnhpUsgudEQi9o6k9VlPssBUox'

    add = quote(address) #由于本文城市变量为中文，为防止乱码，先用quote进行编码
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode() #将其他编码的字符串解码成unicode
    temp = json.loads(res) #对json数据进行解析
    # print(temp)
    return temp

import json
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from locale import *
setlocale(LC_NUMERIC, 'English_US')

def generate_allurl(user_in_nub,city):  # 生成url
    url = 'https://' + city + '.fang.anjuke.com/loupan/all/p{}/'
    for url_next in range(6, int(user_in_nub)):
        yield url.format(url_next)


def get_allurl(generate_allurl):  # 分析url解析出每一页的详细url
    get_url = requests.get(generate_allurl)
    content = get_url.text
    urls = re.findall('<a class="lp-name"\s\shref="(.+?)" soj',content)
    return urls


def open_url(re_get):  # 分析详细url获取所需信息  小区名称/经度/纬度/省/市/区/详细地理位置/每套房总价均价/面积/户型/该户型套数

    res = requests.get(re_get)
    content = res.text.replace('\xb2','').replace('\xa9','').replace('\ufeff', '').replace('\u2022','')
    district = re.findall('soj="loupan_index_crumb">(.+?)</a>',content)
    location = re.findall('<span class="lpAddr-text">(.+?)\s{20}</span>',content)
    title = re.findall('class="desc-v">(.+?)</span>', content)
    area = re.findall('class="desc-k area-k">建筑面积：约(.+?)m</span>', content)
    # number = re.findall('在售共 </span><span class="down">(.+?)</span><span class="wenzi-i"> 套</span>',content)
    number = ['']*len(title)
    price_avg = re.findall('<div class="price"><em>(.+?)</em>元/㎡</div>',content)
    if len(price_avg) == 0:
        price = ['']*len(title)
    else:
        try:
            price_avg = [float(i) for i in price_avg]
            area = [float(i) for i in area]
        except ValueError:
            price_avg = [float(atof(int(i))) for i in price_avg]
            area = [float(atof(int(i))) for i in area]
        price = [i*price_avg[0] for i in area]
    # print(price)
    detail = []
    for each in set(zip(title, area, price, number)):
        detail.append(each)
    return district, location,detail



def pandas_to_xlsx(info):  # 储存到xlsx
    pd_look = pd.DataFrame(info)
    pd_look.to_excel('链家二手房.xlsx', sheet_name='链家二手房')


def writer_to_text(list):  # 储存到text
    with open('安居客新房.text', 'a', encoding='utf-8')as f:
        for i in list:
            f.write('\t'.join([str(l) for l in i]))
            f.write('\n')
        f.close()


def main():

    user_in_nub = input('输入生成页数：')
    city = input('输入城市：')
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    # allurls = list(generate_allurl(user_in_nub,city))
    # allurls.append('https://' + city + '.fang.anjuke.com/loupan/all/')
    for i in generate_allurl(user_in_nub,city):
        print(i)
        urls = (get_allurl(i))
        for u in urls:
            results = []
            re_get = u
            district, location, detail = open_url(re_get)
            address = location[0]
            # address = str(district[2]).replace('楼盘','') + location[0]
            # if getlnglat(address).get('result',None) is not None:
            #     a = getlnglat(address).get('result',None).get('location','UNKNOWN')
            #     lng = a.get('lng','UNKNOWN')*1000000
            #     lat = a.get('lat','UNKNOWN')*1000000
            # else:
            #     lng = 'UNKNOWN'
            #     lat = 'UNKNOWN'
            lng = 'UNKNOWN'
            lat = 'UNKNOWN'
            source = '安居客'
            for ele in detail:
                result = [district[-1],lng,lat,str(district[1]).replace('楼盘',''), str(district[1]).replace('楼盘',''), str(district[2]).replace('楼盘',''),ele[0],str(ele[1]),ele[2],source,'','',ele[3],address,create_time]
                results.append(result)
                print(result)
            # writer_to_text(results)    #储存到text文件



if __name__ == '__main__':
    main()


    # print(atof('123,456'))  # 123456.0
