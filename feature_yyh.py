#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/12/27 14:28
# @Author  : Yang Yuhan
# -*- coding:utf-8 -*-
import xlearn as xl
import os
import sys
import platform
from sklearn import preprocessing
from dsp.ctr.evaluation import evaluation_for_xlearn
from sklearn.model_selection import train_test_split
from dsp.ctr.down_sample_by_dist import down_sample
from dsp.utils.ensemble_utils import *

sys.path.append("../../")


class FFMExperiment(object):
    def __init__(self, config_params):
        self.config_params = config_params
        self.algo = "ffm"

    def prepare_for_ffm(self, dataframe):
        train_x, train_y, test_x, test_y, header = FFMExperiment.scale_and_split(dataframe)
        # w_pos, w_neg = FFMExperiment.get_weight(dataframe)
        self.generate_feature(train_x, train_y, test_x, test_y, header)

    def experiment(self, dataframe=None, *algo):
        """
        :param dataframe: 浅层特征数据框
        :return:
        """
        workdir = self.config_params["workdir"][platform.system()]
        phase = self.config_params[self.algo]["phase"]
        if len(algo) > 0:
            self.algo = algo[0]

        if phase == "complete":
            self.prepare_for_ffm(dataframe)
        elif phase in {"train_python", "ensemble"}:
            if not os.path.exists(workdir + "ffm/ffm_train_python.txt"):
                print("please first run phase='complete'")
                sys.exit(0)
            if phase == "train_python":
                self.train_ffm(workdir + "ffm/ffm_train_python.txt", workdir + "ffm/ffm_test_python.txt",
                               workdir + "ffm/")
            elif phase == "ensemble":
                self.train_ensemble(dataframe)

            evaluation_for_xlearn(workdir + "ffm/ffm_train_python.txt",
                                  workdir + "ffm/ffm_test_python.txt",
                                  workdir + "ffm/train_predict.txt",
                                  workdir + "ffm/test_predict.txt")

        elif phase == "scaler":
            FFMExperiment.get_scaler(dataframe, workdir + "ffm/min_max_scaler.txt", self.config_params["channelid"])
        else:
            raise ValueError("please inupt correct phase: complete, train_python, emsemble, scaler")

    @staticmethod
    def get_scaler(dataframe, save_path, channelid):
        """
        采用 min-max-scaler 对数据进行缩放，可以保持 one-hot 的稀疏性
        :param dataframe: 待缩放的数据
        :param save_path
        :return:
        """
        header = list(dataframe.columns.values)

        df_pos = dataframe[dataframe["label"] == 1]
        df_neg = dataframe[dataframe["label"] == 0]
        df_neg = df_neg.sample(frac=df_pos.shape[0] * 1.1 / df_neg.shape[0])
        df_union = df_neg.append(df_pos)
        df_shuffle = df_union.sample(frac=1)
        x = df_shuffle[header[1:]].values
        min_max_scaler = preprocessing.MinMaxScaler().fit(x)
        with open(save_path, "a", encoding="utf-8") as file_write:
            file_write.write(channelid + "\tscale_\t")
            for i in range(x.shape[1]):
                file_write.write(str(min_max_scaler.scale_[i]) + ",")
            file_write.write("\n")

            file_write.write(channelid + "\tmin_\t")
            for i in range(x.shape[1]):
                file_write.write(str(min_max_scaler.min_[i]) + ",")
            file_write.write("\n")

    @staticmethod
    def get_weight(dataframe, frac=1.0):
        header = list(dataframe.columns.values)
        dataframe = dataframe.drop_duplicates()
        df_pos = dataframe[dataframe["label"] == 1]
        df_neg = dataframe[dataframe["label"] == 0]
        r1 = df_pos.shape[0]/dataframe.shape[0]
        df_neg = df_neg.sample(frac=min(1.0, (df_pos.shape[0] * frac * 1.1 + frac + 1) / df_neg.shape[0]))
        df_union = df_neg.append(df_pos)
        print("去重前", df_union.shape)
        df_union = df_union.drop_duplicates(subset=header[1:], keep='first')
        print("去重后", df_union.shape)
        for i in range(int(frac) - 1):
            df_union = df_union.append(df_pos)
        r2 = df_union[dataframe["label"] == 1].shape[0] / df_union.shape[0]
        w_pos = 1
        w_neg = np.around(r2/r1,5)
        return w_pos,w_neg


    def scale_and_split(dataframe, frac=1.0):
        header = list(dataframe.columns.values)
        dataframe = dataframe.drop_duplicates()
        df_pos = dataframe[dataframe["label"] == 1]

        df_neg = dataframe[dataframe["label"] == 0]
        df_neg = df_neg.sample(frac=min(1.0, (df_pos.shape[0] * frac * 1.1 + frac + 1) / df_neg.shape[0]))
        # df_neg = down_sample(df_neg, frac=min(1.0, df_pos.shape[0] * 1.1 / df_neg.shape[0]))
        df_union = df_pos.append(df_neg)
        print("去重前", df_union.shape)
        df_union = df_union.drop_duplicates(subset=header[1:], keep='first')
        print("去重后", df_union.shape)
        for i in range(int(frac) - 1):
            df_union = df_union.append(df_pos)

        y = df_union[header[0]].values
        x = df_union[header[1:]].values
        train_x, test_x, train_y, test_y = train_test_split(x, y, test_size=0.3, random_state=42)

        min_max_scaler = preprocessing.MinMaxScaler().fit(train_x)
        train_x = np.around(min_max_scaler.transform(train_x), 5)
        test_x = np.around(min_max_scaler.transform(test_x), 5)

        return train_x, train_y, test_x, test_y, header

    def generate_feature(self, train_x, train_y, test_x, test_y, header):
        self.generate_train_test_valid_data(train_x, train_y, header[1:], "ffm_train_python.txt")
        self.generate_train_test_valid_data(test_x, test_y, header[1:], "ffm_test_python.txt")

    def generate_train_test_valid_data(self, x, y, column_names, filename):
        col2field_id = {}
        field_name_dict = {}
        for idx, name in enumerate(column_names):
            items = name.split(":")
            if len(items) == 3:
                field = ":".join(items[:2])
            else:
                field = items[0]
            if field not in field_name_dict:
                field_name_dict[field] = len(field_name_dict)
            col2field_id[idx] = field_name_dict[field]

        if not os.path.exists(self.config_params["workdir"][platform.system()] + "ffm"):
            os.mkdir(self.config_params["workdir"][platform.system()] + "/ffm")

        with open(self.config_params["workdir"][platform.system()] + "ffm/{}".format(filename), "w",
                  encoding="utf-8") as file_write:
            axis_pos = x.nonzero()
            cur_r = 0
            cur_sampele = []
            for i in range(axis_pos[0].shape[0]):
                r, l = axis_pos[0][i], axis_pos[1][i]
                if r == 0 and len(cur_sampele) == 0:
                    cur_sampele = [str(y[0])]
                if r == cur_r:
                    cur_sampele.append(":".join([str(col2field_id[l]), str(l), str(x[r, l])]))
                else:
                    file_write.write(" ".join(cur_sampele) + "\n")
                    cur_sampele = [str(y[r]), ":".join([str(col2field_id[l]), str(l), str(x[r, l])])]
                cur_r = r

    def train_ffm(self, trainset_path, testset_path, model_save_path, suffix=""):
        """
            self.config_params["workdir"] + "ffm/ffm_train_java.txt"
            self.config_params["workdir"] + "ffm/ffm_test_java.txt"
            self.config_params["workdir"] + "ffm/ffm.txt"
        :return:
        """
        ffm_model = xl.create_ffm()  # Use field-aware factorization machine
        ffm_model.disableNorm()  # instance-wise normalization
        ffm_model.setTrain(trainset_path)  # Training data
        ffm_model.setValidate(testset_path)  # Validation data
        ffm_model.setSigmoid()
        param = self.config_params[self.algo]
        if "ffm" in param:
            param = param["ffm"]
        if "phase" in param:
            param.pop("phase")
        if "model_cnt" in param:
            param.pop("model_cnt")

        model_txt_path = model_save_path + "ffm_{}{}.txt".format(self.config_params["channelid"], suffix)
        model_binary_path = model_save_path + "ffm_{}{}.out".format(self.config_params["channelid"], suffix)

        ffm_model.setTXTModel(model_txt_path)
        ffm_model.fit(param, model_binary_path)

        self.evaluation([model_binary_path], trainset_path, testset_path)

    def evaluation(self, model_binary_path_list, trainset_path, testset_path):
        ffm_model = xl.create_ffm()  # Use field-aware factorization machine
        ffm_model.disableNorm()  # instance-wise normalization
        ffm_model.setTrain(trainset_path)  # Training data
        ffm_model.setValidate(testset_path)  # Validation data
        ffm_model.setSigmoid()

        workdir = self.config_params["workdir"][platform.system()]
        if len(model_binary_path_list) > 1:
            for idx, model_binary_path in enumerate(model_binary_path_list):
                ffm_model.setTest(trainset_path)
                ffm_model.predict(model_binary_path, workdir + "ffm/train_predict_{}.txt".format(idx + 1))
                ffm_model.setTest(testset_path)
                ffm_model.predict(model_binary_path, workdir + "ffm/test_predict_{}.txt".format(idx + 1))
        else:
            ffm_model.setTest(trainset_path)
            ffm_model.predict(model_binary_path_list[0], workdir + "ffm/train_predict.txt")
            ffm_model.setTest(testset_path)
            ffm_model.predict(model_binary_path_list[0], workdir + "ffm/test_predict.txt")

    def train_ensemble(self, dataframe):
        if "model_cnt" in self.config_params:
            model_cnt = self.config_params.pop("model_cnt")
        else:
            model_cnt = 3
        train_x, train_y, test_x, test_y, header = FFMExperiment.scale_and_split(dataframe, frac=model_cnt)
        train_cnt = train_x.shape[0]
        subtrain_cnt = int(train_cnt / model_cnt)
        test_cnt = test_x.shape[0]
        subtest_cnt = int(test_cnt / model_cnt)
        workdir = self.config_params["workdir"][platform.system()]
        for m in range(1, model_cnt + 1):
            train_x_cur = train_x[(m - 1) * subtrain_cnt:m * subtrain_cnt, :]
            train_y_cur = train_y[(m - 1) * subtrain_cnt:m * subtrain_cnt]
            test_x_cur = test_x[(m - 1) * subtest_cnt:m * subtest_cnt, :]
            test_y_cur = test_y[(m - 1) * subtest_cnt:m * subtest_cnt]
            self.generate_feature(train_x_cur, train_y_cur, test_x_cur, test_y_cur, header)
            self.train_ffm(workdir + "ffm/ffm_train_python.txt", workdir + "ffm/ffm_test_python.txt",
                           workdir + "ffm/", suffix="_" + str(m))

        self.evaluation(
            [workdir + "ffm/ffm_{}_{}.out".format(self.config_params["channelid"], i) for i in range(1, model_cnt + 1)],
            workdir + "ffm/ffm_train_python.txt", workdir + "ffm/ffm_test_python.txt")

        pred_train_list = get_y_pred([workdir + "ffm/train_predict_{}.txt".format(i) for i in range(1, model_cnt + 1)])
        y_pre_train = ensemble_pred(pred_train_list)
        pred_test_list = get_y_pred([workdir + "ffm/test_predict_{}.txt".format(i) for i in range(1, model_cnt + 1)])
        y_pre_test = ensemble_pred(pred_test_list)
        np.savetxt(workdir + "ffm/train_predict.txt", y_pre_train)
        np.savetxt(workdir + "ffm/test_predict.txt", y_pre_test)


if __name__ == "__main__":
    pass
    # config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    # workdir = config_param["workdir"][platform.system()]
    # xgboost_plus_ffm = XgboostPlusFFMExperiment()
    # xgboost_plus_ffm.train_ffm()
