# -*- coding:utf-8 -*-
'''
Created on 2018/8/22

@author: kongyangyang
'''
import os
import sys
import platform
import argparse
from argparse import RawTextHelpFormatter
import numpy as np
from multiprocessing.pool import Pool
from joblib import Parallel, delayed
from pandas import DataFrame

sys.path.append("../../../")

from dsp.utils.data_utils import *
from dsp.ctr.ad_resources import AdResources
#
# path = '/data/yangyuhan/workspace/ctr/hdfs_ctr/samples-optimization_4_2019-01-17.csv'
# path = '/data/yangyuhan/workspace/ctr/hdfs_ctr/samples-optimization_5_2019-01-17.csv'
# path = '/data/yangyuhan/workspace/ctr/hdfs_ctr/samples-optimization_3_2019-01-17.csv'
# df = pd.read_csv(path)
# col = [i for i in df.columns if i.startswith('title')]
# col.append('label')
# df = df[col]

def prepare_spark_df(spark_std_path, labelday, channelid):
    # spark_df2 = pd.DataFrame(
    #     pd.read_table(spark_std_path, header=None, encoding='utf-8', sep='\t',
    #                   names=header_of_spark_exported_file, low_memory=False, nrows=10000))
    reader = pd.read_table(spark_std_path, sep='\t', encoding="utf-8", header=None,
                           names=header_of_spark_exported_file, low_memory=False,
                           iterator=True, chunksize=100000)
    spark_df = pd.concat([chunk for chunk in reader], ignore_index=True)

    if not check_channelid(spark_df, channel_field_name, channelid):
        return

    spark_df = spark_df[(spark_df[date_field_name] <= labelday) & (spark_df[channel_field_name] == channelid)]

    if spark_df.shape[0] == 0:
        print(list(spark_df[date_field_name].unique()))
        print(
            "current data_df with contition {0} < {1}, channelid={3} shape is {2}".format(date_field_name, labelday,
                                                                                          spark_df.shape, channelid))
        return

    spark_df.fillna(config_param["defaultID"])
    spark_df["province"][np.isnan(spark_df["province"])] = config_param["defaultID"]
    spark_df['width'] = spark_df['width'].astype('int')
    spark_df['height'] = spark_df['height'].astype('int')
    spark_df['province'] = spark_df['province'].astype('int')

    return spark_df


def prepare_interest_material_df(spark_df):
    def _expand_interest_materialid(x, colname):
        vec = [0] * len(featureValuesIndexDict[colname])
        for it in str(x).rstrip("-").split("-"):
            vec[featureValuesIndexDict[colname][int(it)]] = 1.0
        return vec

    featureValuesIndexDict = {}
    entity_idx_to_id = {}
    interest_matericals_df = []
    for entity in ["interest", "materialid"]:
        entity_set = set("-".join([str(x) for x in list(spark_df[entity].unique())]).split("-"))
        entity_set.add(config_param["defaultID"])
        featureValuesIndexDict[entity] = {}
        entity_idx_to_id[entity] = {}
        names_sorted = sorted([int(i) for i in list(entity_set) if i != ""])
        for idx, name in enumerate(names_sorted):
            featureValuesIndexDict[entity][name] = idx
            entity_idx_to_id[entity][idx] = name

        df_entity = spark_df[entity].apply(lambda x: pd.Series(_expand_interest_materialid(x, entity)))
        df_entity.rename(columns={i: entity + "_" + str(names_sorted[i]) for i in range(len(names_sorted))},
                         inplace=True)
        interest_matericals_df.append(df_entity)
    return pd.concat(interest_matericals_df, axis=1, join="inner")


def prepare_histoy_df(history_path_dict, labelday, channelid, window):
    # 历史统计信息
    entity_history_df_dict = {}
    if config_param["fields_use_strategy"]["history"]:
        for entity_name, _path in history_path_dict.items():
            if entity_name != "user":
                entity_history_df_dict[entity_name] = load_history_ad(_path, labelday, channelid, window,
                                                                      column_names=[entity_name, "exposurenum",
                                                                                    "clicknum", "exposureuv",
                                                                                    "clickuv", "etl_dt", "channelid"])
            else:
                # entity_history_df_dict[entity_name] = {}
                entity_history_df_dict[entity_name] = load_history_user(_path, labelday, channelid, window)

    # creativeid_list = list(entity_history_df_dict["creativeid"]["creativeid"].unique())
    # creative_id_to_idx = {creativeid_list[idx]: idx for idx in range(len(creativeid_list))}
    entity_accumulation_dict = {}
    for entityname, history_df in entity_history_df_dict.items():
        if entityname == "user":
            continue
        if entityname not in entity_accumulation_dict:
            entity_accumulation_dict[entityname] = []
        to_day_list = list(history_df["etl_dt"].unique())
        entityid_list = list(history_df[entityname].unique())
        for entityid in entityid_list:
            for to_day in to_day_list:
                day_list = get_day_list(to_day, window=config_param["window"])
                accumu_vec = ad_accumulation(history_df, entityid, entityname, day_list)
                entity_accumulation_dict[entityname].append([entityid, to_day] + accumu_vec)

    history_df_dict = {}
    for entityname, accumu_list in entity_accumulation_dict.items():
        cur_df = DataFrame(accumu_list,
                           columns=[entityname, date_field_name] + ["history:{}:{}".format(entityname, i) for i in
                                                                    range(40)])
        history_df_dict[entityname] = cur_df

    return history_df_dict, entity_history_df_dict["user"]


