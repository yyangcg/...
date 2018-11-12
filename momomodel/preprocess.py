#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


# TODO 添加更多缺失值填充方法
def nan_replace(x, method=None):
    """

    :param x:
    :param method:
    :return:
    """
    if method is not None and method not in ["median", "mean"]:
        raise ValueError ("method must be one of %s " % repr (["median", "mean"]))
    replace_element = 0.0
    if method == "median":
        replace_element = np.nanmedian (x)
    elif method == "mean":
        replace_element = np.nanmean (x)
    return x.fillna (replace_element)
