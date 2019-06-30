# -*- coding:utf-8 -*-
'''
Created on 2018/8/24

@author: kongyangyang
'''
import sys
import yaml
import platform
import numpy as np
import random
from sklearn import preprocessing

sys.path.append("../../")
from dsp.ctr.data_manager import DataManager


def generate_ffm_data(labeledpoint_path, ffm_format_path):
    dm_instance.loadLabeledPoint(labeledpoint_path)
    samples = dm_instance.data
    # 数据归一化
    X = np.vstack((samples["pos_samples"]["X"], samples["neg_samples"]["X"]))
    # scaler = preprocessing.StandardScaler().fit(X)
    min_max_scaler = preprocessing.MinMaxScaler().fit(X)
    X_pos = np.around(min_max_scaler.transform(samples["pos_samples"]["X"]), 4)
    X_neg = np.around(min_max_scaler.transform(samples["neg_samples"]["X"]), 4)

    col2field_id = {}
    with open(ffm_field_idx_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split(" ")
            for item in items:
                field, col = item.split(":")
                col2field_id[int(col)] = field

    with open(ffm_format_path, "w", encoding="utf-8") as file_write:
        axis_pos = X_pos.nonzero()
        cur_sampele = []
        cur_r = 0
        for i in range(axis_pos[0].shape[0]):
            r, l = axis_pos[0][i], axis_pos[1][i]
            if r == cur_r:
                cur_sampele.append(":".join([str(col2field_id[l]), str(l), str(X_pos[r, l])]))
            else:
                file_write.write("1 " + " ".join(cur_sampele) + "\n")
                cur_sampele = []
            cur_r = r

        axis_neg = X_neg.nonzero()
        cur_sampele = []
        cur_r = 0
        for i in range(axis_neg[0].shape[0]):
            r, l = axis_neg[0][i], axis_neg[1][i]
            if r == cur_r:
                cur_sampele.append(":".join([str(col2field_id[l]), str(l), str(X_neg[r, l])]))
            else:
                file_write.write("0 " + " ".join(cur_sampele) + "\n")
                cur_sampele = []
            cur_r = r


def make_ffm_train_vaild_test_data(ffm_format_path):
    ffm_data = {"pos_samples": [], "neg_samples": []}
    with open(ffm_format_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            if line.startswith("1"):
                ffm_data["pos_samples"].append(line.strip())
            else:
                ffm_data["neg_samples"].append(line.strip())

    pos_cnt = len(ffm_data["pos_samples"])
    neg_cnt = len(ffm_data["neg_samples"])
    index_list = list(range(neg_cnt))
    samples_index = random.sample(index_list, int(pos_cnt * 1.1))
    neg_cnt = len(samples_index)
    pos_list = list(range(pos_cnt))
    random.shuffle(pos_list)
    with open(workdir + "ffm_train.txt", "w", encoding="utf-8") as file_write:
        for idx in pos_list[:int(pos_cnt * 0.7)]:
            file_write.write(ffm_data["pos_samples"][idx] + "\n")
        for idx in samples_index[:int(neg_cnt * 0.7)]:
            file_write.write(ffm_data["neg_samples"][idx] + "\n")

    with open(workdir + "ffm_vaild.txt", "w", encoding="utf-8") as file_write:
        for idx in pos_list[int(pos_cnt * 0.7):int(pos_cnt * 0.8)]:
            file_write.write(ffm_data["pos_samples"][idx] + "\n")
        for idx in samples_index[int(neg_cnt * 0.7):int(neg_cnt * 0.8)]:
            file_write.write(ffm_data["neg_samples"][idx] + "\n")

    with open(workdir + "ffm_test.txt", "w", encoding="utf-8") as file_write:
        for idx in pos_list[int(pos_cnt * 0.8):]:
            file_write.write(ffm_data["pos_samples"][idx] + "\n")
        for idx in samples_index[int(neg_cnt * 0.8):]:
            file_write.write(ffm_data["neg_samples"][idx] + "\n")


if __name__ == "__main__":
    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    workdir = config_param["workdir"][platform.system()]
    dm_instance = DataManager(4, workdir)
    ffm_field_idx_path = workdir + "field_idx_4.ffm"

    generate_ffm_data(workdir + "samples-optimization_{}.labeledpoint".format(4),
                      ffm_format_path=workdir + "samples-optimization_{}.ffm".format(4))
    make_ffm_train_vaild_test_data(ffm_format_path=workdir + "samples-optimization_{}.ffm".format(4))
