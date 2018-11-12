#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/29 10:23
# @Author  : Yang Yuhan
import json
from urllib.request import urlopen, quote
import pandas as pd


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
import time

def generate_allurl(user_in_nub,city):  # 生成url
    url = 'https://' + city + '.fang.lianjia.com/loupan/pg{}/'
    for url_next in range(1, int(user_in_nub)):
        yield url.format(url_next)


def get_page_num(re_get):
    res = requests.get(re_get)
    if res.status_code == 200:
        info = {}
        soup = BeautifulSoup(res.text,'lxml')
        info['标题'] = soup.select('.main')[0].text
        info['总价'] = soup.select('.total')[0].text + '万'
        info['每平方售价'] = soup.select('.unitPriceValue')[0].text
        return info

def get_allurl(generate_allurl):  # 分析url解析出每一页的详细url
    get_url = requests.get(generate_allurl)
    content = get_url.text
    urls = re.findall('<a href="/loupan/(.+?)" class="resblock-img-wrapper" title="',content)
    return urls


def open_url(re_get):  # 分析详细url获取所需信息  小区名称/经度/纬度/省/市/区/详细地理位置/每套房总价均价/面积/户型/该户型套数

    res = requests.get(re_get)
    content = res.text.replace('\xb2','').replace('\xa9','').replace('\ufeff', '').replace('\u2022','')
    district = re.findall('" data-xftrack="10152">(.+?)</a>',content)
    location = re.findall('<span class="label">售楼处地址：</span>\s{17}<span class="label-val">(.+?)</span>',content)
    lng = re.findall("parseFloat\('(.+?)'\),parseFloat", content)
    lat = re.findall(",parseFloat\('(.+?)'\)", content)
    title = re.findall('<p class="p1">(.+?) <span>', content)
    area = re.findall(' <span>建面 (.+?)</span>', content)
    if len(area) == 0:
        area = re.findall(' <span>套内 (.+?)</span>', content)
    number = re.findall('在售共 </span><span class="down">(.+?)</span><span class="wenzi-i"> 套</span>',content)
    price = re.findall('<p class="p2">均价 <span>(.+?)</span>',content)
    if len(price) == 0:
        price = ['']*len(title)
    detail = []
    for each in set(zip(title, area, price, number)):
        detail.append(each)
    return district, location,detail,lng,lat



def pandas_to_xlsx(info):  # 储存到xlsx
    pd_look = pd.DataFrame(info)
    pd_look.to_excel('链家二手房.xlsx', sheet_name='链家二手房')


def writer_to_text(list):  # 储存到text
    with open('链家新房.text', 'a', encoding='utf-8')as f:
        for i in list:
            f.write('\t'.join([str(l) for l in i]))
            f.write('\n')
        f.close()

def main():

    user_in_nub = input('输入生成页数：')
    city = input('输入城市：')
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    for i in generate_allurl(user_in_nub,city):
        print(i)
        urls = (get_allurl(i))

        for u in urls:
            results = []
            re_get = 'https://' + city + '.fang.lianjia.com/loupan/' + u
            district, location, detail, lng, lat = open_url(re_get)
            address = location[0]
            # address = str(district[2]).replace('楼盘','') + location[0]
            # if getlnglat(address).get('result',None) is not None:
            #     a = getlnglat(address).get('result',None).get('location','UNKNOWN')
            #     lng = a.get('lng','UNKNOWN')*1000000
            #     lat = a.get('lat','UNKNOWN')*1000000
            # else:
            #     lng = 'UNKNOWN'
            #     lat = 'UNKNOWN'
            # lng = 'UNKNOWN'
            # lat = 'UNKNOWN'
            source = '链家'
            for ele in detail:
                result = [district[4],lng[0],lat[0],str(district[2]).replace('楼盘',''), str(district[2]).replace('楼盘',''), str(district[3]).replace('楼盘',''),ele[0],str(ele[1]).replace('m',''),ele[2],source,'','',ele[3],address,create_time]
                results.append(result)
                print(result)
            # writer_to_text(results)    #储存到text文件



if __name__ == '__main__':
    main()
