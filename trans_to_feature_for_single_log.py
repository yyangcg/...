# -*- coding:utf-8 -*-
'''
Created on 2018/9/26

@author: kongyangyang
'''


# 将单条日志记录转为特征向量

def read_log(log_path, record_num=10):
    col_to_name = {}
    cnt = 0
    log_list = []
    with open(log_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split("\t")
            if line.startswith("typeid"):
                col_to_name = {i: items[i] for i in range(len(items))}
            else:
                cnt += 1
                log_list.append({col_to_name[i]: items[i] for i in range(len(items))})
    return log_list


def load_feature_name(data_path):
    feature_field_value_idx = {}
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split(",")
            for i in range(len(items)):
                _items = items[i].split(":")
                field = _items[0]
                if len(_items) == 3:
                    field += ":" + _items[1]

                if field not in feature_field_value_idx:
                    feature_field_value_idx[field] = {}
                feature_field_value_idx[field][items[-1]] = i

    return feature_field_value_idx


def trans2feature(log_list, feature_field_value_idx):
    for _log_dict in log_list:
        pass


if __name__ == "__main__":
    log_list = read_log("E:/Work/jobs/data/DSP/CTR预估/samples/samples-exposure.txt", record_num=10)
    feature_field_value_idx = load_feature_name("E:/Work/jobs/data/DSP/CTR预估/samples/featuresNames.txt")

    trans2feature(log_list, feature_field_value_idx)
