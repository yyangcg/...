# -*- coding:utf-8 -*-
'''
Created on 2018/3/1

@author: kongyangyang
'''
from dsp.utils.database import MysqlClient
import json
import re


def explore_feature_values():
    results = mysql_client.get_results(
        "select id as creative_id,advertiser_id, `type`, creative_elements, created_at, updated_at from tb_creatives")

    creative_id_set = set()
    advertiser_id_set = set()
    type_set = set()
    display_labels_set = set()

    for r in results:
        creative_elements = json.loads(r["creative_elements"])[0]
        items = []
        if "display_labels" in creative_elements:
            if creative_elements["display_labels"] in ["奥迪", "风神", "觉醒", "汽车", "速派", "景逸", "一马", "大众", "优惠", "特惠", "明锐",
                                                       "汉腾", "马中", "陆风", "速腾", "借款", "促销", "起亚", "借贷", "买车", "宝骏", "红旗",
                                                       "江淮", "日产", "长马", '海马', '朗逸', '越野', '轿跑', '长安', '锐骐', 'S7', '东风']:
                items.append(r["creative_id"])

                if "title" in creative_elements:
                    items.append(creative_elements["title"])
                else:
                    items.append("无")

                if creative_elements["display_labels"] in ["优惠", "特惠", "借贷", "促销", "买车"]:
                    items.append(creative_elements["display_labels"])
                elif creative_elements["display_labels"] == "借款":
                    items.append("借款")
                else:
                    items.append("车型")

                if "image" in creative_elements:
                    items.append(",".join(creative_elements["image"]["material_id"]))
                else:
                    items.append("无")

                items.append(r["type"])
                items.append(r["created_at"].strftime("%Y-%m-%d"))
                items.append(r["updated_at"].strftime("%Y-%m-%d"))
            elif creative_elements["display_labels"] in ["方法", "广告", "呵呵",'优质', '普通', '广告{MonthlyPayment}', '暂停', 'abccde', '好的']:
                continue
            elif creative_elements["display_labels"].isdigit():
                continue
            else:
                continue
                # print(creative_elements["display_labels"])
        else:
            items.append(r["creative_id"])
            if "title" in creative_elements:
                items.append(creative_elements["title"])
            else:
                items.append("无")

            items.append("无")
            if "image" in creative_elements:
                items.append(",".join(creative_elements["image"]["material_id"]))
            else:
                items.append("无")
            items.append(r["type"])
            items.append(r["created_at"].strftime("%Y-%m-%d"))
            items.append(r["updated_at"].strftime("%Y-%m-%d"))

        if len("\t".join(str(i) for i in items)) > 0:
            print("\t".join(str(i) for i in items))

        # else:
        #     creative_id_set.add(r["creative_id"])
        #     if creative_elements["display_labels"] == "普通":
        #         print(r["creative_id"], r["type"], r["advertiser_id"], creative_elements)

        # type_set.add(r["type"])
        # advertiser_id_set.add(r["advertiser_id"])
        # creative_id_set.add(r["creative_id"])

    # print(display_labels_set)
    # print(type_set)
    # print(advertiser_id_set)
    # print(len(creative_id_set))

    # print(",".join([str(i) for i in creative_id_set]))

    # results = mysql_client.get_results("select id from tb_materials")
    # print(",".join([str(r["id"]) for r in results]))


def parse_citycode(data_path):
    provice_code = set()
    city_code = set()
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            items = line.strip().split("\t")
            if items[0].endswith("0000"):
                provice_code.add(items[0])
            elif items[0].endswith("00"):
                city_code.add(items[0])

    print(",".join(city_code))

    print(len(city_code))


def parse_placeid_and_adid(data_path):
    placeid_set = set()
    adid_set = set()
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            try:
                placeid, adid = line.upper().strip().split(",")
                if placeid.startswith("UNKNOWN"):
                    placeid_set.add("UNKNOWN")
                else:
                    placeid_set.add(placeid)

                if len(adid) > 0:
                    adid_set.add(adid)
            except:
                pass

    print(",".join(adid_set))
    print(",".join(placeid_set))


def explore_os_and_phonebrand(data_path):
    phone_brand = {"iPhone", "huawei", "oppo", "vivo", "xiaomi", "Honor", "meizu", "Samsung", "Gionee",
                   "nubia", "360", "Lenovo", "ZTE", "OnePlus", "Smartisan", "BlackBerry", "coolpad"}
    phone_brand = {item.lower() for item in phone_brand}
    n = 0
    with open(data_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            if len(phone_brand & set(re.split("[ ;]", line.strip().lower()))) > 0:
                n += 1
            else:
                pass
                print(line.strip())
    print(n)


if __name__ == "__main__":
    mysql_client = MysqlClient(
        {'host': '172.16.208.128', 'port': 3306, 'user': 'dsptd_read', 'passwd': 'sCLIMSVm', 'db': 'auto_dsp', 'charset': 'utf8'})

    # 创意 素材
    explore_feature_values()

    # city
    # parse_citycode("E:/Work/jobs/data/CTR预估/citycode.txt")

    # 手机品牌
    # explore_os_and_phonebrand("E:/Work/jobs/data/DSP/CTR预估/query_result.csv")
