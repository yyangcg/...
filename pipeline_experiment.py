# -*- coding:utf-8 -*-
'''
Created on 2018/10/16

@author: kyy_b
@desc: train  model 全流程
'''
import os
import sys
import smtplib
from email.mime.text import MIMEText
import yaml
import argparse
import platform
import sys
import subprocess
from argparse import RawTextHelpFormatter


def read_report(report_path):
    report = ""
    with open(report_path, "r", encoding="utf-8") as file_read:
        for line in file_read:
            report += line
    return report


def send_email():
    # 第三方SMTP服务
    mail_host = "smtp.163.com"  # 设置服务器
    mail_user = "kyy_buaa@163.com"  # 用户名
    mail_pass = "zxj15249241892"  # 密码
    receiver = 'kyy_buaa@163.com'  # 接收邮箱
    message = MIMEText(read_report(config_param["workdir"][platform.system()] + "report.txt"), 'plain', 'utf-8')
    message['From'] = 'Python' + '<' + mail_user + '>'
    message['To'] = receiver
    message['Subject'] = 'CTR 报告文件'

    try:
        smtpObj = smtplib.SMTP()  # 实例化
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        smtpObj.login(mail_user, mail_pass)  # 邮箱登录
        print('登录成功！')
        smtpObj.sendmail(mail_user, receiver, message.as_string())  # 发送邮件
        smtpObj.quit()  # 邮件退出
        print("邮件发送成功!")
    except smtplib.SMTPException:
        print("错误：无法发送邮件")


def get_featureNames(csv_path, feature_names_path, channelid):
    with open(feature_names_path, "a", encoding="utf-8") as file_write:
        with open(csv_path, "r", encoding="utf-8") as file_read:
            for line in file_read:
                file_write.write(channelid + "," + ",".join(line.strip().split(",")[1:]) + "\n")
                break


def pipeline(arguments):
    workdir = config_param["workdir"][platform.system()]

    # 特征工程
    if not os.path.exists(
            workdir + "samples-optimization_{0}_{1}.csv".format(arguments["channelid"], arguments["date"])):
        if os.path.exists(workdir + "samples-optimization_{}".format(arguments["date"])):
            # cmd = 'python feature_engineering.py  --channelid {channelid} --date {date} --format csv'.format(
            #     channelid=arguments["channelid"], date=arguments["date"])
            cmd = 'python feature_engineering_mult_threading.py  --channelid {channelid} --date {date} --format csv'.format(
                channelid=arguments["channelid"], date=arguments["date"])
            subprocess.call(cmd, shell=True)
        else:
            print("{dir}samples-optimization_{date} not exists".format(dir=workdir, date=arguments["date"]))
            sys.exit(0)

    if int(arguments["complete"]):
        # 全完特征
        cmd = 'python ctr_experiment.py  --channelid {channelid} --date {date} --phase complete --algo {algo}'.format(
            channelid=arguments["channelid"], date=arguments["date"], algo=arguments["algo"])
        print(cmd)
        subprocess.call(cmd, shell=True)

    if int(arguments["train_python"]):
        # train ffm
        cmd = 'python ctr_experiment.py  --channelid {channelid} --date {date} --phase train_python --algo {algo}'.format(
            channelid=arguments["channelid"], date=arguments["date"], algo=arguments["algo"])
        print(cmd)
        subprocess.call(cmd, shell=True)

    if int(arguments["ensemble"]):
        cmd = 'python ctr_experiment.py  --channelid {channelid} --date {date} --phase ensemble --algo {algo}'.format(
            channelid=arguments["channelid"], date=arguments["date"], algo=arguments["algo"])
        print(cmd)
        subprocess.call(cmd, shell=True)

    if int(arguments["scaler"]):
        cmd = 'python ctr_experiment.py  --channelid {channelid} --date {date} --phase scaler --algo {algo}'.format(
            channelid=arguments["channelid"], date=arguments["date"], algo=arguments["algo"])
        print(cmd)
        subprocess.call(cmd, shell=True)

    if int(arguments["featuresNames"]):
        get_featureNames(workdir + "samples-optimization_{}_{}.csv".format(arguments["channelid"], arguments["date"]),
                         workdir + "ffm/featuresNames.txt", arguments["channelid"])
        #os.rename(workdir + "ffm/ffm.txt", workdir + "ffm/ffm_{}.txt".format(arguments["channelid"]))

    if int(arguments["report"]):
        cmd = 'python ../report.py  --channelid {channelid} --date {date}'.format(channelid=arguments["channelid"],
                                                                                  date=arguments["date"])
        print(cmd)
        subprocess.call(cmd, shell=True)
        send_email()


def parse_arguments(arguments):
    parser = argparse.ArgumentParser(description='''FeatureEngineering''', formatter_class=RawTextHelpFormatter)
    parser.add_argument("--channelid", required=True, default=4, help='渠道')
    parser.add_argument("--date", required=True, help='样本截止日期')
    # parser.add_argument("--fe", required=True, help='特征工程')
    parser.add_argument("--complete", required=True, help='生成 ffm 所用特殊格式文件')
    parser.add_argument("--algo", required=True, help="学习算法")
    parser.add_argument("--train_python", required=True, help="模型训练")
    parser.add_argument("--ensemble", required=True, help="模型融合")
    parser.add_argument("--scaler", required=True, help="生成特征转化器")
    parser.add_argument("--featuresNames", required=False, help="生成java 所用特征名称")
    parser.add_argument("--report", required=False, default=0, help="发送报告信息")
    try:
        arguments = parser.parse_args(args=arguments)
        arguments = vars(arguments)
    except:
        parser.print_help()
        sys.exit(0)

    return arguments


if __name__ == "__main__":
    config_param = yaml.load(open("../config.yml", "r", encoding="utf-8").read())
    pipeline(parse_arguments(sys.argv[1:]))
