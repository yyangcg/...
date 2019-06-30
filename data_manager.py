# -*- coding:utf-8 -*-
'''
Created on 2018/7/30

@author: kongyangyang
'''
import numpy as np
import re
import pandas as pd
import platform
import datetime
import os
import traceback
import pickle
import sys
from dsp.ctr.variable_desc import *
from dsp.utils.data_utils import *

sys.path.append("../../")


class DataManager(object):
    def __init__(self, channelid=4, config_param=None):
        self.max_row_num = 1000000
        self.channelid = channelid
        self.defaultID = "UNKNOWN"
        self.data = {"pos_samples": {"X": None, "Y": None},
                     "neg_samples": {"X": None, "Y": None}}
        self.featureValuesIndexDict = None
        self.featureValuesNumDict = None

    @staticmethod
    def load_dataframe(df_path, nrows=100):
        return pd.DataFrame(pd.read_table(df_path, encoding='utf-8', sep=',', low_memory=False, nrows=nrows))

    def loadLabeledPoint(self, data_path):
        """
        读取 spark  生成的 LabeledPoint 文件
        :param data_path:
        :return:
        """
        label_point_save_path = data_path + ".pkl"
        if os.path.exists(label_point_save_path):
            self.data = pickle.load(open(label_point_save_path, 'rb'))
        else:
            with open(data_path, "r", encoding="utf-8") as file_read:
                counter = {"pos": 0, "neg": 0}
                n = 0
                for line in file_read:
                    n += 1
                    print(n, end="\r")
                    try:
                        items = [float(it) for it in re.sub("[()\[\]]", "", line.strip()).split(",")]
                        if self.data["pos_samples"]["X"] is None:
                            self.data["pos_samples"]["X"] = np.zeros((self.max_row_num, len(items) - 1))
                            self.data["pos_samples"]["Y"] = np.zeros((self.max_row_num, 1))
                            self.data["neg_samples"]["X"] = np.zeros((self.max_row_num, len(items) - 1))
                            self.data["neg_samples"]["Y"] = np.zeros((self.max_row_num, 1))
                        elif counter["pos"] >= self.max_row_num:
                            self.max_row_num *= 2
                            self.data["pos_samples"]["X"] = np.tile(self.data["pos_samples"]["X"], (2, 1))
                            self.data["pos_samples"]["Y"] = np.tile(self.data["pos_samples"]["Y"], (2, 1))
                        elif counter["neg"] >= self.max_row_num:
                            self.max_row_num *= 2
                            self.data["neg_samples"]["X"] = np.tile(self.data["neg_samples"]["X"], (2, 1))
                            self.data["neg_samples"]["Y"] = np.tile(self.data["neg_samples"]["Y"], (2, 1))

                        if items[0] == 1.0:
                            self.data["pos_samples"]["X"][counter["pos"], :] = items[1:]
                            self.data["pos_samples"]["Y"][counter['pos']] = items[0]
                            counter["pos"] += 1
                        else:
                            self.data["neg_samples"]["X"][counter['neg'], :] = items[1:]
                            self.data["neg_samples"]["Y"][counter['neg']] = items[0]
                            counter["neg"] += 1
                    except:
                        traceback.print_exc()
                        print(n, end="\r")

            self.data["pos_samples"]["X"] = self.data["pos_samples"]["X"][:counter["pos"], :]
            self.data["pos_samples"]["Y"] = self.data["pos_samples"]["Y"][:counter["pos"], :]
            self.data["neg_samples"]["X"] = self.data["neg_samples"]["X"][:counter["neg"], :]
            self.data["neg_samples"]["Y"] = self.data["neg_samples"]["Y"][:counter["neg"], :]
            pickle.dump(self.data, open(label_point_save_path, 'wb'))

        print("\npos_samples dim is ", self.data["pos_samples"]["X"].shape, " neg_samples dim is ",
              self.data["neg_samples"]["X"].shape)

    def load_raw_fields(self, data_path, dst_path, profile_path_dict, labelday):
        """
        :param data_path:
        :param dst_path:
        :param profile_path_dict:
        :param labelday:
        :return:
        """
        if os.path.exists(dst_path):
            return

        self.featureValuesIndexDict = pickle.load(open(workdir + "featureValuesIndexDict.pkl", 'rb'))
        self.featureValuesNumDict = {k: {_k: len(_v) for (_k, _v) in v.items()} for (k, v) in
                                     self.featureValuesIndexDict.items()}

        data_df = pd.DataFrame(
            pd.read_table(data_path, header=None, encoding='utf-8', sep=',',
                          names=header_of_spark_exported_file,
                          low_memory=False))
        column_names = list(data_df.columns.values)
        print(column_names)

        channel_list = list(data_df["channelid"].unique())
        print("current all channels:", channel_list)

        if self.channelid not in channel_list:
            print("current used chanel is ", " ".join(str(i) for i in channel_list))
            print("current channelid {} not in used".format(self.channelid))

        data_df = data_df[(data_df["labelDay"] != labelday) & (data_df["channelid"] == self.channelid)]

        featureValuesNumDict = self.featureValuesNumDict[self.channelid]
        featureValuesIndexDict = self.featureValuesIndexDict[self.channelid]

        entity_profile_dict = {}
        for entityname, _path in profile_path_dict.items():
            entity_profile_dict[entityname] = self.load_profile(_path, entityname)

        bad_count = {"pos": 0, "neg": 0}

        cur_row_num = 0
        with open(dst_path, "w", encoding="utf-8") as file_write:
            for index, row in data_df.iterrows():
                cur_row_num += 1
                print("raw fields transfrom to labelpoint:", cur_row_num, end="\r")
                try:
                    tmp_vec = []
                    for k in sorted(featureValuesNumDict.keys()):
                        cur_vec = [0] * featureValuesNumDict[k]
                        if k in ["materialid", "interest"]:
                            if row[k].rstrip("-") != "-1":
                                items = row[k].rstrip("-").split("-")
                            else:
                                items = [row[k]]
                            for it in items:
                                cur_vec[featureValuesIndexDict[k][str(it)]] = 1.0
                        elif k in ["height", "width"]:
                            cur_vec[featureValuesIndexDict[k][str(int(row[k]))]] = 1.0
                        else:
                            cur_vec[featureValuesIndexDict[k][str(row[k])]] = 1.0
                        tmp_vec += cur_vec
                        print(cur_vec)
                        print(k, len(tmp_vec))

                    # print("feature vector dim:", len(tmp_vec))
                    for k in column_names:
                        if k.startswith("days_from"):
                            tmp_vec.append(row[k])
                    # print("feature vector dim:", len(tmp_vec))

                    # 历史曝、点击、pv、uv特征
                    history_feature = []
                    for entityname in sorted(entity_profile_dict.keys()):
                        history_feature += self.stats_by_window(entity_profile_dict[entityname], row["labelDay"],
                                                                featureValuesIndexDict[entityname])
                        # print(len(history_feature))
                    if len(history_feature) > 0:
                        tmp_vec += history_feature
                        # print("feature vector dim:", len(tmp_vec))
                        file_write.write(
                            "({},[".format(row['label']) + ",".join([str(i) for i in tmp_vec]) + "])\n")
                except:
                    traceback.print_exc()
                    print(row)
                    if str(row["ad_exposure_num"]) == '1':
                        bad_count["pos"] += 1
                    else:
                        bad_count["neg"] += 1
                    print(bad_count, end='\r')
        print("\ntrans raw felids to features end")

    def load_profile(self, data_path, entityname):
        tmp_dict = {}
        data_df = pd.DataFrame(
            pd.read_table(data_path, encoding='utf-8', sep=','))

        rst = data_df.groupby(["etl_dt", "channelid", entityname]).agg("sum")
        records = rst.to_dict(orient="split")
        index, data, columns = records["index"], records["data"], records["columns"]
        for idx, item in enumerate(index):
            labelday, channelid, entityid = item[:]
            channelid = str(channelid)
            entityid = str(entityid)
            if labelday not in tmp_dict:
                tmp_dict[labelday] = {}
            if channelid not in tmp_dict[labelday]:
                tmp_dict[labelday][channelid] = {}
            if entityid not in tmp_dict[labelday][channelid]:
                tmp_dict[labelday][channelid][entityid] = {}
            for i, v in enumerate(columns):
                tmp_dict[labelday][channelid][entityid][v] = data[idx][i]

        return tmp_dict

    def stats_by_window(self, profile_dict, labelday, featureValuesIndexDict, window=7):
        from_date = (datetime.datetime.strptime(labelday, "%Y-%m-%d") + datetime.timedelta(-window)).strftime(
            '%Y-%m-%d')
        stats_info = {'clicknum': [0] * len(featureValuesIndexDict),
                      'clickuv': [0] * len(featureValuesIndexDict),
                      'exposurenum': [0] * len(featureValuesIndexDict),
                      'exposureuv': [0] * len(featureValuesIndexDict)
                      }
        for day in profile_dict.keys():
            if from_date < day < labelday:
                if not str(self.channelid) in profile_dict[day]:
                    print("have no channelid = {0}, day = {1}".format(self.channelid, day))
                    return []
                entity_count_info = profile_dict[day][str(self.channelid)]
                for entityid, statistics_name_and_value in entity_count_info.items():
                    if entityid in featureValuesIndexDict:
                        for name, value in statistics_name_and_value.items():
                            stats_info[name][featureValuesIndexDict[entityid]] += value

        click_rate = [0] * len(featureValuesIndexDict)
        for i in range(len(featureValuesIndexDict)):
            if stats_info["exposurenum"][i] > 0:
                click_rate[i] = stats_info["clicknum"][i] / (stats_info["exposurenum"][i] + stats_info["clicknum"][i])

        return stats_info['clicknum'] + stats_info['clickuv'] + stats_info['exposurenum'] + stats_info[
            'exposureuv'] + click_rate

    def main(self):
        data_manager_instance = DataManager(channelid, workdir)

        if not os.path.exists(workdir + "/samples-optimization_std_{}".format(channelid)):
            std_raw_samples(workdir + "/samples-optimization")

        data_manager_instance.load_raw_fields(workdir + "samples-optimization_std",
                                              workdir + "samples-optimization_labeledpoint_{}".format(channelid),
                                              {
                                                  "creativeid": workdir + "ctr_dsp_creativeid_statistics.csv",
                                                  "adid": workdir + "ctr_dsp_adid_statistics.csv",
                                                  "advertiserid": workdir + "ctr_dsp_advertiserid_statistics.csv",
                                              },
                                              "2018-05-26"
                                              )


if __name__ == "__main__":
    workdir = "E:/Work/jobs/data/DSP/CTR预估/samples/"
    if platform.system() == "Linux":
        workdir = "/data/kongyy/ctr/"

    channelid = 5
