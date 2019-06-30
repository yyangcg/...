# -*- coding:utf-8 -*-
"""
Created on 2017/8/21

@author: kongyangyang
"""

import pymysql
from pymongo import *


class MysqlClient(object):
    def __init__(self, param):
        self.param = param
        self.conn = self.connect(param)
        self.insert_id = None

    @staticmethod
    def connect(param):
        if "port" not in param:
            param['port'] = 3306
        return pymysql.connect(cursorclass=pymysql.cursors.DictCursor, **param)

    def close(self):
        self.conn.close()

    def query(self, sql):
        if self.conn is None:
            cursor = self.conn.cursor()
            cursor.execute('set names utf8')
            cursor.execute(sql)
            self.insert_id = cursor.lastrowid
            cursor.close()
        return False

    def check_table_exists(self, tablename):
        sql = "SELECT COUNT(*) as c FROM information_schema.TABLES WHERE TABLE_SCHEMA='{dbname}' and TABLE_NAME='{tablename}'".format(
            dbname=self.param["db"], tablename=tablename)
        cursor = self.conn.cursor()
        cursor.execute('set names utf8')
        cursor.execute(sql)
        res = cursor.fetchone()
        cursor.close()
        if res['c'] > 0:
            return True
        return False

    def get_results(self, sql):
        if self.conn is not None:
            try:
                cursor = self.conn.cursor()
                cursor.execute('set names utf8')
                cursor.execute(sql)
            except(AttributeError, pymysql.OperationalError):
                self.connect(self.param)
                cursor = self.conn.cursor()
                cursor.execute('set names utf8')
                cursor.execute(sql)

            res = cursor.fetchall()
            cursor.close()
            return res
        return False

    @staticmethod
    def check_value(value):
        if isinstance(value, dict):
            first = False
            sql = ''
            for k, v in value.items():
                if first:
                    sql += ' , '
                else:
                    first = True
                if isinstance(v, str):
                    v = pymysql.escape_string(v)
                if v is None:
                    sql += "%s = null" % k
                else:
                    sql += "%s = '%s'" % (k, v)
            return sql
        else:
            return value

    @staticmethod
    def check_condition(condition):
        if isinstance(condition, dict):
            first = False
            sql = ''
            for k, v in condition.items():
                if first:
                    sql += ' AND '
                else:
                    first = True
                sql += "%s = '%s'" % (k, v)
            return sql
        else:
            return condition

    def get_var_by_condition(self, table, condition, var):
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute('set names utf8')
            condition = self.check_condition(condition)
            sql = "SELECT %s FROM %s" % (var, table)
            if condition is not None:
                sql += " WHERE " + condition
            cursor.execute(sql)
            res = cursor.fetchone()
            cursor.close()
            return res[var]
        return False

    def insert_into_table(self, tablename, values):
        if self.conn is not None:
            if isinstance(values, dict):
                values = [values]
            sql = ''
            for v in values:
                if sql == '':
                    sql = 'INSERT INTO ' + tablename + ' (' + ','.join(v.keys()) + ')' + ' VALUES '
                else:
                    sql += ','
                sql += ' ('
                start = True
                for res in v.values():
                    if start:
                        start = False
                    else:
                        sql += ','
                    sql += "'%s'" % res
                sql += ') '

            try:
                cursor = self.conn.cursor()
                cursor.execute('set names utf8')
                cursor.execute(sql)
            except(AttributeError, pymysql.OperationalError):
                self.connect(self.param)
                cursor = self.conn.cursor()
                cursor.execute('set names utf8')
                cursor.execute(sql)

            self.insert_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
        return False

    def update_by_condition(self, table, value, condition):
        condition = self.check_condition(condition)
        value = self.check_value(value)
        cursor = self.conn.cursor()
        sql = 'UPDATE %s SET %s' % (table, value)
        if condition is not None and condition != '':
            sql += ' WHERE ' + condition
        cursor.execute('set names utf8')
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()

    def get_count_by_condition(self, table, condition=''):
        cursor = self.conn.cursor()
        condition = self.check_condition(condition)
        sql = 'SELECT count(*) as c FROM %s' % table
        if condition is not None and condition != '':
            sql += " WHERE " + condition
        cursor.execute('set names utf8')
        cursor.execute(sql)
        res = cursor.fetchone()
        cursor.close()
        return res['c']

    @staticmethod
    def check_var(var):
        if isinstance(var, list):
            var = ','.join(var)
        else:
            return var
        return var

    def get_row_by_condition(self, table, var, condition):
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute('set names utf8')
            condition = self.check_condition(condition)
            sql = "SELECT %s FROM %s" % (self.check_var(var), table)
            if condition is not None and condition != '':
                sql += " WHERE " + condition
            cursor.execute(sql)

            res = cursor.fetchone()
            cursor.close()
            return res
        return False

    def get_rows_by_condition(self, table, var, condition):
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute('set names utf8')
            condition = self.check_condition(condition)
            sql = "SELECT %s FROM %s" % (self.check_var(var), table)
            if condition is not None and condition != '':
                sql += " WHERE " + condition
            cursor.execute(sql)
            res = cursor.fetchall()
            cursor.close()
            return res
        return False

    def get_insert_id(self):
        return self.insert_id

    def create_table(self, table_structure):
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute('set names utf8')
            cursor.execute(table_structure)
            self.conn.commit()
            cursor.close()

    def drop_table(self, table_name):
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute("drop table if EXISTS {table_name}".format(table_name=table_name))
            self.conn.commit()
            cursor.close()

    def execute_sql(self, sql):
        """
        :param sql:
        :return:
        """
        if self.conn is not None:
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()


class MyMongoClient(object):
    def __init__(self, param={}):
        self.connect(param)

    def connect(self, param):
        # 建立连接
        if "port" not in param:
            param['port'] = 27017
        if "ip" not in param:
            param['host'] = "172.16.224.82"
        self.client = MongoClient(param['host'], param['port'])
        # self.client = MongoClient('172.21.0.250:27017,172.21.0.249:27017,172.21.0.251:27017')

    def insert(self, dbname, collectioname, values):
        # {"word":word,"releventwords":wvlist}
        self.client[dbname][collectioname].insert(values)

    def remove(self, dbname, collectioname, condition):
        self.client[dbname][collectioname].remove(condition)

    def getResultByCondition(self, dbname, collectionname, condition, values):
        # condition = {'crawl_time':{'$gte':startstamp,"$lte":stopstamp}
        rsts = self.client[dbname][collectionname].find(condition, values)

        return rsts

    def updateByCondition(self, dbname, collectionname, condition, objNew):
        ''' 参数说明：
        criteria：查询条件
        objNew：update对象和一些更新操作符
        upsert：如果不存在update的记录，是否插入objNew这个新的文档，true为插入，默认为false，不插入。
        '''
        criteria = condition['criteria']
        upsert = condition['upsert']
        multi = condition['multi']

        self.client[dbname][collectionname].update(criteria, objNew, upsert, multi)
