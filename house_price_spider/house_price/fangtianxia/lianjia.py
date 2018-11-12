#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/6/29 10:23
# @Author  : Yang Yuhan

from utils import generate_allurl,get_allurl,open_url,writer_to_text, get_price
import time
from city_list import get_province_dict, get_citycode_dict, get_district_code, get_city_list, get_city_page, get_city_dict, city_dict
from save_to_mysql import update_house_price_db,update_community_db
import pymysql



def get_city_house(user_in_nub,city):

    #创建时间
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    province_dict = get_province_dict()
    city_code_dict = get_citycode_dict()
    city_name_dict = city_dict()
    # 打开数据库连接
    db = pymysql.connect(host='172.20.206.28', port=3306, user='nanwei', password='nanwei', db='autodata-roomprice',
                         charset='utf8')
    cursor = db.cursor()

    # 生成城市url
    result_sum = []
    for i in generate_allurl(user_in_nub,city):
        print(i)
        # 楼盘，楼盘链接
        contents, urls = (get_allurl(i))

        # 对每个楼盘爬取数据
        for content in contents:

            results = []
            re_get = 'https://' + city + '.fang.lianjia.com/loupan/' + content[0]

            #数据来源
            source = '链家'
            # 楼盘名
            name = content[1]
            detail, longitude, latitude = open_url(re_get)
            city_name = list(city_name_dict.get(city))[0]
            province = list(province_dict.get(city_name,''))[0]
            district = content[2]
            city_code = city_code_dict.get(city_name,'')
            province_code = city_code_dict.get(province,'')
            district_code = get_district_code(city_name,district,city_code_dict)
            for ele in detail:
                try:
                    house_type = ele[0]
                    area = str(ele[1]).replace('m', '')
                    total_price = int(ele[2])*10000
                    count = ele[3]
                    result = [name, longitude, latitude, province, city_name, district, house_type, area, total_price, source, create_time, count]
                    results.append(result)
                except:
                    pass
            # writer_to_text(results)    #储存到text文件
            print(results)
            # update_house_price_db(db,cursor,results,table = '''house_price_yyh''')
            try:
                average, metre_average, area_average = get_price(results)
                result_sum.append([name, longitude, latitude, province, city_name, district, province_code, city_code, district_code,average, metre_average, area_average, create_time,source])
            except:
                pass
        # writer_to_text(result_sum)    #储存到text文件
    # update_community_db(db, cursor, result_sum, table='''community_yyh_tmp''')
    print(result_sum)
    # 关闭数据库连接
    db.close()


def get_data():
    cities,pages = get_city_dict()
    for i in range(len(cities)):
        user_in_nub = pages[i]
        city = cities[i]
        get_city_house(user_in_nub, city)

    # cities = get_city_list()
    # for i in range(len(cities)):
    #     city = cities[i]
    #     user_in_nub = get_city_page(city)
    #     get_city_house(user_in_nub, city)

if __name__ == '__main__':
    get_data()
