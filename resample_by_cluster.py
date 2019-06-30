# -*- coding:utf-8 -*-
"""
file name: resample_by_cluster.py
Created on 2018/10/29
@author: kyy_b
@desc: 对样本聚类，然后从每簇中采样
"""
import numpy as np
from sklearn import preprocessing
from sklearn.cluster import KMeans


# from sklearn.externals import joblib


def cluster_and_resample(dataframe, clusters=10, frac=1):
    """
    :param dataframe:
    :param clusters:
    :param frac: neg/pos
    :return: resampled x, y
    """
    header = list(dataframe.columns.values)
    df_pos = dataframe[dataframe["label"] == 1]
    df_neg = dataframe[dataframe["label"] == 0]

    x_pos = df_pos[header[1:]].values
    x_neg = df_neg[header[1:]].values
    min_max_scaler = preprocessing.MinMaxScaler().fit(x_neg)
    x_neg_scaled = np.around(min_max_scaler.transform(x_neg), 5)

    k_means = KMeans(init='k-means++', n_clusters=clusters, n_init=10, n_jobs=-1)
    k_means.fit(x_neg_scaled)

    # joblib.dump(k_means, "k_means.m")

    frac = min(1.0, frac * df_pos.shape[0] / df_neg.shape[0])

    neg_sampeles_list = []

    for label in range(clusters):
        cur_x = x_neg[k_means.labels_ == label, :]
        print(label, cur_x.shape)
        np.random.shuffle(cur_x)
        neg_sampeles_list.append(cur_x[:int(frac * cur_x.shape[0]), :])
    x_neg = np.vstack(neg_sampeles_list)
    y_neg = [0] * x_neg.shape[0]
    y_pos = [1] * x_pos.shape[0]

    return np.vstack([x_neg, x_pos]), np.array(y_neg + y_pos)


if __name__ == "__main__":
    pass
