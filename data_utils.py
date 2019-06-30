# -*- coding:utf-8 -*-
'''
Created on 2018/8/14

@author: kongyangyang
'''

import datetime
import pandas as pd
import json
import sys
import time

sys.path.append("../../")

from dsp.ctr.variable_desc import *


def std_raw_samples(data_path, creative_resources, material_resources):
    """
    spark 保存的数据存在一些特殊符号，此处去除特殊符号
    :param data_path:
    :return:
    """
    print("running std samples ...")
    creativeid_idx = header_of_spark_exported_file.index("creativeid")
    user_idx = header_of_spark_exported_file.index("user")
    with open(data_path + "_std", "w", encoding="utf-8") as file_write:
        with open(data_path, "r", encoding="utf-8") as file_read:
            for line in file_read:
                items = line.strip().split("\t")
                if len(items) != 19:
                    continue
                user = items[user_idx]
                if user.endswith("WEO7bSfuwptr9Bgaxa0VqA==") or len(user) == 64:
                    user = user[:32]
                    items[user_idx] = user

                if items[creativeid_idx] not in creative_resources:
                    continue
                cur_creative = creative_resources[items[creativeid_idx]]
                displaylabel = cur_creative["display_labels"]
                title = cur_creative["title"]
                creative_type = cur_creative["type"]
                campaign_id = cur_creative["campaign_id"]
                adgroup_id = cur_creative["adgroup_id"]
                material_ids = cur_creative["material_id"]
                width, height = 0, 0
                for mid in material_ids:
                    if mid in material_resources:
                        width = max(width, material_resources[mid]["width"])
                        height = max(height, material_resources[mid]["height"])

                creativeTime_create = time.mktime(time.strptime(cur_creative["created_at"], '%Y-%m-%d %H:%M:%S'))
                creativeTime_updated = time.mktime(time.strptime(cur_creative["updated_at"], '%Y-%m-%d %H:%M:%S'))

                items += ["-".join(material_ids), str(creative_type), str(height), str(width), title, displaylabel,
                          str(campaign_id), str(adgroup_id), str(creativeTime_create), str(creativeTime_updated)]

                new_line = "\t".join(items)
                file_write.write(new_line + "\n")


def std_raw_oot(data_path, creative_resources, material_resources):
    """
    spark 保存的数据存在一些特殊符号，此处去除特殊符号
    :param data_path:
    :return:
    """
    print("running std samples ...")
    creativeid_idx = header_of_spark_exported_file.index("creativeid")
    user_idx = header_of_spark_exported_file.index("user")
    with open(data_path + "_std", "w", encoding="utf-8") as file_write:
        with open(data_path, "r", encoding="utf-8") as file_read:
            for line in file_read:
                items = line.strip().split("\t")
                if len(items) != 19:
                    continue
                user = items[user_idx]
                if user.endswith("WEO7bSfuwptr9Bgaxa0VqA==") or len(user) == 64:
                    user = user[:32]
                    items[user_idx] = user

                if items[creativeid_idx] not in creative_resources:
                    continue
                cur_creative = creative_resources[items[creativeid_idx]]
                displaylabel = cur_creative["display_labels"]
                title = cur_creative["title"]
                creative_type = cur_creative["type"]
                campaign_id = cur_creative["campaign_id"]
                adgroup_id = cur_creative["adgroup_id"]
                material_ids = cur_creative["material_id"]
                width, height = 0, 0
                for mid in material_ids:
                    if mid in material_resources:
                        width = max(width, material_resources[mid]["width"])
                        height = max(height, material_resources[mid]["height"])

                creativeTime_create = time.mktime(time.strptime(cur_creative["created_at"], '%Y-%m-%d %H:%M:%S'))
                creativeTime_updated = time.mktime(time.strptime(cur_creative["updated_at"], '%Y-%m-%d %H:%M:%S'))

                items += ["-".join(material_ids), str(creative_type), str(height), str(width), title, displaylabel,
                          str(campaign_id), str(adgroup_id), str(creativeTime_create), str(creativeTime_updated)]

                new_line = "\t".join(items)
                file_write.write(new_line + "\n")


def check_channelid(df, channel_field_name, channelid):
    channel_list = list(df[channel_field_name].unique())
    print("current all channels:", channel_list)
    if channelid not in channel_list:
        print("current used chanel is ", " ".join(str(i) for i in channel_list))
        print("current channelid {} not in used".format(channelid))
        return False
    return True


def get_day_list(to_date, window):
    return sorted([(datetime.datetime.strptime(to_date, "%Y-%m-%d") + datetime.timedelta(-w)).strftime(
        '%Y-%m-%d') for w in range(1, window + 1)])


def load_history_ad(data_path, to_date, channelid, window, column_names):
    day_list = get_day_list(to_date, window * 3)
    data_df = pd.DataFrame(pd.read_table(data_path, encoding='utf-8', sep=',', names=column_names, header=None))
    data_df = data_df[(data_df["etl_dt"] <= day_list[-1]) & (data_df["etl_dt"] >= day_list[0]) & (
            data_df["channelid"] == channelid)].sort_values("etl_dt")

    return data_df


def load_history_user(user_path, to_date, channelid, window=7):
    day_list = get_day_list(to_date, window * 3)

    user_history = {}
    with open(user_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split("\t")
            user, exposure_num_str, click_num_str, etl_dt, _channelid = items[:]
            if int(_channelid) != channelid:
                continue
            if etl_dt not in day_list:
                continue

            if user not in user_history:
                user_history[user] = {}
            if etl_dt not in user_history[user]:
                user_history[user][etl_dt] = {"exposure_num": {}, "click_num": {}}
                if len(exposure_num_str) > 0:
                    user_history[user][etl_dt]["exposure_num"] = json.loads(exposure_num_str)
                if len(click_num_str) > 0:
                    user_history[user][etl_dt]["click_num"] = json.loads(click_num_str)
    return user_history
