#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/24 17:41
# @Author  : Yang Yuhan
# from urllib import parse
# import hashlib
# def get_urt(addtress):
#  # 以get请求为例http://api.map.baidu.com/geocoder/v2/?address=百度大厦&output=json&ak=你的ak
#  queryStr = '/geocoder/v2/?address=%s&output=json&ak=你的ak' % addtress
#  # 对queryStr进行转码，safe内的保留字符不转换
#  encodedStr = parse.quote(queryStr, safe="/:=&?#+!$,;'@()*[]")
#  # 在最后直接追加上yoursk
#  rawStr = encodedStr + '你的sk'
#  #计算sn
#  sn = (hashlib.md5(parse.quote_plus(rawStr).encode("utf8")).hexdigest())
#  #由于URL里面含有中文，所以需要用parse.quote进行处理，然后返回最终可调用的url
#  url = parse.quote("http://api.map.baidu.com"+queryStr+"&sn="+sn, safe="/:=&?#+!$,;'@()*[]")
#  return url

import json
from urllib.request import urlopen, quote
import pandas as pd


def getlnglat(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'b2VqPcmMq1TlofkHbp1QanVhwxLWVTuY'

    add = quote(address) #由于本文城市变量为中文，为防止乱码，先用quote进行编码
    uri = url + '?' + 'address=' + add  + '&output=' + output + '&ak=' + ak
    req = urlopen(uri)
    res = req.read().decode() #将其他编码的字符串解码成unicode
    temp = json.loads(res) #对json数据进行解析
    # print(temp)
    return temp


if __name__ == '__main__':

    # df = pd.read_csv('house_price.csv',encoding='gbk')
    # addressList = df['location']
    # df.lng = pd.DataFrame()
    # df.lat = pd.DataFrame()
    # print(addressList[0])
    # for i in range(len(addressList)):
    #     address = addressList[i]
    address = ' 王佐镇长青路南侧'
    print(getlnglat(address))
    a = getlnglat(address).get('result').get('location')
    # df.lng[i] = int(a.get('lng'))
    # df.lat[i] = int(a.get('lat'))
    print(a.get('lng')*1000000,a.get('lat')*1000000)
    # df.to_csv('new.csv',encoding='utf-8')