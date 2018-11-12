#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/26 10:04
# @Author  : Yang Yuhan
import pandas as pd
def writer_to_text(list):  # 储存到text
    with open('new4.text', 'a', encoding='utf-8')as f:
        for i in list:
            f.write(''.join([str(l) for l in i]))
            f.write('\n')
        f.close()

file = open('E:\project\stats.txt','r',encoding='utf-8')
# file = open('citycode.txt','r',encoding='utf-8')
# citydict = {}

def get_price():
    file = open('E:\project\stats.txt', 'r', encoding='utf-8')
    data = []
    names = []
    area_average = {}
    metre_average = {}
    average = {}
    for l in file:
        items = l.strip().split('\t')
        name = items[1]
        names.append(name)
        data.append(items)

    for i in set(names):
        p = 0
        num = 0
        a = 0
        for line in data:
            if line[1] == i:
                p += int(line[5])
                num += int(line[4])
                a += int(line[2])*int(line[4])
        metre_average[i] = p*10000/(a+0.1)
        average[i] = p/num
        area_average[i] = a/num
    print(area_average.get('领秀翡翠墅'))

    for k in data:
        key = k[1]
        k.append(average.get(key))
        k.append(metre_average.get(key))
        k.append(area_average.get(key))

    writer_to_text(list(data))


def get_code(file):
    citydict = {}
    for l in file:
        items = l.strip().split()
        citydict[items[1]] = items[0]
    return citydict


def get_citycode():
    city = open('E:\project\\new.txt', 'r', encoding='utf-8')
    file = open('citycode.txt','r',encoding='utf-8')

    citydict = get_code(file)

    for line in city:
        line = line.strip('\t')
        a = []
        if len(line) == 0:
            eles = 'qq'
        else:
            eles = citydict.get(str(line) + '区',line)
            if eles == line:
                eles = citydict.get(str(line) + '县',line)
                if eles == line:
                    eles = citydict.get(str(line) + '市', line)
                    if eles == line:
                        eles = citydict.get(str(line), line)
                        if eles == line:
                            eles = ''

        a.append(eles)
        eles[1] = citydict.get(eles[1] + '区','')
    writer_to_text(list(a))



def get_citycode_add():
    city = open('new.txt', 'r', encoding='utf-8')
    file = open('citycode.txt','r',encoding='utf-8')

    citydict = get_code(file)
    a = []
    for line in city:
        items = line.strip('\n').split('\t')

        if len(items[1]) == 0:
            eles = citydict.get(str(items[0]),'')
        else:
            eles = items[1]
        # else:
        #     eles = citydict.get(str(line) + '区',line)
        #     if eles == line:
        #         eles = citydict.get(str(line) + '县',line)
        #         if eles == line:
        #             eles = citydict.get(str(line) + '市', line)
        #             if eles == line:
        #                 eles = citydict.get(str(line), line)
        #                 if eles == line:
        #                     eles = ''

        a.append(eles)
        # eles[1] = citydict.get(eles[1] + '区','')
    writer_to_text(list(a))

if __name__ == '__main__':
    get_citycode_add()

