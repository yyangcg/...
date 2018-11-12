#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/27 9:18
# @Author  : Yang Yuhan

import requests
import re
import json
from urllib.request import urlopen, quote
import pandas as pd
import time


# 百度地图API获取经纬度
def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'vCGr7NmnhpUsgudEQi9o6k9VlPssBUox'
    add = quote(address) #由于本文城市变量为中文，为防止乱码，先用quote进行编码
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode() #将其他编码的字符串解码成unicode
    temp = json.loads(res) #对json数据进行解析
    return temp


 # 生成每个城市 url list
def generate_allurl(user_in_nub,city):
    url = 'https://' + city + '.fang.anjuke.com/loupan/all/p{}/'
    for url_next in range(1, int(user_in_nub)):
        yield url.format(url_next)


# 分析url解析出每一页的详细url  :   loupan list
def get_allurl(generate_allurl):  # 分析url解析出每一页的详细url
    get_url = requests.get(generate_allurl)
    content = get_url.text
    # 楼盘url
    urls = re.findall('<a class="lp-name"\s\shref="(.+?)" soj',content)
    # 楼盘名称
    names = re.findall('<h3><span class="items-name">(.+?)</span></h3>',content)
    # 区
    resblock_location = re.findall('<span class="list-map" target="_blank">\[&nbsp;(.+?)&nbsp;]', content)
    district = [ele.split('&nbsp;')[0] for ele in resblock_location]
    details = []
    for each in set(zip(urls, names, district)):
        details.append(each)
    return details , urls


# 分析详细url获取所需信息  小区名称/经度/纬度/详细地理位置/每套房总价/均价/面积/户型/该户型套数
def open_url(re_get):

    res = requests.get(re_get)
    content = res.text.replace('\xb2','').replace('\xa9','').replace('\ufeff', '').replace('\u2022','')

    # 经纬度
    lng = re.findall(", lng:(.+?)}", content)
    lat = re.findall("lat: (.+?),", content)
    longitude = float(lng[0]) * 1000000
    latitude = float(lat[0]) * 1000000

    # 户型
    house_type = re.findall('class="desc-v">(.+?)</span>', content)

    #面积
    area = re.findall('class="desc-k area-k">建筑面积：约(.+?)m</span>', content)

    # 户型套数
    number = ['']*len(house_type)
    # number = re.findall('在售共 </span><span class="down">(.+?)</span><span class="wenzi-i"> 套</span>',content)

    #户型总价
    price_url = re_get + '/' + re.findall('soj="(.+?)">',content)[0]
    print(price_url)
    price = re.findall('<p class="p2">均价 <span>(.+?)</span>',content)
    if len(price) == 0:
        price = [0]*len(house_type)

    detail = []
    for each in set(zip(house_type, area, price, number)):
        detail.append(each)
    return detail, longitude, latitude


# 储存到xlsx
def pandas_to_xlsx(info):
    pd_look = pd.DataFrame(info)
    pd_look.to_excel('链家二手房.xlsx', sheet_name='链家二手房')


# 储存到text
def writer_to_text(list):
    with open('链家新房.text', 'a', encoding='utf-8')as f:
        for i in list:
            f.write('\t'.join([str(l) for l in i]))
            f.write('\n')
        f.close()


# 计算 average,metre_average,area_average
def get_price(results):
    # 小区所有房子总价
    p = 0
    # 小区房子套数
    num = 0
    # 小区所有房子总面积
    a = 0
    for result in results:
        p += int(result[11])*int(result[8])
        num += int(result[11])
        a += int(result[7])*int(result[11])

    # 每平米均价
    metre_average = int(p/a)
    # 总价均价
    average = int(p/num)
    # 每套房平均面积
    area_average = int(a/num)

    return average,metre_average,area_average


