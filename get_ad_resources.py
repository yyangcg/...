# -*- coding:utf-8 -*-
"""
file name: get_ad_resources.py
Created on 2018/10/17
@author: kyy_b
@desc:
"""
import pandas as pd
import sys
import platform
import argparse
from argparse import RawTextHelpFormatter

sys.path.append("../../../")
from dsp.utils.data_utils import *


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='''FeatureEngineering''', formatter_class=RawTextHelpFormatter)
    parser.add_argument("--date", required=True, default="2018-08-09", help='样本截止日期')

    try:
        arguments = parser.parse_args(args=arguments)
        arguments = vars(arguments)
    except:
        parser.print_help()
        sys.exit(0)

    return arguments


def load_ad_and_channel(parameters):
    parameters = parse_arguments(parameters)
    column_names = ["adid", "exposurenum", "clicknum", "exposureuv", "clickuv", "etl_dt", "channelid"]
    day_list = get_day_list(parameters["date"], config_param["window"] * 3)
    data_df = pd.DataFrame(pd.read_table(config_param["workdir"][platform.system()] + "ad_accumulation",
                                         encoding='utf-8', sep=',', names=column_names, header=None))
    data_df = data_df[(data_df["etl_dt"] <= day_list[-1]) & (data_df["etl_dt"] >= day_list[0])]
    channel_ad_dict = {}
    for index, row in data_df.iterrows():
        adid = row["adid"]
        channelid = row["channelid"]
        if channelid not in channel_ad_dict:
            channel_ad_dict[channelid] = set()
        channel_ad_dict[channelid].add(adid)
    with open(config_param["workdir"][platform.system()] + "ffm/channelid_ad", "w", encoding="utf-8") as file_write:
        for cid, adid_set in channel_ad_dict.items():
            file_write.write(str(cid) + "\t" + "\t".join([str(i) for i in adid_set]) + "\n")


if __name__ == "__main__":
    config_param = yaml.load(open("../config.yml", "r", encoding="utf-8").read())
    load_ad_and_channel(sys.argv[1:])