def combine_df(spark_df, history_df_dict, fields_used):
    df_combine = prepare_interest_material_df(spark_df)
    if config_param["fields_use_strategy"]["creativeTime"]:
        # df_createiveTime = (spark_df[creative_related_dt] - time.time()) / (24 * 3600)
        df_creativeTime = spark_df[creative_related_dt]
        df_combine = pd.concat([df_combine, df_creativeTime], axis=1, join="inner")

    df_combine = pd.concat([df_combine, spark_df[[user_field_name, label_field_name, date_field_name]]], axis=1,
                           join="inner")

    fields_used = [f for f in fields_used if f not in ["interest", "materialid"]]
    df_one_hot = pd.get_dummies(
        spark_df[sorted([field for field in fields_used if field in categorical_field_name])],
        columns=sorted([field for field in fields_used if field in categorical_field_name]))
    df_combine = pd.concat([df_combine, df_one_hot], axis=1, join="inner")

    if config_param["fields_use_strategy"]["history"]:
        history_id_df = spark_df[['creativeid', 'adid', 'advertiserid']]
        df_combine = pd.concat([df_combine, history_id_df], axis=1, join="inner")
        for entity_name in ['creativeid', 'adid', 'advertiserid']:
            df_combine = pd.merge(df_combine, history_df_dict[entity_name], on=[date_field_name, entity_name],
                                  how='outer').fillna(0)
        df_combine = df_combine[
            (df_combine["adid"] != 0) & (df_combine["creativeid"] != 0) & (df_combine["advertiserid"] != 0)]
    return df_combine


def generate_feature(df_combine, user_history_dict, labeled_point_path):
    def _fun(row, user_history_dict):
        day_list = get_day_list(row[date_field_name], window=config_param["window"])
        if len(user_history_dict) > 0:
            user_accumu_vec = user_accumulation(user_history_dict, day_list, creative_id_to_idx)
        else:
            user_accumu_vec = [0] * (len(creative_id_to_idx) * 2)
        return ",".join(
            [str(row[label_field_name])] + [str(row[name]) for name in names if name not in special_fields] +
            [str((time.mktime(time.strptime(row[date_field_name], "%Y-%m-%d")) - row[_n]) / 24 / 3600) for _n in
             creative_related_dt] + [str(i) for i in user_accumu_vec])

    names = df_combine.columns.values
    names = names.tolist()
    special_fields = set(
        creative_related_dt + [label_field_name, date_field_name, user_field_name, "creativeid", "advertiserid",
                               "adid"])
    creativeid_list = sorted(list(df_combine["creativeid"].unique()))
    creative_id_to_idx = {int(creativeid_list[idx]): idx for idx in range(len(creativeid_list))}
    results = Parallel(n_jobs=-1)(
        delayed(_fun)(row, user_history_dict.get(row["user"], {})) for index, row in df_combine.iterrows())

    headers = [label_field_name] + [name for name in names if name not in special_fields] + creative_related_dt \
              + ["history:user:{}".format(i) for i in range(len(creative_id_to_idx) * 2)]

    with open(labeled_point_path, "w", encoding="utf-8") as file_write:
        file_write.write(",".join(headers) + "\n")
        for r in results:
            file_write.write(r + "\n")


def get_fields_used():
    fields_used = []
    if config_param["fields_use_strategy"]["history"]:
        fields_used += history_fields
    if config_param["fields_use_strategy"]["realtime"]:
        fields_used += real_time_ad_fields
    if config_param["fields_use_strategy"]["personas"]:
        fields_used += personas_fields
    if config_param["fields_use_strategy"]["context"]:
        fields_used += context_fields
    if config_param["fields_use_strategy"]["creativeTime"]:
        fields_used += creative_related_dt

    return fields_used


