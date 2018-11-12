#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/15 11:07
# @Author  : Yang Yuhan
from pyspark import SparkContext
sc =SparkContext()
sc.setLogLevel("ERROR")
import sys
from pyspark.sql.functions import *
from pyspark import StorageLevel
from pyspark.sql import Row
from pyspark.sql import HiveContext
import time
from pyspark.sql.functions import StringType


def load_appname2tag(data_path):
    return sc.textFile(data_path).map(lambda x: (x.split("\t")[0], x.split("\t")[1])).collectAsMap()


def load_appname2tag_df(data_path):
    return sc.textFile(data_path).map(lambda x: Row(appname=x.split("\t")[0], tag=x.split("\t")[1])).toDF()


def map_tag(app2tag):
    def mapping(col):
        tag = app2tag.get(col)
        return tag
    return udf(mapping, StringType())


def yichche_app(data_path):
    sqlContext = HiveContext(sc)
    sqlContext.sql("use t2pdm_data");
    df = sqlContext.sql("select distinct user_id as userid, appname,etl_dt from t01_sdk_device_app_info where etl_dt between '2018-04-26' and '2018-04-27'")
    tag_list = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车', '美容', '母婴育儿', '电影', '搞笑', '健康', '教育', '音乐', '资讯']
    appname2tag_dict = load_appname2tag(data_path)
    exprs = [max(when(col("tag") == x, lit(1)).otherwise(0)).alias(x) for x in tag_list]
    df0 = df.select("userid", "appname").where(col("appname").isin(list(appname2tag_dict.keys()))).distinct()
    df0 = df0.withColumn("tag", map_tag(appname2tag_dict)('appname')).select("userid", 'tag').filter((col('tag') != '') & (col('tag').isNotNull()) & (col('tag') != 'null')).distinct()
    cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
    df1 = df0.drop("appname").distinct().groupby("userid").agg(*exprs)
    df1 = df1.withColumn('source', lit('app')).withColumn('update_dt', lit(cur_date))
    df1.show()
    sqlContext.sql("use usercenter_dw")
    df1.registerTempTable('tab_name')
    sqlContext.sql("insert into table app_user_tag select * from tab_name ")


if __name__ == '__main__':
    # data_path = sys.argv[1]
    data_path = "hdfs://bitautodmp/user/yangyuhan1/app_interest.txt"
    yichche_app(data_path)




