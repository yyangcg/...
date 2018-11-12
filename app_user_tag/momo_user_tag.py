#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/10/16 9:35
# @Author  : Yang Yuhan
from pyspark import SparkContext
sc =SparkContext()
sc.setLogLevel("ERROR")
from pyspark.sql.functions import StringType
from pyspark.sql.functions import *
from pyspark import StorageLevel
from pyspark.sql import Row
from pyspark.sql import HiveContext
import time
from pyspark.sql.functions import udf
import json


def translate(tag):
    def translate_(col):
        data = json.loads(col)
        return data.get(tag)
    return udf(translate_, StringType())


def momo2tag(data_path):
    return sc.textFile(data_path).map(lambda x: Row(momotag=x.split("\t")[0], tag=x.split("\t")[1])).collectAsMap()


def map_tag(momo2tag):
    def mapping(col):
        tag = momo2tag.get(col,'')
        return tag
    return udf(mapping, StringType())

momo_tag_list = [('10001', '游戏'),
                 ('10002', '汽车'),
                 ('10003', '旅游'),
                 ('10004', '生活'),
                 ('10005', '娱乐'),
                 ('10006', '体育'),
                 ('10007', '电影'),
                 ('10008', '时尚'),
                 ('10009', '科技'),
                 ('10010', '教育'),
                 ('10011', '教育'),
                 ('10012', '教育'),
                 ('10013', '生活'),
                 ('10014', '购物')]


def imei_user_tag(data_path):
    sqlContext = HiveContext(sc)
    sqlContext.sql("use usercenter_dw");
    df = sqlContext.sql("select * from momo_tmp")
    df = df.withColumn("momotag", translate('usertag')("mediadata")).select("userid", 'momotag').filter(col('momotag') != '')\
        .withColumn('momotag', explode(split('momotag', ',')))\
        .filter((length('momotag') == 5))\
        .withColumn('tag',lit(''))
    for item in momo_tag_list:
        df = df.withColumn('tag', when(col('momotag') == item[0], item[1]).otherwise(col('tag'))).cache()
    tag_list = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车', '美容', '母婴育儿', '电影', '搞笑', '健康', '教育', '音乐', '资讯']
    exprs = [max(when(col("tag") == x, lit(1)).otherwise(lit(0))).alias(x) for x in tag_list]
    cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
    df = df.groupby("userid").agg(*exprs)\
        .withColumn('source', lit('momo'))\
        .withColumn('update_dt', lit(cur_date))
    sqlContext.sql("use usercenter_dw")
    df.registerTempTable('tab_name')
    sqlContext.sql("insert into table momo_user_tag_distinct select * from tab_name")

# insert overwrite table usercenter_dw.momo_tmp select distinct imeimd5 as userid, mediadata from t2pdm_data.t05_chehui_dsp_log where etl_dt between '2018-01-01' and '2018-04-14' and channelid=4 and length(imeimd5) =32;
#  create table usercenter_dw.momo_tmp_idfa as
# insert overwrite table usercenter_dw.momo_tmp select distinct idfa as userid, mediadata from t2pdm_data.t05_chehui_dsp_log where etl_dt between '2018-01-01' and '2018-04-14' and channelid=4 and length(idfa) > 24;



