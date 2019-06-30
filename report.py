# -*- coding:utf-8 -*-
'''
file name: report.py
Created on 2018/10/16
@author: kyy_b
@desc:  train 结果的报表信息
'''
import os
import datetime
import yaml
import argparse
import platform
import sys
from argparse import RawTextHelpFormatter

sys.path.append("../../")
sys.path.append("../../../")
sys.path.append("../")
sys.path.append(".")
from dsp.ctr.evaluation import evaluateOnTrainAndTest
from dsp.utils.data_utils import *


class Report:
    def __init__(self):
        pass

    @staticmethod
    def stats_ad():
        """
        统计每个广告实际点击次数、实际曝光次数、点击率、预测点击率
        :return:
        """

    @staticmethod
    def get_evaluation(train_real_path, test_real_path, train_predict_path, test_predict_path):
        """
        :param train_real_path:
        :param test_real_path:
        :param train_predict_path:
        :param test_predict_path:
        :return:
        """
        with open(test_predict_path, "r", encoding="utf-8") as file_read:
            y_pre_test = [float(line.strip()) for line in file_read]

        with open(train_predict_path, "r", encoding="utf-8") as file_read:
            y_pre_train = [float(line.strip()) for line in file_read]

        with open(test_real_path, "r", encoding="utf-8") as file_read:
            y_test = [float(line.strip().split(" ")[0]) for line in file_read]

        with open(train_real_path, "r", encoding="utf-8") as file_read:
            y_train = [float(line.strip().split(" ")[0]) for line in file_read]

        report_dict = evaluateOnTrainAndTest(y_train, y_test, y_pre_train, y_pre_test)

        return report_dict

    @staticmethod
    def get_ctr_real_and_predict(test_real_path, train_real_path, ad_accumulation_path, channelid, date):
        """
        统计下采样后的数据集上的 ctr_predict 以及 没有采样的真实数据集上的 ctr_ture值
        :return:
        """
        with open(test_real_path, "r", encoding="utf-8") as file_read:
            y_predict = [float(line.strip().split(" ")[0]) for line in file_read]

        with open(train_real_path, "r", encoding="utf-8") as file_read:
            y_predict += [float(line.strip().split(" ")[0]) for line in file_read]

        ctr_predict = sum(y_predict) / len(y_predict)

        exposure_num, click_num = 0, 0
        days = get_day_list(date, window=7)
        with open(ad_accumulation_path, "r", encoding="utf-8") as file_read:
            for line in file_read:
                items = line.strip().split(",")
                if items[-1] == channelid and items[-2] in days:
                    exposure_num += float(items[1])
                    click_num += float(items[2])
        ctr_observed = click_num / (click_num + exposure_num)
        return {"ctr_predict": ctr_predict, "ctr_cobserved": ctr_observed}

    @staticmethod
    def get_report_and_save(train_real_path, test_real_path, train_predict_path, test_predict_path,
                            ad_accumulation_path, report_path, channelid, date):
        report_dict = Report.get_evaluation(train_real_path, test_real_path, train_predict_path, test_predict_path)
        report_dict.update(
            Report.get_ctr_real_and_predict(test_real_path, train_real_path, ad_accumulation_path, channelid, date))

        sorted_key = sorted(list(report_dict.keys()))

        if not os.path.exists(report_path):
            f = open(report_path, "w")
            f.close()

        with open(report_path, "w", encoding="utf-8") as file_write:
            file_write.write("=" * 20 + " channelid = {} ".format(channelid) + "=" * 20 + "\n")
            file_write.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
            file_write.write("=" * 50 + "\n")
            for k in sorted_key:
                file_write.write(k + "\t" + str(report_dict[k]) + "\n")
                file_write.write("-" * 55 + "\n")


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='''FeatureEngineering''', formatter_class=RawTextHelpFormatter)
    parser.add_argument("--channelid", required=True, default=4, help='渠道')
    parser.add_argument("--date", required=True, default="2018-10-15", help='样本截止日期')

    try:
        arguments = parser.parse_args(args=arguments)
        arguments = vars(arguments)
    except:
        parser.print_help()
        sys.exit(0)

    return arguments


def run(arugments):
    config_params = yaml.load(open("../config.yml", "r", encoding="utf-8").read())
    workdir = config_params["workdir"][platform.system()]
    parameters = parse_arguments(arugments)
    Report.get_report_and_save(workdir + "ffm/ffm_train_java.txt",
                               workdir + "ffm/ffm_test_java.txt",
                               workdir + "ffm/train_predict.txt",
                               workdir + "ffm/test_predict.txt",
                               workdir + "ad_accumulation",
                               workdir + "report.txt",
                               parameters["channelid"],
                               parameters["date"])


if __name__ == "__main__":
    run(sys.argv[1:])
