# -*- coding:utf-8 -*-
'''
Created on 2018/8/23

@author: kongyangyang
'''
import yaml
import platform


def load_feature_name(data_path):
    feature_col_to_name = {}
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split(",")[1:]
            feature_col_to_name = {idx: items[idx] for idx in range(len(items))}

    return feature_col_to_name


def check_feature_each_dim_dist(data_path, feature_col_to_field_id):
    feature_count = {}
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split(" ")[1:]
            col_list = [int(item.split(":")[1]) for item in items]
            for col in col_list:
                if col not in feature_count:
                    feature_count[col] = 0
                feature_count[col] += 1

    sored_keys = sorted(list(feature_count.keys()))
    for k in sored_keys:
        print(k, feature_count[k])


if __name__ == "__main__":
    # channelid = 4
    # predict_day = "2018-08-09"
    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    workdir = config_param["workdir"][platform.system()]
    #
    # format = "labeledpoint"
    # dm = DataManager(workdir=workdir)
    # dm.loadLabeledPoint(workdir + "samples-optimization_{}.{}".format(4, format))
    # idx_dict = {}
    # with open(workdir + "features_before_xgb.train", "r", encoding="utf-8") as file_read:
    #     for line in file_read:
    #         items = line.strip().split(" ")
    #         for it in items:
    #             if it.startswith("252:"):
    #                 it = it.split(":")[-1]
    #                 if it not in idx_dict:
    #                     idx_dict[it] = 0
    #                 idx_dict[it] += 1
    #
    # with open(workdir + "features_before_xgb.test", "r", encoding="utf-8") as file_read:
    #     for line in file_read:
    #         items = line.strip().split(" ")
    #         for it in items:
    #             if it.startswith("252:"):
    #                 # value = it.split(":")[-1]
    #                 if it not in idx_dict:
    #                     idx_dict[it] = 0
    #                 idx_dict[it] += 1
    #
    # for k, v in idx_dict.items():
    #     print(k, v)

    feature_col_to_field_id = load_feature_name(workdir + "model/featuresNames.txt")
    check_feature_each_dim_dist(workdir + "ffm/ffm_test_java.txt", feature_col_to_field_id)
