# -*- coding:utf-8 -*-
'''
Created on 2018/7/30

@author: kongyangyang
'''
import platform
from sklearn2pmml import sklearn2pmml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import preprocessing
import yaml
import sys
import argparse
from argparse import RawTextHelpFormatter

sys.path.append("../../../")

from dsp.ctr.experiment.gbdt_experiment import GbdtExperiment
from dsp.ctr.experiment.gbdt_plus_lr_experiment import GbdtPlusLrExperiment
from dsp.ctr.experiment.xgboost_experiment import XgboostExperiment
from dsp.ctr.data_manager import DataManager
from dsp.ctr.experiment.xgboost_plus_ffm_experiment import XgboostPlusFFMExperiment
from dsp.ctr.experiment.lightgbm_plus_ffm_experiment import LightGbmPlusFFMExperiment
from dsp.ctr.experiment.ffm_experiment import FFMExperiment
from dsp.ctr.evaluation import *


class CtrExperiment(object):
    def __init__(self):
        pass

    @staticmethod
    def experiment(x, y, algo, params=None, df_path=None):
        x_train, x_test, y_train, y_test = None, None, None, None
        if df_path is None:
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
            print("train samples dim", x_train.shape, "test samples dim", x_test.shape)

            # 数据归一化
            min_max_scaler = preprocessing.MinMaxScaler().fit(x)
            x_train = np.around(min_max_scaler.transform(x_train), 4)
            x_test = np.around(min_max_scaler.transform(x_test), 4)

        print("runing algorithm:" + algo)

        if algo == "gbdt":
            return GbdtExperiment.train(x_train, y_train, params)
        elif algo == "lr":
            clf_l2_LR = LogisticRegression(penalty='l2', tol=0.01)
            clf_l2_LR.fit(x_train, y_train)
            y_pre_train = clf_l2_LR.predict(x_train)
            # print(classification_report(y_train, y_pre_train, target_names=["exposure", "click"]))
        elif algo == "gbdt_plus_lr":
            return GbdtPlusLrExperiment.experiment(x_train, x_test, y_train, y_test, params)
            # # todo 类别变量与连续变量分开
            # X_train, X_train_lr, y_train, y_train_lr = train_test_split(X_train, y_train, test_size=0.5)
            # params_ = params.copy()
            # params_["n_estimators"] = 40
            # pipelineModel = GbdtExperiment.train(X_train, y_train, params_)
            # gbt_enc = OneHotEncoder()
            # gbt_enc.fit(pipelineModel.named_steps['gbtclassifier'].apply(X_train)[:, :, 0])
            #
            # grd_lm = LogisticRegression(max_iter=300)
            # grd_lm.fit(gbt_enc.transform(pipelineModel.named_steps['gbtclassifier'].apply(X_train_lr)[:, :, 0]),
            #            y_train_lr)
            #
            # y_pred_grd_lm = grd_lm.predict(
            #     gbt_enc.transform(pipelineModel.named_steps['gbtclassifier'].apply(X_test)[:, :, 0]))  # [:, 1]
            # print(classification_report(y_test, y_pred_grd_lm, target_names=["exposure", "click"]))

        elif algo == "xgboost":
            pipelineModel = XgboostExperiment.experiment(x_train, y_train, params)
            evaluateOnTrainAndTest(y_train, y_test, pipelineModel.predict(x_train), pipelineModel.predict(x_test))
            return pipelineModel
        elif algo == "xgboost_plus_fm":
            pass
        elif algo == "xgboost_plus_ffm":
            xgboost_plust_ffm = XgboostPlusFFMExperiment(config_params=config_param)
            phase = config_param[algo]["phase"]
            if phase.startswith("train"):
                xgboost_plust_ffm.experiment()
            else:
                xgboost_plust_ffm.experiment(DataManager.load_dataframe(df_path, 10000000))
        elif algo == "lightgbm_plus_ffm":
            lgbm_plust_ffm = LightGbmPlusFFMExperiment(config_params=config_param)
            phase = config_param[algo]["phase"]
            if phase.startswith("train"):
                lgbm_plust_ffm.experiment()
            else:
                lgbm_plust_ffm.experiment(DataManager.load_dataframe(df_path, 10000000))
        elif algo == "ffm":
            ffm = FFMExperiment(config_params=config_param)
            phase = config_param[algo]["phase"]
            if phase.startswith("train") or phase == "emsemble":
                ffm.experiment()
            else:
                ffm.experiment(DataManager.load_dataframe(df_path, 10000000))

    def run(self, samples_path, model_save_path, algo="ffm", params=None, df_path=None, channelid=4,
            phase="train"):
        if df_path is None and not os.path.exists(samples_path + ".pkl") and not os.path.exists(samples_path):
            print(samples_path + " not exists")
            return

        pipelineModel = None
        if df_path is None:
            """
            实际上这个分支已经不支持了
            """
            data_manager = DataManager(channelid=channelid, config_param=config_param)
            data_manager.loadLabeledPoint(samples_path)
            x, y = CtrExperiment.resamples(data_manager.data)
            pipelineModel = CtrExperiment.experiment(x, y, algo, params=params)
        else:
            config_param[algo]["phase"] = phase
            CtrExperiment.experiment(None, None, algo, params=params, df_path=df_path)

        if pipelineModel is not None:
            CtrExperiment.saveModel2PMMLFormat(pipelineModel, model_save_path)
            pickle.dump(pipelineModel,
                        open(config_param["workdir"][platform.system()] + algo + "_{}.pkl".format(channelid), "wb"))


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='''ctr experiment''', formatter_class=RawTextHelpFormatter)
    parser.add_argument("--channelid", required=True, default=4, help='渠道')
    parser.add_argument("--date", required=True, default="2018-08-09", help='样本截止日期')
    parser.add_argument("--algo", required=True, help='学习算法')
    parser.add_argument("--phase", required=True, default="train",
                        help='阶段选择，maybe train: train model, shallow: 生成浅层特征, complete:生成浅层+组合特征, scaler')

    try:
        arguments = parser.parse_args(args=arguments)
        arguments = vars(arguments)
    except:
        parser.print_help()
        sys.exit(0)

    return arguments


def run(argvs):
    parameters = parse_arguments(argvs)
    algo = parameters["algo"]
    channelid = parameters["channelid"]
    workdir = config_param["workdir"][platform.system()]
    config_param["channelid"] = channelid
    model_save_path = workdir + "{0}_channel_{1}.pmml".format(algo, channelid)

    ctr_experiment = CtrExperiment()
    ctr_experiment.run(workdir + "samples-optimization_{}.labeledpoint".format(channelid),
                       model_save_path, algo,
                       config_param[algo],
                       df_path=workdir + "samples-optimization_{}_{}.csv".format(channelid, parameters["date"]),
                       channelid=channelid, phase=parameters["phase"])


if __name__ == "__main__":
    config_param = yaml.load(open("../config.yml", "r", encoding="utf-8").read())
    run(sys.argv[1:])
