#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/8/13 17:37
# @Author  : Yang Yuhan
from sklearn.model_selection import train_test_split
import pandas as pd
from feature_engineering import *
##格式转换
import datetime
import time


def build_model(Xtrain, label_train):
    from sklearn.ensemble import RandomForestClassifier

    # clf = RandomForestClassifier(n_estimators=128, n_jobs=-1, oob_score=True, random_state=13)
    # clf = RandomForestClassifier(n_estimators=128, n_jobs=-1, oob_score=False, random_state=13)
    clf = RandomForestClassifier(n_estimators=128, min_samples_leaf=25, max_features='sqrt', n_jobs=-1, oob_score=True,
                                 random_state=13)
    clf.fit(Xtrain, label_train)

    return clf


def predict_and_get_score(clf, Xtest):
    y_pred = clf.predict_proba(Xtest)
    label_pred = clf.predict(Xtest)
    score = y_pred[:, 1]
    return score, label_pred


def create_mysql_csv(y, proba, label_pred, filename):
    cols = ['user_id', 'y', 'proba', 'label_pred']

    # df = data_test.loc[:, mysql_cols]
    df = pd.DataFrame()
    # df['user_id'] = userid
    df['y_true'] = y
    df['proba'] = proba
    df['label_pred'] = label_pred

    df.to_csv(filename, index=False)

    return df


def calc_ks(data, n, prediction="prediction", label="label"):
    """
    calculate ks value
    :param data: DataFrame[prediction,label]
    :param n : int number of cut
    :param prediction: string name of prediction
    :param label: string name of label
    :return: array
    """
    data = data.sort_values(prediction, ascending=False)
    boolean = True
    while boolean:
        try:
            data[prediction] = pd.Series(pd.qcut(data[prediction], n, labels=np.arange(n).astype(str)))
        except ValueError:
            boolean = True
            n -= 1
        else:
            boolean = False
    count = data.groupby(prediction)[label].agg({'bad': np.count_nonzero, 'obs': np.size})
    count["good"] = count["obs"] - count["bad"]
    t_bad = np.sum(count["bad"])
    t_good = np.sum(count["good"])
    ks_vector = np.abs(np.cumsum(count["bad"]) / t_bad - np.cumsum(count["good"]) / t_good)
    return ks_vector


def calc_continus_ks(data, prediction="prediction", label="label"):
    """

    :param data:
    :param prediction:
    :param label:
    :return:
    """
    data = data.sort_values(prediction, ascending=False)
    count = data.groupby(prediction, sort=False)[label].agg({'bad': np.count_nonzero, 'obs': np.size})
    count["good"] = count["obs"] - count["bad"]
    t_bad = np.sum(count["bad"])
    t_good = np.sum(count["good"])
    ks_vector = np.abs(np.cumsum(count["bad"]) / t_bad - np.cumsum(count["good"]) / t_good)
    return ks_vector


def eval_ks(y_true, y_pred):
    target_oos = y_pred
    # rf_results = pd.DataFrame({'prediction':target_oos[:, 1],"label":y_true})
    rf_results = pd.DataFrame({'prediction': target_oos, "label": y_true})
    ks_dis = calc_ks(rf_results, 10, prediction="prediction")
    #     print(max(ks_dis))
    ks_cont = calc_continus_ks(rf_results, prediction="prediction")
    #     print(max(ks_cont))
    return max(ks_dis), max(ks_cont)


def main():
    print("Process running at {}".format(datetime.datetime.now()))
    start_time = time.time()

    # Get data
    # data_train, data_test = get_data(conf.data_dir,conf.data_dir)
    data_train = get_data(conf.data_dir)
    print("get_data is Finished!")
    userid,appname,cityid, provinceid, hour, devicetype, mobiletype, nettype = get_features(data_train)
    numeric_features = [hour]
    categorical_features = [cityid, provinceid, devicetype,mobiletype,nettype]

    # Feature transform
    X = feature_transform(categorical_features, numeric_features)
    # X.append(userid)
    print("feature_transform is Finished!")

    # Get label
    interest = get_interest(appname)
    Y = get_labels(interest)
    print("get_labels_train is Finished!")

    print("get_labels_test is Finished!!!")

    # split data train to train,valid
    X_train, X_valid, y_train, y_valid = train_test_split(X, Y[2], test_size=0.33, random_state=42)

    # Build_model

    clf = build_model(X_train, y_train)

    # # Get score
    # score_aug = predict_and_get_score(clf_aug, feature_test, label_test)
    # score_aug = pdo_transform(score_aug)
    proba, label_pred = predict_and_get_score(clf, X_valid)
    print(proba)

    # Save score data to csv
    df = create_mysql_csv(y_valid, proba, label_pred, 'valid_result.csv')

    print('Entire process took {} seconds.'.format(time.time() - start_time))
    # print('Waiting for next process....')


if __name__ == '__main__':
    main()