def momo_user_tag(data_path):
    sqlContext = HiveContext(sc)
    sqlContext.sql("use t2pdm_data");
    momo2tag_dict = momo2tag(data_path)
    df = sqlContext.sql("select distinct imeimd5, idfa, mediadata from t05_chehui_dsp_log where etl_dt between '2018-08-10' and '2018-08-15' and channelid=4")
    df = df.withColumn('userid',when(col('idfa') == 'WEO7bSfuwptr9Bgaxa0VqA==', col('imeimd5')).otherwise(col('idfa'))).filter(length('userid') > 31).select('userid', 'mediadata')
    df = df.withColumn("momotag", translate('usertag')("mediadata")).select("userid", 'momotag').filter(col('momotag') != '')
    df = df.withColumn('momotag', explode(split('momotag', ','))).filter((col('momotag') != '') & (col('momotag').isNotNull()) & (col('momotag') != 'null'))
    df = df.withColumn("tag", map_tag(momo2tag_dict)('momotag')).select("userid", 'tag').filter((col('tag') != '') & (col('tag').isNotNull()) & (col('tag') != 'null'))
    tag_list = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车', '美容', '母婴育儿', '电影', '搞笑', '健康', '教育', '音乐', '资讯']
    exprs = [max(when(col("tag") == x, lit(1)).otherwise(lit(0))).alias(x) for x in tag_list]
    cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
    df = df.groupby("userid").agg(*exprs).withColumn('source', lit('momo')).withColumn('update_dt', lit(cur_date))
    sqlContext.sql("use usercenter_dw")
    df.registerTempTable('tab_name')
    sqlContext.sql("insert overwrite table momo_user_tag select * from tab_name ")

# def momo_user_tag(data_path):
#     sqlContext = HiveContext(sc)
#     sqlContext.sql("use t2pdm_data")
#     momo2tag_dict = momo2tag(data_path)
#     # to_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time() - 55 * 60 * 60 * 24)))
#     # from_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time() - 60 * 60 * 60 * 24)))
#     df = sqlContext.sql("select distinct imeimd5, idfa, mediadata from t05_chehui_dsp_log where etl_dt between '2018-08-10' and '2018-08-16' and channelid=4")
#     df = df.withColumn('userid',when(col('idfa') == 'WEO7bSfuwptr9Bgaxa0VqA==', col('imeimd5')).otherwise(col('idfa'))).filter(length('userid') > 31).select('userid', 'mediadata').distinct()
#     df1 = df.withColumn("momotag", translate('usertag')("mediadata")).select("userid", 'momotag').filter(col('momotag') != '')
#     df2 = df1.withColumn('momotag', explode(split('momotag', ','))).filter((col('momotag') != '') & (col('momotag').isNotNull()) & (col('momotag') != 'null'))
#     df0 = df2.withColumn("tag", map_tag(momo2tag_dict)('momotag')).select("userid", 'tag').filter((col('tag') != '') & (col('tag').isNotNull()) & (col('tag') != 'null')).distinct()
#     tag_list = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车', '美容', '母婴育儿', '电影', '搞笑', '健康', '教育', '音乐', '资讯']
#     exprs = [max(when(col("tag") == x, lit(1)).otherwise(lit(0))).alias(x) for x in tag_list]
#     cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
#     df0 = df0.groupby("userid").agg(*exprs).withColumn('source', lit('momo')).withColumn('update_dt', lit(cur_date))
#     sqlContext.sql("use usercenter_dw")
#     df0.registerTempTable('tab_name')
#     sqlContext.sql("insert into table momo_user_tag select * from tab_name ")


if __name__ == '__main__':
    # data_path = sys.argv[1]
    data_path = "hdfs://bitautodmp/user/yangyuhan1/momo_dict.txt"
    momo_user_tag(data_path)


df = df.withColumn("momotag", translate('usertag')("mediadata")).select("userid", 'momotag').filter(col('momotag') != '')\
        .withColumn('momotag', explode(split('momotag', ',')))\
        .filter((length('momotag') == 5))\
        .withColumn('tag',lit(''))
for item in momo_tag_list:
    df = df.withColumn('tag', when(col('momotag') == item[0], item[1]).otherwise(col('tag'))).cache()
tag_list = ['娱乐', '科技', '购物', '生活', '企业办公', '时尚', '旅游', '游戏', '财经', '女性', '体育', '摄影', '汽车', '美容', '母婴育儿', '电影', '搞笑', '健康', '教育', '音乐', '资讯']
exprs = [max(when(col("tag") == x, lit(1)).otherwise(lit(0))).alias(x) for x in tag_list]
cur_date = time.strftime("%Y-%m-%d", time.localtime(int(time.time())))
df = df.groupby("userid").agg(*exprs)\
    .withColumn('source', lit('momo'))\
    .withColumn('update_dt', lit(cur_date))