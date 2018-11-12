import numpy as np
import pandas as pd
import config as conf
import csv


def get_data(training_filename, testing_filename = None):
    if testing_filename is not None:
        print("Loading data...")
        data_train = csv.reader(open(training_filename,'r',errors='ignore'))
        data_test = csv.reader(open(testing_filename,'r',errors='ignore'))
        print("Finished loading data.")
        return data_train, data_test
    else:
        print("Loading data...")
        data_train = csv.reader(open(training_filename,'r',errors='ignore'))
        print(data_train[0])
        print("Finished loading data.")
        print(len(data_train))
        return data_train

def get_ua(data):

    return data



def get_labels(data_train, data_test=None):

    if data_test is not None:
        data_train = pd.read_csv(data_train)
        data_test = pd.read_csv(data_test)
        return data_train.interest, data_test.interest
    else:
        data_train = pd.read_csv(data_train)
        return data_train.interest


def drop_columns(df):
    table_name = 'tmp_yicheapp_dsp_momo_20180830.'
    table_name = ''
    drop_useless_cols = [table_name + 'imei'
        ,table_name + 'imeimd5'
        ,table_name + 'timestamp'
        ,table_name + 'ip'
        ,table_name + 'provincename'
        ,table_name + 'cityname'
        ,table_name + 'bidid'
        ,table_name + 'channelid'
        ,table_name + 'mediaid'
        ,table_name + 'bidprice'
        ,table_name + 'price'
        ,table_name + 'cookie'
        ,table_name + 'pageurl'
        ,table_name + 'ordersn'
        ,table_name + 'campaignid'
        ,table_name + 'materialid'
        ,table_name + 'schedulingid'
        ,table_name + 'resulttype'
        ,table_name + 'creativeid'
        ,table_name + 'capfrequency'
        ,table_name + 'groupid'
        ,table_name + 'advertiserid'
        ,table_name + 'adid'
        ,table_name + 'adnetwork'
        ,table_name + 'dealid'
        ,table_name + 'ttdealid'
        ,table_name + 'agentprice'
        ,table_name + 'floorprice'
        ,table_name + 'mid'
        ,table_name + 'etl_dt'
        ,table_name + 'etl_hr']
    drop_might_be_useful_cols = [table_name + 'placeid'
                                ,table_name + 'mediadata'
                                , table_name + 'lon'
                                , table_name + 'lat']
    useful_col = [table_name + 'hour'
        ,table_name + 'province'
        ,table_name + 'city'
        ,table_name + 'ua'
        ,table_name + 'devicetype'
        ,table_name + 'mobiletype'
        ,table_name + 'nettype'
        ,table_name + 'mediadata'
        ,table_name + 'lon'
        ,table_name + 'lat']


    drop_total = list(set(drop_useless_cols + drop_might_be_useful_cols))
    print(len(drop_total),drop_useless_cols)
    df_modified = df.drop(drop_total, axis=1, errors='ignore')

    return df_modified





if __name__ == '__main__':
    # data_train, data_test = get_data(conf.data_dir,conf.data_dir)
    data_train = get_data(conf.data_dir)

    train = drop_columns(data_train)
