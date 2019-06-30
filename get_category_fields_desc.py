# -*- coding:utf-8 -*-
'''
Created on 2018/8/14

@author: kongyangyang
'''
import pickle
import os
import pandas as pd
import platform
import sys

sys.path.append("../../")
from dsp.ctr.variable_desc import *


def load_raw_fields(data_path):
    """
    :param data_path:
    :param dst_path:
    :param profile_path_dict:
    :param labelday:
    :return:
    """
    data_df = pd.DataFrame(
        pd.read_table(data_path, header=None, encoding='utf-8', sep=',', names=header_of_spark_exported_file,
                      low_memory=False))
    channel_list = list(data_df["channelid"].unique())
    print("current all channels:", channel_list)

    categorical_field_name = []

    if config_param["fields_use_strategy"]["realtime"]:
        categorical_field_name += real_time_ad_fields
    if config_param["fields_use_strategy"]["personas"]:
        categorical_field_name += personas_fields

    featureValuesNumDict = {channel: {k: 0 for k in categorical_field_name} for channel in channel_list}
    featureValuesIndexDict = {channel: {k: {} for k in categorical_field_name} for channel in channel_list}

    for channelid in channel_list:
        current_channel_data_df = data_df[data_df["channelid"] == channelid]
        print("current channelid = {}".format(channelid), list(current_channel_data_df["placeid"].unique()))
        for k in featureValuesIndexDict[channelid].keys():
            _values = list(current_channel_data_df[k].unique())
            values = set()
            for v in _values:
                if k in ["materialid", "interest"]:
                    if v.rstrip("-") != "-1":
                        for _v in v.rstrip("-").split("-"):
                            values.add(_v)
                    else:
                        values.add(v.rstrip("-"))
                elif k in ["height", "width"]:
                    values.add(int(float(v)))
                else:
                    values.add(v)
            if defaultID not in values:
                values.add(defaultID)
            if k == "height":
                values.add("260")
            elif k == "width":
                values.add("370")

            tmp_dict = {}
            for (idx, v) in enumerate(sorted([str(i) for i in values])):
                tmp_dict[str(v)] = idx
            featureValuesIndexDict[channelid][k] = tmp_dict
            featureValuesNumDict[channelid][k] = len(tmp_dict)

    # for k, v in featureValuesIndexDict.items():
    #     print(k, v)

    # print("categorical variable dim:")
    # for k, v in featureValuesNumDict.items():
    #     print(k + "\t", featureValuesIndexDict[k])
    # print("枚举类特征维度总和:", sum(featureValuesNumDict.values()))
    pickle.dump(featureValuesIndexDict,
                open(workdir + "featureValuesIndexDict.pkl", "wb"))


if __name__ == "__main__":
    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    workdir = config_param["workdir"][platform.system()]

    load_raw_fields(workdir + "samples-optimization_08_std")
