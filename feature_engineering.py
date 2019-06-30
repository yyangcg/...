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
import threading

sys.path.append("../../../")

from dsp.ctr.variable_desc import *
from dsp.utils.data_utils import *
from dsp.ctr.ad_resources import AdResources


class FeatureEngineering:
    def __init__(self):
        self.channelid = None
        self.day_list = None
        self.featureValuesIndexDict = None

    def prepare_data(self, spark_std_path, history_path_dict, labelday, window):
        data_df = pd.DataFrame(
            pd.read_table(spark_std_path, header=None, encoding='utf-8', sep='\t',
                          names=header_of_spark_exported_file, low_memory=False))

        if not check_channelid(data_df, channel_field_name, self.channelid):
            return

        data_df = data_df[(data_df[date_field_name] <= labelday) & (data_df[channel_field_name] == self.channelid)]
        if data_df.shape[0] == 0:
            print("current data_df with contition {0} < {1} shape is {2}".format(label_field_name, labelday,
                                                                                 data_df.shape))
            return
        data_df.fillna(config_param["defaultID"])
        data_df["province"][np.isnan(data_df["province"])] = config_param["defaultID"]

        data_df['width'] = data_df['width'].astype('int')
        data_df['height'] = data_df['height'].astype('int')
        data_df['province'] = data_df['province'].astype('int')

        creativeid_list = sorted(list(data_df["creativeid"].unique()))

        # 历史统计信息
        entity_history_df_dict = {}
        for entity_name, _path in history_path_dict.items():
            if entity_name != "user":
                entity_history_df_dict[entity_name] = load_history_ad(_path, labelday, self.channelid, window,
                                                                      column_names=[entity_name, "exposurenum",
                                                                                    "clicknum", "exposureuv", "clickuv",
                                                                                    "etl_dt", "channelid"])
            else:
                entity_history_df_dict[entity_name] = load_history_user(_path, labelday, self.channelid, window)

        fields_used = FeatureEngineering.get_fields_used()
        return data_df, entity_history_df_dict, fields_used, creativeid_list

    def generate_feature(self, spark_std_df, entity_history_df_dict, fields_used, creativeid_list, labeled_point_path,
                         format="csv"):
        def _one_hot_interest_materialid(x, colname):
            vec = [0] * len(self.featureValuesIndexDict[colname])
            if x != "-1":
                items = x.rstrip("-").split("-")
            else:
                items = [config_param["defaultID"]]
            for it in items:
                vec[self.featureValuesIndexDict[colname][int(it)]] = 1.0
            return vec

        _fields_used = fields_used.copy()
        fields_used = [f for f in fields_used if f not in ["interest", "materialid"]]
        df_one_hot = pd.get_dummies(
            spark_std_df[sorted([field for field in fields_used if field in categorical_field_name])],
            columns=sorted([field for field in fields_used if field in categorical_field_name]))

        self.featureValuesIndexDict, entity_idx_to_id = {}, {}
        for entity in ["interest", "materialid"]:
            if entity in _fields_used:
                entity_set = set(
                    "-".join([x.rstrip("-") for x in list(spark_std_df[entity].unique()) if x != "-1"]).split("-"))
                entity_set.add(config_param["defaultID"])
                self.featureValuesIndexDict[entity] = {}
                entity_idx_to_id[entity] = {}
                for idx, name in enumerate(sorted([int(i) for i in list(entity_set) if i != ""])):
                    self.featureValuesIndexDict[entity][name] = idx
                    entity_idx_to_id[entity][idx] = name

                df_one_hot_entity = spark_std_df[entity].map(lambda x: _one_hot_interest_materialid(x, entity))
                df_one_hot = pd.concat([df_one_hot, df_one_hot_entity], axis=1, join="inner")

        colname_sorted = sorted(list(df_one_hot.columns.values))
        self.featureValuesIndexDict["creativeTime"] = {}
        for colname in colname_sorted:
            if colname not in ["interest", "materialid"]:
                items = colname.split("_")
                field_type, field_value = items[0], "_".join(items[1:])
                if field_value == "UNKNOWN":
                    print(colname)
                if field_type not in self.featureValuesIndexDict:
                    self.featureValuesIndexDict[field_type] = {}
                self.featureValuesIndexDict[field_type][field_value] = len(self.featureValuesIndexDict[field_type])

        if config_param["fields_use_strategy"]["creativeTime"]:
            for colname in creative_related_dt:
                self.featureValuesIndexDict["creativeTime"][colname] = len(self.featureValuesIndexDict["creativeTime"])
            df_one_hot = df_one_hot.join(spark_std_df[creative_related_dt], how="inner")
            colname_sorted = sorted(colname_sorted + creative_related_dt)

        if config_param["fields_use_strategy"]["history"]:
            df_one_hot = df_one_hot.join(spark_std_df[['creativeid', 'adid', 'advertiserid']], how="inner")

        df_one_hot = df_one_hot.join(spark_std_df[[user_field_name, label_field_name, date_field_name]], how="inner")

        history_entityname_entityid = {}
        creative_id_to_idx = {creativeid_list[idx]: idx for idx in range(len(creativeid_list))}

        history_entity_sorted = sorted(entity_history_df_dict.keys())

        feature_name_list = []
        count = 0
        with open(labeled_point_path, "w", encoding="utf-8") as file_write:
            for index, row in df_one_hot.iterrows():
                count += 1
                print("current process:{0}%, total = {1}".format(round(count / df_one_hot.shape[0] * 100, 3),
                                                                 df_one_hot.shape[0]), end="\r")

                cur_label_day = row[date_field_name]
                cur_label_day_stamp = time.mktime(time.strptime(cur_label_day, '%Y-%m-%d'))
                cur_feature = []
                for name in colname_sorted:
                    if name not in ["interest", "materialid"]:
                        if name.startswith("creativeTime"):
                            cur_feature.append(int(row[name] - cur_label_day_stamp) / 24 / 3600)
                        else:
                            cur_feature.append(row[name])
                        if feature_name_list is not None:
                            feature_name_list.append(name.replace("_", ":"))
                    else:
                        cur_feature += row[name]
                        if feature_name_list is not None:
                            feature_name_list += ["{}:{}".format(name, entity_idx_to_id[name][idx]) for idx in
                                                  range(len(row[name]))]

                if config_param["fields_use_strategy"]["history"]:
                    # day_list = get_day_list(cur_label_day, window=config_param["window"])
                    _history_entityname_entityid = {}

                    # 统计 截止到 cur_label_day 前一天的 历史累计信息
                    if cur_label_day not in history_entityname_entityid:
                        for entityname in entity_history_df_dict:
                            if entityname != "user":
                                _history_entityname_entityid[entityname] = {}
                                for entityid in self.featureValuesIndexDict[entityname].keys():
                                    if entityid == "UNKNOWN":
                                        entityid = config_param["defaultID"]

                                    _history_entityname_entityid[entityname][int(entityid)] = \
                                        self.ad_accumulation(entity_history_df_dict[entityname], int(entityid),
                                                             entityname,
                                                             get_day_list(cur_label_day, config_param["window"]))
                        history_entityname_entityid[cur_label_day] = _history_entityname_entityid

                    for entityname in history_entity_sorted:
                        if entityname != "user":
                            cur_history = history_entityname_entityid[cur_label_day][entityname][row[entityname]]
                        else:
                            user = row[user_field_name]

                            if user in entity_history_df_dict[entityname]:
                                cur_history = self.user_accumulation(
                                    entity_history_df_dict[entityname][user],
                                    get_day_list(cur_label_day, window=config_param["window"]), creative_id_to_idx)
                            else:
                                cur_history = [0] * len(self.featureValuesIndexDict["creativeid"]) * 2
                        if feature_name_list is not None:
                            feature_name_list += ["history:{}:{}".format(entityname, i) for i in
                                                  range(len(cur_history))]
                        cur_feature += cur_history

                if feature_name_list is not None:
                    feature_name_list.insert(0, "label")
                    file_write.write(",".join(feature_name_list) + "\n")
                    feature_name_list = None
                file_write.write(
                    "{},".format(row[label_field_name]) + ",".join([str(i) for i in cur_feature]) + "\n")

        print("\ntrans raw felids to {} end".format(format))

    @staticmethod
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

    def user_accumulation(self, user_history_dict, day_list, creative_id_to_idx):
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

    def ad_accumulation(self, history_df, entityid, entityname, day_list):
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

    def main(self, spark_std_path, history_path_dict, labeled_point_path, labelday, format="csv", channelid=4):
        if not os.path.exists(spark_std_path) or os.path.getsize(spark_std_path) == 0:
            if spark_std_path.endswith("_std"):
                adresources = AdResources(config_param=config_param)
                std_raw_samples(spark_std_path[:-4], adresources.creative_resources, adresources.meterial_resources)
            else:
                raise ValueError("spark_std_path = {} must ends with '_std'".format(spark_std_path))

        self.channelid = int(channelid)
        self.day_list = get_day_list(labelday, window=config_param["window"])
        spark_std_df, entity_history_df_dict, fields_used, creativeid_list = self.prepare_data(spark_std_path,
                                                                                               history_path_dict,
                                                                                               labelday,
                                                                                               config_param["window"])
        self.generate_feature(spark_std_df,
                              entity_history_df_dict,
                              fields_used,
                              creativeid_list,
                              labeled_point_path,
                              format=format)


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
    fe = FeatureEngineering()
    fe.main(spark_std_path=workdir + spark_export_file_name + "_std",
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
