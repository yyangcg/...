#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/6 14:20
# @Author  : Yang Yuhan
import pymysql
from save_to_mysql import update_community_db
# from utils import get_price
from city_list import get_citycode_dict,get_district_code,get_province_dict
import time
# 计算 average,metre_average,area_average
def get_price(results):
    # 小区所有房子总价
    p = 0
    # 小区房子套数
    num = 0
    # 小区所有房子总面积
    a = 0
    for result in results:
        p += int(result[13])*int(result[9])*10000
        num += int(result[13])
        a += int(result[8])*int(result[13])

    # 每平米均价
    metre_average = int(p/a)
    # 总价均价
    average = int(p/num)
    # 每套房平均面积
    area_average = int(a/num)

    return average,metre_average,area_average


# def get_province_dict():
#     province_dict = dict(北京={'北京市'}, 上海={'上海市'}, 广州={'广东省'}, 天津={'天津市'}, 重庆={'重庆市'}, 沈阳={'辽宁省'}, 石家庄={'河北省'},
#                          西安={'陕西省'}, 郑州={'河南省'}, 济南={'山东省'}, 太原={'山西省'}, 合肥={'安徽省'}, 武汉={'湖北省'}, 长沙={'湖南省'},
#                          南京={'江苏省'},
#                          成都={'四川省'}, 昆明={'云南省'}, 杭州={'浙江省'}, 哈尔滨={'黑龙江省'}, 长春={'吉林省'}, 呼和浩特={'内蒙古自治区'},
#                          乌鲁木齐={'新疆维吾尔自治区'}, 兰州={'甘肃省'}, 西宁={'青海省'}, 银川={'宁夏回族自治区'}, 贵阳={'贵州省'}, 南宁={'广西壮族自治区'},
#                          拉萨={'西藏自治区'}, 南昌={'江西省'}, 福州={'福建省'}, 海口={'海南省'}, 台北={'台湾省'}, 香港={'香港特别行政区'},
#                          澳门={'澳门特别行政区'})
#     return province_dict


def get_namelist(table,cursor):
    # 建立sql语句
    sql = '''SELECT city_name,name FROM ''' + table + ''' WHERE source='房天下' '''
    # 执行sql语句
    cursor.execute(sql)
    # 只取出一条满足条件的数据结果
    namelist = set(cursor.fetchall())  # 也可以用cursor.fetchall()取出所有满足条件的数据结果
    return namelist


def cal_ftx(table = '''house_price''',source_name='房天下'):
    create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    update_time = None
    city_code_dict = get_citycode_dict()
    province_dict = get_province_dict()
    db = pymysql.connect(host='172.20.206.28', port=3306, user='nanwei', password='nanwei', db='autodata-roomprice',
                         charset='utf8')

    with db.cursor() as cursor:
        namelist = get_namelist(table,cursor)
        # print(list(namelist)[0])
        result_sum = []
        source = '"' + source_name + '"'
        for ele in namelist:
            city_name = '"' + ele[0] + '"'
            name = '"' + ele[1] + '"'
            # 建立sql语句
            sql = '''SELECT * FROM ''' + table + ''' WHERE source={2} and city_name={0} and name={1} '''.format(city_name,name,source)
            # 执行sql语句
            cursor.execute(sql)
            # 只取出一条满足条件的数据结果
            results = list(set(cursor.fetchall()))  # 也可以用cursor.fetchall()取出所有满足条件的数据结果
            longitude = results[0][2]
            latitude = results[0][3]
            city = results[0][5] + '市'
            province = list(province_dict.get(city,''))[0]
            district = results[0][6]
            province_code = city_code_dict.get(province,'')
            city_code = city_code_dict.get(city,'')
            district_code, district = get_district_code(city,district,city_code_dict)
            average, metre_average, area_average = get_price(results)
            result_sum.append([ele[1], longitude, latitude, province, ele[0], district, province_code, city_code, district_code, average,metre_average, area_average, create_time, update_time, source_name])
        print(len(result_sum))
        # update_community_db(db, cursor, result_sum, '''community_yyh''')
        try:
            update_community_db(db, cursor, result_sum, '''community''')
        except:
            pass


    db.close()

if __name__ == '__main__':
    cal_ftx()