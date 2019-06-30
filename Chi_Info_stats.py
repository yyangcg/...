
# coding: utf-8

import pandas as pd
import numpy as np


# Calculate Chi Value

def get_feature_list_dict(dataraw,FeatureList):
    """
    例子：feature = 'age'
        feature_list_dict['age'] = ['age_0', 'age_19', 'age_23', 'age_27', 'age_33']
    :param dataraw:
    :param FeatureList:
    :return:
    """
    feature_list_dict = dict()
    for feature in FeatureList:
        filter_col = [col for col in dataraw if col.startswith(feature)]
        feature_list_dict[feature] = filter_col
    return feature_list_dict


def get_pos_neg_counts(dataraw,FeatureList,pos_idx=1,neg_idx=0):
    """
    计算每个特征中正负样本的个数
    :param dataraw:
    :param FeatureList:
    :param pos_idx:
    :param neg_idx:
    :return:
    """
    feature_poscounts = dict()
    feature_negcounts = dict()
    for feature in FeatureList:
        for ele in feature_list_dict[feature]:
            feature_poscounts[ele] = dataraw[ele][pos_idx]
            feature_negcounts[ele] = dataraw[ele][neg_idx]
    return feature_poscounts,feature_negcounts

def cal_Chi(a,b,c,d):
    """
    calculate Chi value
    :param a: 包含该特征特征的正样本个数
    :param b: 包含该特征特征的负样本个数
    :param c: 不包含该特征特征的正样本个数
    :param d: 不包含该特征特征的负样本个数
    :return: 卡方值
    """
    m = int(a*d - c*b)
    n = int((a + b) * (c + d))
    x = m*m/(n + 0.0001)
    return x

# Calculate Information Gain

def calc_freq(df, feature_list_dict, feature):
    """
        calculate freq of x
    """
    featureList = feature_list_dict[feature]
    total = 0
    freq = dict()
    for feature in featureList:
        f = df[feature][1] + df[feature][0]
        freq[feature] = f
        total += f
    return freq, total, featureList


def calc_prob(df, feature_list_dict, feature):
    """
        calculate prob of x, P(X)
    """
    freq_dict, total, featureList = calc_freq(dataraw, feature_list_dict, feature)
    prob = dict()
    for f in featureList:
        p = float(freq_dict[f] / total)
        prob[f] = p
    return prob


def calc_condition_entropy(df, feature_list_dict, feature, prob):
    """
        calculate conditional entropy H(y|x)
    """
    condition_entropy = 0
    featureList = feature_list_dict[feature]
    for f in featureList:
        f1 = df[f][1]
        f0 = df[f][0]
        total = f1 + f0
        p1 = f1 / total
        p0 = f0 / total
        if p1 == 0:
            logp1 = 0
        else:
            logp1 = - p1 * np.log2(p1)
        if p0 == 0:
            logp0 = 0
        else:
            logp0 = - p0 * np.log2(p0)
        condition_entropy += (logp1 + logp0) * prob[f]
    return condition_entropy


def calc_ent(df):
    """
        calculate entropy y , H(Y)
    """
    f1 = df['type'][1]
    f0 = df['type'][0]
    total = f1 + f0
    p1 = f1 / total
    p0 = f0 / total
    ent = - p1 * np.log2(p1) - p0 * np.log2(p0)
    return ent


def calc_ent_grap(ent, conditional_ent):
    """
        calculate entropy grap
    """
    ent_grap = ent - conditional_ent

    return ent_grap



if __name__ == '__main__':
    # Calculate Chi Value
    dataraw = pd.read_csv(r'D:\201806\feature\feature_sum.csv')
    FeatureList = ["type"
        , "gender"
        , "age"
        , "interest"
        , "week"
        , "hour"
        , "province"
        , "adid"
        , "creativeid"
        , "advertiserid"
        , "material"
        , "display_label"
        , "createtype"
        , "nettype"
        , "mobiletype"
        ,"os"
        , "phonebrand"
        ,'placeid']
    feature_list_dict = get_feature_list_dict(dataraw,FeatureList)
    feature_poscounts,feature_negcounts = get_pos_neg_counts(dataraw,FeatureList,pos_idx=1,neg_idx=0)
    feature_detail_list = dataraw.columns
    c1 = feature_poscounts['type']
    c2 = feature_negcounts['type']
    feature_Chi = dict()
    for feature in feature_detail_list:
        a = feature_poscounts[feature]
        b = feature_negcounts[feature]
        c = c1 - a
        d = c2 - b
        feature_Chi[feature] = cal_Chi(a,b,c,d)
    feature_Chi_dict = sorted(feature_Chi.items(), key=lambda d: d[1], reverse=True)
    print(feature_Chi_dict)


    # Calculate Information Gain

    ent = calc_ent(dataraw)
    ent_grap_dict = dict()
    for feature in FeatureList:
        prob = calc_prob(dataraw, feature_list_dict ,feature)
        condition_entropy = calc_condition_entropy(dataraw, feature_list_dict ,feature,prob)
        ent_grap = calc_ent_grap(ent,condition_entropy)
        ent_grap_dict[feature] = ent_grap

    feature_Info_dict= sorted(ent_grap_dict.items(), key=lambda d:d[1], reverse = True)
    print(feature_Info_dict)
    # pd.DataFrame(dicta).to_csv(r'D:201806\feature\feature_entropy_new.csv',  encoding='utf-8')

