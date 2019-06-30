# -*- coding:utf-8 -*-
'''
Created on 2018/10/8

@author: kyy_b
'''
# 广告类资源
import sys
import json
import yaml
import platform

sys.path.append("../../")
from dsp.utils.database import MysqlClient


class AdResources:
    def __init__(self, config_param):
        self.mysql_client = MysqlClient(
            {'host': '172.16.208.128', 'port': 3306, 'user': 'dsptd_read', 'passwd': 'sCLIMSVm', 'db': 'auto_dsp',
             'charset': 'utf8'})
        self.config_param = config_param
        self.invalid_display_label = {"方法", "广告", "呵呵", '优质', '普通', '广告{MonthlyPayment}', '暂停',
                                      'abccde', '好的'}
        self.invalid_title = {"640-360-1.jpg", "哈哈哈"}

        self.creative_resources = self.load_creatives()
        self.meterial_resources = self.load_materials()

    def load_creatives(self):
        results = self.mysql_client.get_results(
            "select id as creative_id,advertiser_id,`name`,campaign_id, adgroup_id, `type`, creative_elements, created_at, updated_at from tb_creatives where created_at >= '2018-08-01'")

        creative_resources = {}

        for r in results:
            r["creative_id"] = str(r["creative_id"])
            creative_elements = json.loads(r["creative_elements"])[0]
            if "display_labels" in creative_elements:
                if creative_elements["display_labels"].isdigit() \
                        or creative_elements["display_labels"] in self.invalid_display_label:
                    continue

            if "title" in creative_elements:
                if creative_elements["title"] in self.invalid_title or creative_elements["title"].endswith("jpg") \
                        or "测试" in creative_elements["title"] or creative_elements["title"].isdigit():
                    continue
            # if "desc" in creative_elements:
            #     print(creative_elements["desc"])

            if r["creative_id"] not in creative_resources:
                creative_resources[r["creative_id"]] = {"display_labels": self.config_param["defaultID"],
                                                        "title": self.config_param["defaultID"],
                                                        "material_id": self.config_param["defaultID"],
                                                        "type": r["type"],
                                                        "created_at": r["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
                                                        "updated_at": r["updated_at"].strftime("%Y-%m-%d %H:%M:%S"),
                                                        "advertiser_id": r["advertiser_id"],
                                                        "campaign_id": r["campaign_id"],
                                                        "adgroup_id": r["adgroup_id"],
                                                        "name": r["name"]
                                                        # "desc": creative_elements["desc"]
                                                        }
            if "display_labels" in creative_elements:
                creative_resources[r["creative_id"]]["display_labels"] = creative_elements["display_labels"]
            if "title" in creative_elements:
                creative_resources[r["creative_id"]]["title"] = creative_elements["title"]
            if "image" in creative_elements:
                creative_resources[r["creative_id"]]["material_id"] = creative_elements["image"]["material_id"]

        return creative_resources

    def load_materials(self):
        results = self.mysql_client.get_results(
            "select id as meterical_id, width, height from tb_materials where created_at >= '2018-08-01'")
        return {str(r["meterical_id"]): {"width": r["width"], "height": r["height"]} for r in results}

    def save2file(self):
        creative_resources = self.load_creatives()
        with open(self.config_param["workdir"][platform.system()] + "ffm/creatives.txt", "w",
                  encoding="utf-8") as file_write:
            for cid, cinfo in creative_resources.items():
                file_write.write(
                    "\t".join([str(cid), cinfo["name"], cinfo["display_labels"],
                               ",".join([str(i) for i in cinfo["material_id"]]),
                               str(cinfo["type"]), cinfo["created_at"], cinfo["updated_at"]]) + "\n")
            file_write.write("99999999	99999999	99999999	99999999	99999999	2015-01-01	2015-01-01\n")

        materials_resources = self.load_materials()
        with open(self.config_param["workdir"][platform.system()] + "ffm/materials.txt", "w",
                  encoding="utf-8") as file_write:
            for mid, minfo in materials_resources.items():
                file_write.write("\t".join([str(mid), str(minfo["width"]), str(minfo["height"])]) + "\n")
            file_write.write("99999999	250	250\n")


if __name__ == "__main__":
    adresources = AdResources(config_param=yaml.load(open("config.yml", "r", encoding="utf-8").read()))
    # print({r["title"] for r in adresources.creative_resources.values()})
    adresources.save2file()