def user_accumulation(user_history_dict, day_list, creative_id_to_idx):
    """
    在给定时间窗口内统计用户历史信息
    :return:
    """
    creative_num = len(creative_id_to_idx)
    history_vec = [0.0] * creative_num * 2
    for day, exposure_click_num in user_history_dict.items():
        if day in day_list:
            for key in ["exposure_num", "click_num"]:
                for _id, _cnt in exposure_click_num[key].items():
                    if int(_id) in creative_id_to_idx:
                        if key == "exposure_num":
                            history_vec[creative_id_to_idx[int(_id)]] = _cnt
                        else:
                            history_vec[creative_num + creative_id_to_idx[int(_id)]] = _cnt

    for i in range(creative_num, 2 * creative_num):
        if history_vec[i] > 0:
            history_vec[i] = history_vec[i] / (history_vec[i] + history_vec[i - creative_num])

    return history_vec


def ad_accumulation(history_df, entityid, entityname, day_list):
    """
    在给定时间窗口内统计广告id 相关历史信息
    :param history_df:
    :param entityid:
    :param entityname:
    :param day_list:
    :return:
    """
    df = history_df[history_df[entityname] == entityid]
    total_exposurenum, total_clicknum, total_clickuv, total_exposureuv = 0, 0, 0, 0

    feature_dim = 5
    day_to_idx = {day_list[idx]: idx for idx in range(len(day_list))}

    rst = [0] * len(day_list) * feature_dim
    for index, row in df.iterrows():
        clicknum, exposurenum, clickuv, exposureuv = row["clicknum"], row["exposurenum"], row["clickuv"], row[
            "exposureuv"]
        total_clicknum += clicknum
        total_exposurenum += exposurenum
        total_clickuv += clickuv
        total_exposureuv += exposureuv

        if row["etl_dt"] not in day_list:
            continue
        idx = day_to_idx[row["etl_dt"]]
        ratio = 0 if clicknum == 0 else clicknum / (clicknum + exposurenum)
        rst[idx * feature_dim:(idx + 1) * feature_dim] = clicknum, exposurenum, clickuv, exposureuv, ratio

    ratio = 0 if total_clicknum == 0 else total_clicknum / (total_exposurenum + total_clicknum)
    rst += [total_clicknum, total_exposurenum, total_clickuv, total_exposureuv, ratio]

    return rst


def main(spark_std_path, history_path_dict, labeled_point_path, labelday, format="csv", channelid=4):
    if not os.path.exists(spark_std_path) or os.path.getsize(spark_std_path) == 0:
        if spark_std_path.endswith("_std"):
            adresources = AdResources(config_param=config_param)
            std_raw_samples(spark_std_path[:-4], adresources.creative_resources, adresources.meterial_resources)
        else:
            raise ValueError("spark_std_path = {} must ends with '_std'".format(spark_std_path))

    channelid = int(channelid)

    time_start = time.time()
    spark_df = prepare_spark_df(spark_std_path, labelday, channelid)
    time_end = time.time()
    print("prepare_spark_df spend time is ", time_end - time_start)
    time_start = time_end
    history_df_dict, user_history_dict = prepare_histoy_df(history_path_dict, labelday, channelid,
                                                           window=config_param["window"])
    time_end = time.time()
    print("prepare_histoy_df spend time is ", time_end - time_start)
    time_start = time_end
    df_combine = combine_df(spark_df, history_df_dict, get_fields_used())
    time_end = time.time()
    print("combine_df spend time is ", time_end - time_start)
    time_start = time_end
    generate_feature(df_combine, user_history_dict, labeled_point_path)
    time_end = time.time()
    print("generate_feature spend time is ", time_end - time_start)


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='''FeatureEngineering''', formatter_class=RawTextHelpFormatter)
    parser.add_argument("--channelid", required=True, default=4, help='渠道')
    parser.add_argument("--date", required=True, default="2018-08-09", help='样本截止日期')
    parser.add_argument("--format", required=False, default="csv", help='特征样本保存格式')

    try:
        arguments = parser.parse_args(args=arguments)
        arguments = vars(arguments)
    except:
        parser.print_help()
        sys.exit(0)

    return arguments


def run(argvs):
    parameters = parse_arguments(argvs)
    channelid = parameters["channelid"]
    labelday = parameters["date"]
    workdir = config_param["workdir"][platform.system()]

    spark_export_file_name = "samples-optimization_{}".format(parameters["date"])
    # fe = FeatureEngineeringMult()
    main(spark_std_path=workdir + spark_export_file_name + "_std",
         history_path_dict={
             "creativeid": workdir + "creative_accumulation",
             "adid": workdir + "ad_accumulation",
             "advertiserid": workdir + "advertiser_accumulation",
             "user": workdir + "user_accumulation"
         },
         labeled_point_path=workdir + "samples-optimization_{}_{}.{}".format(channelid, labelday,
                                                                             parameters["format"]),
         labelday=labelday,
         format=parameters["format"],
         channelid=channelid
         )


if __name__ == "__main__":
    config_param = yaml.load(open("../config.yml", "r", encoding="utf-8").read())

    run(sys.argv[1:])
