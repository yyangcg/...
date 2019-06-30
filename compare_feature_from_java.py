# -*- coding:utf-8 -*-
'''
Created on 2018/8/17

@author: kongyangyang
'''


# -*- coding:utf-8 -*-
'''
Created on 2018/8/17

@author: kongyangyang
'''
import os
import yaml
import platform
import sys

sys.path.append("../../")
from dsp.ctr.data_manager import DataManager
from dsp.utils.data_utils import *

# 测试 Python 生成的特征向量与java 生成的是否一样


if __name__ == "__main__":
    config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    if platform.system() == "Linux":
        workdir = config_param["work_dir"]["Linux"]
    else:
        workdir = config_param["work_dir"]["Windows"]

    channelid = 4
    predict_day = "2018-08-09"
    data_manager = DataManager(channelid=channelid, workdir=workdir)

    if not os.path.exists(workdir + "/samples-optimization_test_std".format(channelid)):
        std_raw_samples(workdir + "/samples-optimization_test")
    data_manager.load_raw_fields(workdir + "samples-optimization_test_std",
                                 workdir + "samples-optimization_test_labeledpoint_{}".format(channelid),
                                 {
                                     "creativeid": workdir + "ctr_dsp_creativeid_statistics.csv",
                                     "adid": workdir + "ctr_dsp_adid_statistics.csv",
                                     "advertiserid": workdir + "ctr_dsp_advertiserid_statistics.csv",
                                 },
                                 predict_day
                                 )
    print("end")


