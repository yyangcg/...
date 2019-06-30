# -*- coding:utf-8 -*-
"""
file name: down_sample_by_dist.py
Created on 2018/11/8
@author: kyy_b
@desc: 根据数据的分布下采样
"""
import math
from joblib import Parallel, delayed


def down_sample(dataframe, frac):
    m, n = dataframe.shape
    nonzero_list = dataframe.astype(bool).sum(axis=0).values.tolist()
    headers = dataframe.columns.values
    nonzero_list_lg = []
    for i in nonzero_list:
        if i > 0:
            nonzero_list_lg.append(math.log10(i))
        else:
            nonzero_list_lg.append(0)

    def _fun(row, headers, nonzero_list_lg):
        return sum([nonzero_list_lg[i] for i in range(n) if row[headers[i]] != 0])

    results = Parallel(n_jobs=-1)(
        delayed(_fun)(row, headers, nonzero_list_lg) for index, row in dataframe.iterrows())

    return dataframe.sample(frac=frac, weights=results)


if __name__ == "__main__":
    pass
