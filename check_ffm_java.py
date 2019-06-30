# -*- coding:utf-8 -*-
'''
Created on 2018/9/26

@author: kongyangyang
'''
import math


def load_ffm(data_path):
    ffm = {"bias": 0, "w": {}, "v": {}}
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            key, value = line.strip().split(":")
            if key == "bias":
                ffm["bias"] = float(value.strip())
            elif key.startswith("i_"):
                ffm["w"][key] = float(value.strip())
            else:
                ffm["v"][key] = [float(it) for it in value.strip().split(" ")]
    return ffm


def load_field(data_path):
    field_name2id = {}
    feature_col_to_field_id = {}
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split(",")
            for idx, item in enumerate(items):
                _items = item.split(":")
                field = _items[0]
                if len(_items) == 3:
                    field += ":" + _items[1]
                if field not in field_name2id:
                    field_name2id[field] = len(field_name2id)

                feature_col_to_field_id[idx] = field_name2id[field]
        _size = len(feature_col_to_field_id)
        ntree = 20
        width = int(math.pow(2, 4))
        for t in range(ntree):
            for j in range(width):
                feature_col_to_field_id[_size + t * width + j] = len(field_name2id) + t

    return feature_col_to_field_id


def cal(data_path, ffm, feature_col_to_field_id):
    _size = len(ffm["w"])
    count = 0
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            count += 1
            if count > 20:
                break
            y = ffm["bias"]
            items = line.strip().split(" ")[1:]
            field_list = []
            idx_list = []
            value_list = []
            for item in items:
                field, idx, value = item.split(":")
                if int(idx.strip()) < _size:
                    field_list.append(field.strip())
                    idx_list.append(int(idx.strip()))
                    value_list.append(float(value.strip()))

            y += sum([ffm["w"]["i_{}".format(idx_list[i])] * value_list[i] for i in range(len(idx_list))])
            for i, idx in enumerate(idx_list):
                for j in range(i + 1, len(idx_list)):
                    if idx_list[j] > idx:
                        vi = ffm["v"]["v_{}_{}".format(idx, field_list[j])]
                        vj = ffm["v"]["v_{}_{}".format(idx_list[j], field_list[i])]

                        y += sum([vi[k] * vj[k] for k in range(len(vj))]) * value_list[i] * value_list[j]
                        # print(field_list[i],field_list[j], y, sum([vi[k] * vj[k] for k in range(len(vj))]), value_list[i] * value_list[j])
            print(1.0 / (1 + math.exp(-y)))

            # valueMap = {int(item.split(":")[1]): float(item.split(":")[-1]) for item in items}
            #
            # for item in items:
            #     field, idx, value = item.split(":")
            #     if int(idx) < _size:
            #         y += ffm["w"]["i_" + idx] * float(value)
            #         for col in range(int(idx) + 1, _size):
            #             if col in valueMap:
            #                 field2 = feature_col_to_field_id[col]
            #                 v1 = ffm["v"]["v_{}_{}".format(idx, field2)]
            #                 v2 = ffm["v"]["v_{}_{}".format(col, field)]
            #                 y += sum([v1[i] * v2[i] for i in range(len(v1))]) * float(value) * valueMap[col]
            # print(y)
            # print(1.0 / (1 + math.exp(-y)))


if __name__ == "__main__":
    feature_col_to_field_id = load_field("E:/Work/jobs/data/DSP/CTR预估/samples/model/featuresNames.txt")
    ffm = load_ffm("E:/Work/jobs/data/DSP/CTR预估/samples/model/ffm.txt")
    cal("E:/Work/jobs/data/DSP/CTR预估/samples/ffm_test_java.txt", ffm, feature_col_to_field_id)
