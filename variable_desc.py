# -*- coding:utf-8 -*-
'''
Created on 2018/8/11

@author: kongyangyang
'''

import yaml

# spark 导出文件的字段对应关系
# header_of_spark_exported_file = ["channelid", "user", "gender", "age", "interest", "week", "hour", "province", "adid",
#                                  "creativeid", "advertiserid", "materialid", "placeid", "displaylabel", "createtype",
#                                  "height", "width", "nettype", "mobiletype", "os", "phonebrand", "creativeTime_create",
#                                  "creativeTime_updated", "creativeTime_fromcreated2updated", "ad_exposure_num", "label",
#                                  "labelDay"]

header_of_spark_exported_file = ["channelid", "user", "gender", "age", "interest", "week", "hour", "province", "adid",
                                 "creativeid", "advertiserid", "placeid", "nettype", "mobiletype", "os", "phonebrand",
                                 "ad_exposure_num", "label", "labelDay"]
extent_fields = ["materialid", "createtype", "height", "width", "title", "displaylabel", "campaignid", "adgroupid", "kws"]
header_of_spark_exported_file += extent_fields

# 上下文相关字段
context_fields = ["nettype", "mobiletype", "os", "phonebrand", "week", "hour", "province"]
# 用户个人属性
personas_fields = ["age", "gender", "interest"]
# 实时广告相关字段
real_time_ad_fields = ["adid", "creativeid", "advertiserid", "materialid", "placeid", "displaylabel", "createtype",
                       "height", "width", "title", "campaignid", "adgroupid"]
# 历史统计特征 - 连续
history_fields = []

# 创意相关特征
# creative_related_dt = ["creativeTime_create", "creativeTime_updated", "creativeTime_fromcreated2updated"]
creative_related_dt = ["creativeTime_create", "creativeTime_updated"]
header_of_spark_exported_file += creative_related_dt

categorical_field_name = context_fields + personas_fields + real_time_ad_fields

label_field_name = "label"
date_field_name = "labelDay"
channel_field_name = 'channelid'
user_field_name = 'user'

# 曝光次数
# ad_exposure_num

if __name__ == "__main__":
    import pickle

    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    defaultID = config_param["defaultID"]

    featureValuesIndexDict = pickle.load(open("E:/Work/jobs/data/DSP/CTR预估/samples/featureValuesIndexDict.pkl", 'rb'))
    with open("E:/Work/jobs/data/DSP/CTR预估/samples/featureValuesIndexDict.txt", "w", encoding="utf-8") as file_write:
        for channel, entity_value_index in featureValuesIndexDict.items():
            for entity, value_index in entity_value_index.items():
                if entity == "province":
                    _value_index = {}
                    for (_k, _v) in value_index.items():
                        if _k != defaultID and _k != 'nan':
                            _value_index[str(int(float(_k)))] = _v
                        else:
                            _value_index[_k] = _v
                    value_index = _value_index
                file_write.write(str(channel) + "\t" + entity + "\t" + ",".join(
                    [_k + ":" + str(_v) for (_k, _v) in value_index.items()]) + "\n")
