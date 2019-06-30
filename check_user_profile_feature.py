# -*- coding:utf-8 -*-
'''
Created on 2018/8/30

@author: kongyangyang
'''

if __name__ == "__main__":
    cnt = 0
    line_num = 0
    with open("/data/kongyy/ctr_online/samples-optimization_4.csv", "r", encoding="utf-8") as file_read:
        for line in file_read:
            line_num += 1
            if line_num == 1:
                continue
            items = [float(i) for i in line.strip().split(",")[-40:] if i != "0"]
            if len(items) > 0:
                print(min(items))
                cnt += 1
    print(cnt)
