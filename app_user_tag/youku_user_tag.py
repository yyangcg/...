#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/16 11:05
# @Author  : Yang Yuhan

from pip._vendor.pyparsing import col
from pyspark.shell import sc

sc.setLogLevel("ERROR")
from pyspark.sql.functions import *
from pyspark import StorageLevel
from pyspark.sql import Row
from pyspark.sql import HiveContext
import time
from pyspark.sql.functions import StringType
from pyspark.sql.functions import udf
import json


def translate(tag):
    def translate_(col):
        data = json.loads(col)
        return data.get(tag)
    return udf(translate_, StringType())


def iqiyi2tag(data_path,iqiyi_tags):
    iqiyi2tag_df = sc.textFile(data_path).map(lambda x: Row(iqiyi=x)).toDF()
    iqiyi2tag_df = iqiyi2tag_df.withColumn('movie', split(iqiyi2tag_df['iqiyi'], ',').getItem(0))
    for i in range(len(iqiyi_tags)):
        iqiyi2tag_df = iqiyi2tag_df.withColumn(iqiyi_tags[i], split(iqiyi2tag_df['iqiyi'], ',').getItem(i + 1))
    iqiyi2tag_df = iqiyi2tag_df.drop('iqiyi')
    iqy_movies = sc.textFile(data_path).map(lambda x: Row(iqiyi=x.split(",")[0])).collect()
    iqy = [item[0] for item in iqy_movies]
    tag_list = ['美容', '母婴育儿', '电影', '搞笑',
                '健康', '教育', '音乐', '资讯']
    for tag in tag_list:
        iqiyi2tag_df = iqiyi2tag_df.withColumn(tag, lit(0)).persist(StorageLevel.DISK_ONLY)
    return iqiyi2tag_df, iqy


def find(x,iqy):
    movie = ''
    for ele in iqy:
        if ele in x:
            movie = ele
            break
        else:
            continue
    return movie


def match_all_df(data_path):
    sqlContext = HiveContext(sc)
    sqlContext.sql("use usercenter_dw")
    df = sqlContext.sql("select * from youku_mediadata")
    df = df.withColumn("yk_movie", translate('title')("mediadata")).filter(col('yk_movie') != '').withColumn('movie', lit('')).persist(StorageLevel.DISK_ONLY)
    iqiyi_tags = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车']
    iqiyi2tag_df, iqy = iqiyi2tag(data_path, iqiyi_tags)
    for ele in iqy:
        df1 = df.withColumn('movie', when(col('yk_movie').like('%' + ele + '%'), ele).otherwise(col('movie'))).filter(col('movie') != '').select('mediadata','movie')
        df = df.withColumn('movie', when(col('yk_movie').like('%' + ele + '%'), ele).otherwise(col('movie'))).filter(col('movie') == '').persist(StorageLevel.DISK_ONLY)
        df1.registerTempTable('tab_name')
        sqlContext.sql("insert into table youku_iqy select * from tab_name ")



def match_all(data_path):
    sqlContext = HiveContext(sc)
    sqlContext.sql("use usercenter_dw")
    df = sqlContext.sql("select * from youku_mediadata")
    df = df.withColumn("yk_movie", translate('title')("mediadata")).filter(col('yk_movie') != '').persist(StorageLevel.DISK_ONLY)
    iqiyi_tags = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车']
    iqiyi2tag_df, iqy = iqiyi2tag(data_path, iqiyi_tags)
    yk_rdd = df.select('mediadata').rdd.map(list)
    yk_rdd = yk_rdd.map(lambda xs: [xs[0],find(xs[0],iqy)])
    df = yk_rdd.toDF(['mediadata','movie'])
    df = df.join(iqiyi2tag_df, "movie", "left")
    df.registerTempTable('tab_name')
    sqlContext.sql("insert into table yk_iqytag select * from tab_name ")




def youku_user_tag():
    sqlContext = HiveContext(sc)
    sqlContext.sql("use usercenter_dw")
    df = sqlContext.sql("select * from youku_matched")
    drop_list = ['mediadata', 'yktag', 'iqytag']
    df = df.select([column for column in df.columns if column not in drop_list])
    exprs = [avg(x).alias(x) for x in df.drop('userid').columns]
    cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
    df = df.groupby("userid").agg(*exprs).withColumn('source', lit('youku')).withColumn('update_dt', lit(cur_date))
    df.registerTempTable('tab_name')
    sqlContext.sql("insert overwrite table youku_user_tag select * from tab_name")



if __name__ == '__main__':
    # data_path = sys.argv[1]
    data_path = "hdfs://bitautodmp/user/yangyuhan1/iqy.txt"
    match_all(data_path)
    youku_user_tag()
