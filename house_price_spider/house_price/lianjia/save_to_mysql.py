#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/27 16:02
# @Author  : Yang Yuhan
import time
import pymysql

# 创建数据库
def create_mysql_db():
    # 打开数据库连接
    db = pymysql.connect(host='172.20.206.28', port=3306, user='nanwei', password='nanwei', db='autodata-roomprice',
                         charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    # Relatively generic SQL DDL to create a table:
    create_table_sql = """CREATE TABLE IF NOT EXISTS house_price_yyh(`id` int(11) NOT NULL AUTO_INCREMENT,
    `name` varchar(500) DEFAULT NULL COMMENT '小区名称',
    `longitude` int(11) DEFAULT NULL,
    `latitude` int(11) DEFAULT NULL,
    `province_name` varchar(200) DEFAULT NULL COMMENT '省/直辖市名称',
    `city_name` varchar(200) DEFAULT NULL COMMENT '城市名称',
    `district_name` varchar(200) DEFAULT NULL COMMENT '区县名称',
    `house_type` varchar(64) DEFAULT NULL COMMENT '户型',
    `area` float DEFAULT NULL COMMENT '面积',
    `total_price` varchar(64) DEFAULT NULL COMMENT '总价',
    `source` varchar(32) DEFAULT NULL COMMENT '链家',
    `create_time` datetime DEFAULT NULL,
    `update_time` datetime DEFAULT NULL,
    `count` int(5) DEFAULT NULL COMMENT '该户型套数',
    PRIMARY KEY (`id`))ENGINE=InnoDB DEFAULT CHARSET=utf8"""

    cursor.execute(create_table_sql)

    # 关闭数据库连接
    db.close()


# 为house_price表 添加新的记录
def add_new_record_to_house_db(conn, sql_cursor, result, table):
    sql_cursor.execute('''INSERT INTO ''' + table + ''' (name, longitude, latitude, province_name, city_name, district_name, house_type, area, total_price, source, create_time,update_time,
    count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',result)
    # Make commitment to the above query
    # conn.commit()


# 为community表 添加新的记录
def add_new_record_to_community_db(conn, sql_cursor, result, table):
    sql_cursor.execute('''INSERT INTO ''' + table + ''' (name, longitude, latitude, province_name, city_name, district_name, province, city, district, average, metre_average, area_average, create_time,update_time, source
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ''',result)


# 更新house_price表
def update_house_price_db(db,cursor,results,table):
    for result in results:
        name = '"' + result[0] + '"'
        city = '"' + result[4] + '"'
        house_type = '"' + result[6] + '"'
        area ='"' + str(int(result[7])) + '"'
        source = '"' + result[9] + '"'
        sql = '''SELECT * FROM ''' + table + ''' WHERE name={0} and area={1} and city_name={2} and house_type={3} and source={4}'''.format(name,area,city,house_type,source)
        cursor.execute(sql)
        tmp = cursor.fetchall()
        # print(len(tmp))
        try:
            if len(tmp) == 0:
                add_new_record_to_house_db(db, cursor, result, table)
            else:
                # 更新house_price表中已存在的记录
                total_price = '"' + str(result[8]) + '"'
                update_time = '"' + result[10] + '"'
                count = '"' + str(result[12]) + '"'
                update_sql = '''UPDATE ''' + table + ''' SET total_price={0}, update_time={1}, count={2} WHERE name={3} and area={4} and city_name={5} and house_type={6} and source={7}'''.format(total_price,update_time,count,name, area, city, house_type,source)
                cursor.execute(update_sql)
        except:
            pass
    # Make commitment to the above query
    db.commit()


# 更新community表
def update_community_db(db,cursor, results,table):
    for result in results:
        name = '"' + result[0] + '"'
        city = '"' + result[4] + '"'
        area_average ='"' + str(int(result[11])) + '"'
        source = '"' + result[14] + '"'
        sql = '''SELECT * FROM ''' + table + ''' WHERE name={0} and area_average={1} and city_name={2} and source={3}'''.format(name,area_average,city,source)
        cursor.execute(sql)
        tmp = cursor.fetchall()
        # print(len(tmp))
        try:
            if len(tmp) == 0:
                add_new_record_to_community_db(db, cursor, result, table)
            else:
                # 更新community表中已存在的记录
                average = '"' + str(result[9]) + '"'
                update_time = '"' + result[12] + '"'
                metre_average = '"' + str(result[10]) + '"'
                update_sql = '''UPDATE ''' + table + ''' SET average={0}, update_time={1}, metre_average={2} WHERE name={3} and area_average={4} and city_name={5} and source={6}'''.format(
                    average, update_time, metre_average, name, area_average, city, source)
                cursor.execute(update_sql)
        except:
            pass
    # Make commitment to the above query
    db.commit()


if __name__ == '__main__':
    create_mysql_db()




