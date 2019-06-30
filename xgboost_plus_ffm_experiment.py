# -*- coding:utf-8 -*-
'''
Created on 2018/8/22

@author: kongyangyang
'''
import numpy as np
from xgboost.sklearn import XGBClassifier
from sklearn.preprocessing import OneHotEncoder
import xlearn as xl
import os
import sys
import platform
from sklearn2pmml.pipeline import PMMLPipeline
from sklearn2pmml import sklearn2pmml
from sklearn import preprocessing
from dsp.ctr.evaluation import evaluateOnTrainAndTest, plot_prob_curve
from dsp.ctr.report import Report

sys.path.append("../../")


class XgboostPlusFFMExperiment(object):
    def __init__(self, config_params):
        self.config_params = config_params

    def experiment(self, dataframe=None):
        """
        方案: 浅层特征 + xgboost ===> 组合特征
              浅层特征 + 组合特征 + ffm ==> model
        :param dataframe: 浅层特征数据框
        :return:
        """
        workdir = self.config_params["workdir"][platform.system()]
        phase = self.config_params["xgboost_plus_ffm"]["phase"]
        params = self.config_params["xgboost_plus_ffm"]["xgboost"]

        if phase in ["shallow", "complete"]:
            train_x, train_y, test_x, test_y, header = XgboostPlusFFMExperiment.scale_and_split(dataframe)
            print("train_x_before_xgb.shape = ", train_x.shape)
            print("test_x_before_xgb.shape = ", test_x.shape)
            if phase == "shallow":
                XgboostPlusFFMExperiment.save_samples_before_xgb(train_x, train_y,
                                                                 workdir + "features_before_xgb.train")
                XgboostPlusFFMExperiment.save_samples_before_xgb(test_x, test_y, workdir + "/features_before_xgb.test")
            if phase == "complete":
                self.generate_feature(train_x, train_y, test_x, test_y, header, params)
        elif phase == "train_java":
            self.train_ffm(workdir + "ffm/ffm_train_java.txt", workdir + "ffm/ffm_test_java.txt", workdir + "ffm/")
            self.evaluation(workdir + "ffm/ffm_train_java.txt",
                            workdir + "ffm/ffm_test_java.txt",
                            workdir + "ffm/train_predict.txt",
                            workdir + "ffm/test_predict.txt")
        elif phase == "train_python":
            if not os.path.exists(workdir + "ffm/ffm_train_python.txt"):
                print("please first run phase='complete'")
                sys.exit(0)
            self.train_ffm(workdir + "ffm/ffm_train_python.txt", workdir + "ffm/ffm_test_python.txt", workdir + "ffm/")

            self.evaluation(workdir + "ffm/ffm_train_python.txt",
                            workdir + "ffm/ffm_test_python.txt",
                            workdir + "ffm/train_predict.txt",
                            workdir + "ffm/test_predict.txt")

        elif phase == "scaler":
            XgboostPlusFFMExperiment.get_scaler(dataframe, workdir + "ffm/min_max_scaler_{}.txt".format(
                self.config_params["channelid"]))

    @staticmethod
    def save_samples_before_xgb(x, y, save_path):
        """
        用于xgb挖掘组合特征之前的特征，主要是用来在java中跑xgb
        :param x:
        :param y:
        :param save_path:
        :return:
        """
        with open(save_path, "w") as file_write:
            axis_pos = x.nonzero()
            cur_r = 0
            cur_sampele = []
            for i in range(axis_pos[0].shape[0]):
                r, col = axis_pos[0][i], axis_pos[1][i]
                if r == 0 and len(cur_sampele) == 0:
                    cur_sampele = [str(y[0])]
                if r == cur_r:
                    cur_sampele.append(":".join([str(col), str(x[r, col])]))
                else:
                    file_write.write(" ".join(cur_sampele) + "\n")
                    cur_sampele = [str(y[r]), ":".join([str(col), str(x[r, col])])]
                cur_r = r
            if len(cur_sampele) > 0:
                file_write.write(" ".join(cur_sampele) + "\n")

    @staticmethod
    def get_scaler(dataframe, save_path):
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
        with open(save_path, "w", encoding="utf-8") as file_write:
            file_write.write("scale_" + "\t")
            for i in range(x.shape[1]):
                file_write.write(str(min_max_scaler.scale_[i]) + ",")
            file_write.write("\n")

            file_write.write("min_" + "\t")
            for i in range(x.shape[1]):
                file_write.write(str(min_max_scaler.min_[i]) + ",")
            file_write.write("\n")

    @staticmethod
    def scale_and_split(dataframe):
        header = list(dataframe.columns.values)

        df_pos = dataframe[dataframe["label"] == 1]
        # df_pos_sample = df_pos.sample(frac=1, replace=True)
        # df_pos = df_pos.append(df_pos_sample)
        df_neg = dataframe[dataframe["label"] == 0]
        df_neg = df_neg.sample(frac=min(1.0, df_pos.shape[0] * 1.05 / df_neg.shape[0]))
        df_union = df_neg.append(df_pos)
        df_shuffle = df_union.sample(frac=1)

        label_name = header[0]
        train_y = df_shuffle[label_name][:int(df_shuffle.shape[0] * 0.7)].values
        train_x = df_shuffle[header[1:]][:int(df_shuffle.shape[0] * 0.7)].values
        test_y = df_shuffle[label_name][int(df_shuffle.shape[0] * 0.7):].values
        test_x = df_shuffle[header[1:]][int(df_shuffle.shape[0] * 0.7):].values
        min_max_scaler = preprocessing.MinMaxScaler().fit(train_x)
        train_x = np.around(min_max_scaler.transform(train_x), 5)
        test_x = np.around(min_max_scaler.transform(test_x), 5)

        return train_x, train_y, test_x, test_y, header

    def generate_feature(self, train_x, train_y, test_x, test_y, header, params):
        train_x_transform, test_x_transform = XgboostPlusFFMExperiment.feature_transformer(train_x, train_y, test_x,
                                                                                           test_y, params)

        self.generate_train_test_valid_data(train_x_transform, train_x, train_y, header[1:], "ffm_train_python.txt")
        self.generate_train_test_valid_data(test_x_transform, test_x, test_y, header[1:], "ffm_test_python.txt")

    @staticmethod
    def feature_transformer(x_train, y_train, x_test, y_test, params):
        xgbt = XGBClassifier(**params).fit(x_train, y_train)
        gbt_enc = OneHotEncoder()
        gbt_enc.fit(xgbt.apply(x_train))
        train_x_transform = gbt_enc.transform(xgbt.apply(x_train))
        test_x_transform = gbt_enc.transform(xgbt.apply(x_test))

        # pipelineModel = PMMLPipeline([("xgboost", XGBClassifier(**params))])
        # pipelineModel.fit(x_train, y_train)
        # sklearn2pmml(pipelineModel, "/data/kongyy/ctr_online/model/xgboost_feature.pmml", with_repr=True)

        return train_x_transform, test_x_transform

    def generate_train_test_valid_data(self, train_transform, x, y, column_names, filename):
        col2field_id = {}
        field_name_dict = {}
        for idx, name in enumerate(column_names):
            if "_" in name:
                field = name.split("_")[0]
                if field not in field_name_dict:
                    field_name_dict[field] = len(field_name_dict)
                col2field_id[idx] = field_name_dict[field]
            elif ":" in name:
                field = name.split(":")[0]
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
                    leaf = train_transform[cur_r - 1, :]
                    col_start = x.shape[1]
                    cur_sampele += [
                        ":".join([str(len(field_name_dict) + i), str(col_start + leaf.indices[i]), str(1.0)]) for i in
                        range(leaf.indices.shape[0])]
                    file_write.write(" ".join(cur_sampele) + "\n")
                    cur_sampele = [str(y[r]), ":".join([str(col2field_id[l]), str(l), str(x[r, l])])]
                cur_r = r

    def train_ffm(self, trainset_path, testset_path, model_save_path):
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
        param = self.config_params["xgboost_plus_ffm"]["ffm"]

        model_txt_path = model_save_path + "ffm.txt"
        model_binary_path = model_save_path + "ffm.out"

        ffm_model.setTXTModel(model_txt_path)
        ffm_model.fit(param, model_binary_path)

        ffm_model.setTest(trainset_path)
        ffm_model.predict(model_binary_path, self.config_params["workdir"][platform.system()] + "ffm/train_predict.txt")
        ffm_model.setTest(testset_path)
        ffm_model.predict(model_binary_path, self.config_params["workdir"][platform.system()] + "ffm/test_predict.txt")

    @staticmethod
    def evaluation(train_real_path, test_real_path, train_predict_path, test_predict_path):
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

        evaluateOnTrainAndTest(y_train, y_test, y_pre_train, y_pre_test)

        # plot_prob_curve(np.array(y_train), np.array(y_pre_train))


if __name__ == "__main__":
    pass
    # config_param = yaml.load(open("config.yml", "r", encoding="utf-8").read())
    # workdir = config_param["workdir"][platform.system()]
    # xgboost_plus_ffm = XgboostPlusFFMExperiment()
    # xgboost_plus_ffm.train_ffm()
