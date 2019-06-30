# -*- coding:utf-8 -*-
"""
file name: merge_sample_for_different_label_day.py
Created on 2018/11/2
@author: kyy_b
@desc:
"""


def merge_acumulation():
    for filename in ["ad_accumulation", "advertiser_accumulation", "creative_accumulation"]:
        with open("/data/kyy/workspace/ctr/hdfs_ctr/" + filename, "r", encoding="utf-8") as file_read:
            record_set = set([line.strip() for line in file_read])
        with open("/data/kyy/workspace/ctr/hdfs_ctr-1101/" + filename, "r", encoding="utf-8") as file_read:
            for line in file_read:
                record_set.add(line.strip())

        with open("/data/kyy/workspace/ctr/hdfs_ctr/" + filename, "w", encoding="utf-8") as file_write:
            for line in record_set:
                file_write.write(line + "\n")


def merge_samples():
    with open("/data/kyy/workspace/ctr/hdfs_ctr/samples-optimization_4_2018-11-02.csv", "a",
              encoding="utf-8") as file_write:
        with open("/data/kyy/workspace/ctr/hdfs_ctr-1101/samples-optimization_4_2018-11-01.csv", "r",
                  encoding="utf-8") as file_read:
            for line in file_read:
                file_write.write(line)


if __name__ == "__main__":
    merge_acumulation()
    merge_samples()
