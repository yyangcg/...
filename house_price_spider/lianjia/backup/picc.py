# -*- coding:utf-8 -*-
'''
Created on 2018/6/17

@author: kyy_b
'''
import re
from datetime import datetime
from PIL import Image
from carinsurance.base_simulation_access import *
from carinsurance.utils import *
from carinsurance.universal_verification import SlideImage
import numpy as np


class PICC(BaseSimulationAccess):
    def __init__(self, home_page_url):
        BaseSimulationAccess.__init__(self, home_page_url)
        self.uuid = ""
        self._load_area_code(config_param["work_dir"] + config_param['picc_area_code_path'])

        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "www.epicc.com.cn",
            "Origin": "http://www.epicc.com.cn",
            "Proxy-Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def login_page(self):
        self.driver.get(self.home_page_url)

        WebDriverWait(self.driver, self.wait_present).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="login-tabs"]/ul/li[2]')),
        )
        self.driver.find_element_by_xpath('//*[@class="login-tabs"]/ul/li[2]').click()

        user_id, passwd = config_param["userinfo"]["user"][self.random_select_user()].split(",")
        print("current user and pwd:", user_id, passwd)
        # 定位账号
        user_id_element = self.driver.find_element_by_xpath('//*[@id="entryId"]')
        user_id_element.send_keys(user_id)

        # 定位密码
        pwd_element = self.driver.find_element_by_xpath('//*[@id="password"]')
        pwd_element.send_keys(passwd)

        # 定位滑动按钮并滑动解锁
        link = self.driver.find_element_by_xpath('//*[@id="slideBar"]')
        self.driver.execute_script('$(arguments[0]).click()', link)

        # self.move()

        # 定位登录按钮
        link = self.driver.find_element_by_xpath('//*[@id="epiccLogin"]')
        self.driver.execute_script('$(arguments[0]).click()', link)

    def prepare_image(self):
        wait = WebDriverWait(self.driver, self.wait_present)
        # 点击拖动按钮，弹出有缺口的图片
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'captcha-box')))

        _style = self.driver.find_element_by_xpath('//*[@id="validateBox"]').get_attribute("style")
        style = {k.split(":")[0].strip(): k.split(":")[1].strip() for k in _style.split(";") if ":" in k}
        url = style["background"].split('url("/')[-1][:-2]
        number = url.split('.')[0][-1]
        img_topic = url.split("/")[1]
        print(style)

        # 下载缺口图片
        img_name2 = config_param["work_dir"] + config_param['verification_path'] + img_topic + "_slide{number}.png".format(number=number)
        print(style["top"].replace("px", ""), style["left"].replace("px", ""))

        if os.path.exists(img_name2):
            os.remove(img_name2)
        r = requests.get("http://www.epicc.com.cn/" + url)
        with open(img_name2, "wb") as f:  # 开始写文件，wb代表写二进制文件
            f.write(r.content)

        # 下载带缺口的背景图片
        img_name1 =  config_param["work_dir"] + config_param['verification_path'] + img_topic + "_grap{number}.png".format(number=number)
        if os.path.exists(img_name1):
            os.remove(img_name1)
        r = requests.get(
            "http://www.epicc.com.cn/" + "images_slide/" + img_topic + "/grap{number}.png".format(number=number))

        with open(img_name1, "wb") as f:  # 开始写文件，wb代表写二进制文件
            f.write(r.content)

        # 下载不带缺口的背景图片
        img_name3 =  config_param["work_dir"] + config_param['verification_path'] + img_topic + "_grayBack.png"
        if os.path.exists(img_name3):
            os.remove(img_name3)
        r = requests.get(
            "http://www.epicc.com.cn/" + "images_slide/" + img_topic + "/grayBack.png")

        with open(img_name3, "wb") as f:  # 开始写文件，wb代表写二进制文件
            f.write(r.content)

        return Image.open(img_name1), Image.open(img_name2), Image.open(img_name3), int(style["left"].replace("px", ""))

    def move(self):
        wait = WebDriverWait(self.driver, self.wait_present)
        image1, image2, image3, left = self.prepare_image()

        # 步骤七：按照轨迹拖动，完全验证
        button = wait.until(EC.presence_of_element_located((By.ID, 'slideBar')))
        max_offset = SlideImage.get_predict_ans(np.array(image3) - np.array(image1))

        for i in range(0, 20):
            dragger = self.driver.find_element_by_id("slideBar")
            action = ActionChains(self.driver)
            action.drag_and_drop_by_offset(dragger, xoffset=max_offset - left - i, yoffset=0).perform()

            # ActionChains(self.driver).click_and_hold(button).perform()
            # ActionChains(self.driver).move_by_offset(xoffset=max_offset - left - i, yoffset=0).perform()
            time.sleep(5)
            # ActionChains(self.driver).release().perform()
            if self.driver.find_element_by_xpath('//*[@id="slideBox"]/span[1]/img').get_attribute(
                    "src") == "/idprovider/images/images/success_bg_text.png":
                break

    def _load_area_code(self, data_path):
        """
        :param data_path:
        :return:
        """
        self.cityname_to_citycode = {}
        self.cityname_to_areacode = {}
        areacode_list = json.loads(open(data_path, "r", encoding="utf-8").read())
        for area_dict in areacode_list:
            area_code = area_dict["proid"]
            citys = area_dict['citys']
            for city_dict in citys:
                self.cityname_to_areacode[city_dict["cityname"]] = area_code
                self.cityname_to_citycode[city_dict["cityname"]] = city_dict["cityid"]

    def quote_price(self):
        # # 定位城市
        WebDriverWait(self.driver, self.wait_present).until(
            EC.visibility_of_element_located((By.NAME, "city_input"))
        )
        city_element = self.driver.find_element_by_xpath('//*[@id="city_input"]')
        city_element.clear()
        city_element.send_keys(config_param["city"])

        WebDriverWait(self.driver, self.wait_present).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="dimCityQuery"]/ul/li/a'))
        )
        self.driver.find_element_by_xpath('//*[@id="dimCityQuery"]/ul/li/a').click()
        time.sleep(0.5)

        # 定位车牌号
        if config_param['userinfo']["carID"] in ["无", "新车"]:
            self.driver.find_element_by_xpath('//*[@id="newcarbox1"]/span').click()
        else:
            self.driver.find_element_by_id('licenseNo').clear()
            self.driver.find_element_by_id('licenseNo').send_keys(config_param['userinfo']["carID"])

        # 获取报价
        link = self.driver.find_element_by_xpath('//*[@id="cxpressCarInsurce"]/form/div[4]/input')
        self.driver.execute_script('$(arguments[0]).click()', link)
        time.sleep(5)

    def skip_select_picc_again(self):
        all_hand = self.driver.window_handles
        self.driver.switch_to.window(all_hand[-1])
        wait_short = WebDriverWait(self.driver, self.wait_maybe_present)
        try:
            wait_short.until(EC.visibility_of_element_located((By.ID, "Skip_id")))
            self.init_uuid_car()
            # 跳过 欢迎您再次选择人保车险
            self.driver.find_element_by_id("Skip_id").click()
            time.sleep(1)
        except:
            print("用户为首次选择人保车险")

        try:
            wait_short.until(EC.visibility_of_element_located((By.CLASS_NAME, "a_already")))
            self.init_uuid_car()
            # 续保用户，车辆已过户?
            self.driver.find_element_by_class_name("a_already").click()
            time.sleep(1)
        except:
            print("非过户车")

    def fill_configuration_information(self):
        """
         填写车辆配置信息
        :return:
        """
        # 切换到当前页面句柄
        all_hand = self.driver.window_handles
        self.driver.switch_to.window(all_hand[-1])
        wait = WebDriverWait(self.driver, self.wait_present)

        # 发动机号, 车架号, 车主姓名, 证件号码, 邮箱
        value_list = [config_param["userinfo"]["engineSerialNumber"], config_param["userinfo"]["frameNumber"],
                      config_param["userinfo"]["userName"], config_param["userinfo"]["CardNoforUMS"],
                      config_param["userinfo"]["mail"]]
        elem_id_list = ['engineNo', 'frameNo', 'insuredName', 'insuredIDNumber', 'insuredEmail']
        name_list = ["发动机号", "车架号", "车主姓名", "证件号码", "邮箱"]
        for id_value in list(zip(elem_id_list, value_list, name_list)):
            wait.until(EC.visibility_of_element_located((By.ID, id_value[0])))
            try:
                yy = self.driver.find_element_by_id(id_value[0])
                yy.clear()
                yy.send_keys(id_value[1])
                time.sleep(0.5)
            except:
                print("不需要输入" + id_value[2])

        # 定位品牌型号
        wait.until(EC.visibility_of_element_located((By.ID, "VEHICLE_MODELSH")))
        try:
            self.driver.find_element_by_id('VEHICLE_MODELSH').send_keys(self.cur_model_name)
            # self.driver.find_element_by_id('vehicle_query').click()
            time.sleep(1)
        except:
            pass
            # traceback.print_exc()
            # wait.until(EC.visibility_of_element_located((By.ID, 'modelList0')))
            # self.driver.find_element_by_xpath('//*[@id="pop_bra1"]/div[1]/a').click()
            # time.sleep(3)
            # wait.until(EC.visibility_of_element_located((By.ID, "VEHICLE_MODELSH")))
            # self.driver.find_element_by_id('VEHICLE_MODELSH').send_keys(self.cur_model_name)
            # self.driver.find_element_by_id('vehicle_query').click()

        try:
            self.driver.find_element_by_id('vehicle_query').click()
        except:
            pass

        self.cur_save_file_name += self.cur_model_name + "_"
        time.sleep(2)
        result_code = self.select_style()
        if int(result_code) < 0:
            return result_code

        # 再次输入发动机号
        wait.until(EC.visibility_of_element_located((By.ID, 'engineNo')))
        try:
            yy = self.driver.find_element_by_id('engineNo')
            yy.clear()
            yy.send_keys(config_param["userinfo"]["engineSerialNumber"])
            time.sleep(0.5)
        except:
            print("不需要输入" + '发动机号')

        # 车辆注册日期

        try:
            wait.until(EC.visibility_of_element_located((By.ID, "enrollDate")))
            if self.driver.find_element_by_id('enrollDate').text == "":
                self.driver.execute_script("arguments[0].value=arguments[1]", self.driver.find_element_by_id("enrollDate"),
                                           config_param["userinfo"]["firstRegisterDate"])
                time.sleep(1.5)
        except:
            print("未正确输入注册登记时间")
            traceback.print_exc()

        # 商业险保单生效日期
        wait.until(EC.visibility_of_element_located((By.ID, "startDateBI")))
        try:
            self.driver.execute_script("arguments[0].value=arguments[1]", self.driver.find_element_by_id("startDateBI"),
                                       time.strftime("%Y/%m/%d", time.localtime(time.time() + 3600 * 24 * 2)))
            time.sleep(1.5)
        except:
            print("未正确输入商业险保单生效日期")

        # 获取精准报价
        WebDriverWait(self.driver, self.wait_present).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="toCalculate"]/input'))
        )
        link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
        self.driver.execute_script('$(arguments[0]).click()', link)
        time.sleep(1)
        try:
            # 商业险连接平台失败：指定查询地区代码值不在有效范围内。
            WebDriverWait(self.driver, self.wait_maybe_present).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/p'))
            )
            self.error_msg = self.driver.find_element_by_xpath(
                '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/p').text

            # 弹出系统推荐车型，选择一款
            WebDriverWait(self.driver, self.wait_maybe_present).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/input'))
            )
            # 点击 确定
            self.driver.find_element_by_xpath(
                '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/input').click()

            if len(self.error_msg) > 0 and re.search("系统已自动调整", self.error_msg) is None:
                return config_param["status"]['canNotSkipToInsurancePage']

            # 系统已自动调整
            link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
            self.driver.execute_script('$(arguments[0]).click()', link)
            time.sleep(1)
        except:
            traceback.print_exc()

        try:
            # 您的爱车品牌型号与车管所预留信息不符，请在列表中选择您的车辆
            cur_url = self.driver.current_url
            for i in range(2):
                WebDriverWait(self.driver, self.wait_maybe_present).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="pop_div pop_div4_tra"]'))
                )
                self.driver.find_element_by_xpath('//*[@id="traCarInfo"]/tbody/tr[i]/td[7]'.format(i=i + 1)).click()
                self.driver.find_element_by_xpath('//*[@id="selectTrueCar"]').click()
                time.sleep(1)
                link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
                self.driver.execute_script('$(arguments[0]).click()', link)
                all_hand = self.driver.window_handles
                self.driver.switch_to.window(all_hand[-1])
                if cur_url != self.driver.current_url:
                    return config_param["status"]["OK"]
        except:
            pass

        time.sleep(5)

        return config_param["status"]["OK"]

    def select_style(self):
        try:
            WebDriverWait(self.driver, self.wait_maybe_present).until(
                EC.presence_of_element_located((By.CLASS_NAME, "car-table"))
            )
        except:
            self.error_msg = "没有找到车型"
            return config_param["status"]['noFindModel']

        try:
            # self.skip_to_page(self.cur_table_page, '//*[@id="pop_bra1"]/div[2]/div[2]/div[2]/a[4]')
            table = self.driver.find_element_by_class_name('car-table')
            table_rows = table.find_elements_by_tag_name('tr')
            table_columns = table_rows[0].find_elements_by_tag_name('th')
        except:
            traceback.print_exc()
            print("cur table page = ", self.cur_table_page)
            return config_param["status"]['noNextStyle']

        print(self.cur_table_row, len(table_rows))
        time.sleep(1)
        if self.cur_table_row == len(table_rows):
            return config_param["status"]['noNextStyle']

        self.cur_style_name = ""
        for l in range(1, len(table_columns) + 1):
            if l == 4:
                self.cur_style_name += self.driver.find_element_by_xpath(
                    '//*[@id="modelList{0}"]/td[{1}]/p'.format(self.cur_table_row - 1, l)).text + "^"
            else:
                self.cur_style_name += self.driver.find_element_by_xpath(
                    '//*[@id="modelList{0}"]/td[{1}]'.format(self.cur_table_row - 1, l)).text + "^"

        # self.driver.find_element_by_xpath('//*[@id="modelList{0}"]/td[{1}]'.format(self.cur_table_row - 1, 4)).click()
        self.driver.execute_script("$(arguments[0]).click()",
                                   self.driver.find_element_by_xpath(
                                       '//*[@id="modelList{0}"]/td[{1}]'.format(self.cur_table_row - 1, 4)))

        time.sleep(2)

        self.cur_table_row += 1
        return config_param["status"]["OK"]

    def init_uuid_car(self):
        all_hand = self.driver.window_handles
        # 切换句柄
        self.driver.switch_to.window(all_hand[-1])
        self.uuid = self.driver.find_element_by_id('uniqueID').get_attribute("value")
        print('init_uuid_car', self.uuid)
        requests.post('http://www.epicc.com.cn/newecar/uuid/initUUidCar', headers=self.headers,
                      cookies=self.set_cookie(),
                      data={'uniqueID': self.uuid, 'vehicleModelsh': ''}
                      )

    def uuid_null_car(self):
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/backToCarPage'
        form_data = {
            'mainReqDto.pagestep': 'car',
            'insuredReqDtos[0].insuredFlag': '1000000',
            'insuredReqDtos[0].serialno': '1',
            'insuredReqDtos[1].insuredFlag': '0100000',
            'insuredReqDtos[1].serialno': '2',
            'insuredReqDtos[2].insuredFlag': '0010000',
            'insuredReqDtos[2].serialno': '3',
            'insuredReqDtos[3].insuredFlag': '0000000                 1     ',
            'insuredReqDtos[3].serialno': '4',
            'mainReqDto.isRenewal': '0',
            'mainReqDto.reuseFlag': '0',
            'TZFlag': '',
            'mainReqDto.areaCode': '13000000',
            'mainReqDto.cityCode': '13010000',
            'uniqueID': self.uuid,
            'licenseNo': '冀A1M7H7',
            'carReqDto.countryNature': '03',
            'serverDateTime': '2018/06/25',
            'carReqDto.frameNoFlag': '',
            'carReqDto.vinNoFlag': '',
            'carReqDto.engineNoFlag': '',
            'carReqDto.startdateFlagBI': '',
            'mainReqDto.packageType': '',
            'mainReqDto.entryID': '',
            'carReqDto.certificatedateSH': '',
            'carReqDto.engineno': '171540198',
            'carReqDto.frameno': 'LSGBC5343HG122189',
            'carReqDto.vehicle_modelsh': '别克SGM7152DMAB轿车',
            'carReqDto.carModelDetail': '威朗1.5L手动档别克SGM7152DMAB轿车 2015款 进取型 5座11.39万',
            'jyBrandName': '',
            'jyGroupName': '请选择',
            'jyDisplacement': '请选择',
            'jyGearboxName': '请选择',
            'jyParentVehName': '请选择',
            'jyFgwCode': '请选择',
            'carReqDto.aliasName': '',
            'carReqDto.seatcount': '5',
            'carReqDto.enrolldate': '2017/07/04',
            'mainReqDto.startDateBI': '2018/06/28',
            'mainReqDto.startHourBI': '0',
            'startHourBIReal': '0',
            'mainReqDto.endDateBI': '2019/06/27',
            'mainReqDto.endHourBI': '24',
            'carReqDto.haveOwnerChange': '',
            'platFormTrDate': '',
            'carReqDto.ownerChangeDate': '',
            'carReqDto.isHaveLoan': '0',
            'carReqDto.loanName': '',
            'insuredReqDtos[1].insuredname': '李泽',
            'insuredReqDtos[1].identifytype': '01',
            'insuredReqDtos[1].changeIdentifyFlag': '',
            'insuredReqDtos[1].identifyno': '130104198801015875',
            'insuredReqDtos[1].insuredSex': '1',
            'insuredReqDtos[1].birthday': '1988/01/01',
            'insuredReqDtos[1].age': '31',
            'insuredReqDtos[1].changeMobileFlag': '',
            'insuredReqDtos[1].mobile': '15510263256',
            'insuredReqDtos[1].changeEmailFlag': '',
            'insuredReqDtos[1].email': 'kyy_buaa2@163.com',
            'mainReqDto.soldierFlag': '',
            'insuredReqDtos[3].soldierrelations': '0',
            'insuredReqDtos[3].insuredname': '',
            'insuredReqDtos[3].soldieridentifytype': '000',
            'insuredReqDtos[3].soldieridentifynumber': ''
        }
        response = requests.post(
            'http://www.epicc.com.cn/newecar/interim/setUuidNullCar?time={time}'.format(time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=self.set_cookie(),
            data=form_data
        )
        print('uuid_null_car', response.status_code)

    def init_uuidid_calcu(self):
        """
        example: 0bf1edc2-037b-4e10-a430-935771c6665a
        :return:
        """
        self.headers['Referer'] = 'http://www.epicc.com.cn/newecar/proposal/loadCalculateInfo'
        response = requests.post('http://www.epicc.com.cn/newecar/uuid/initUUidCalcu', headers=self.headers,
                                 cookies=self.set_cookie(),
                                 data={'uniqueID': self.uuid}
                                 )
        print('init_uuid_calcu', response.status_code)

    def preForCalBI(self):
        'http://www.epicc.com.cn/newecar/proposal/preForCalBI?time=1529975831642'
        cookie = self.set_cookie()
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/backToCarPage'

        form_data = {
            'mainReqDto.pagestep': 'car',
            'insuredReqDtos[0].insuredFlag': '1000000',
            'insuredReqDtos[0].serialno': '1',
            'insuredReqDtos[1].insuredFlag': '0100000',
            'insuredReqDtos[1].serialno': '2',
            'insuredReqDtos[2].insuredFlag': '0010000',
            'insuredReqDtos[2].serialno': '3',
            'insuredReqDtos[3].insuredFlag': '0000000                 1     ',
            'insuredReqDtos[3].serialno': '4',
            'mainReqDto.isRenewal': '0',
            'mainReqDto.reuseFlag': '0',
            'TZFlag': '',
            'mainReqDto.areaCode': '13000000',
            'mainReqDto.cityCode': '13010000',
            'uniqueID': self.uuid,
            'licenseNo': '冀A1M7H7',
            'carReqDto.countryNature': '03',
            'serverDateTime': '2018/06/26',
            'carReqDto.frameNoFlag': '',
            'carReqDto.vinNoFlag': '',
            'carReqDto.engineNoFlag': '',
            'carReqDto.startdateFlagBI': '',
            'mainReqDto.packageType': '',
            'mainReqDto.entryID': '',
            'carReqDto.certificatedateSH': '',
            'carReqDto.engineno': '171540198',
            'carReqDto.frameno': 'LSGBC5343HG122189',
            'carReqDto.vehicle_modelsh': '别克SGM7152DMAB轿车',
            'carReqDto.carModelDetail': '威朗1.5L手动档别克SGM7152DMAB轿车 2015款 进取型 5座11.39万',
            'jyBrandName': '',
            'jyGroupName': '请选择',
            'jyDisplacement': '请选择',
            'jyGearboxName': '请选择',
            'jyParentVehName': '请选择',
            'jyFgwCode': '请选择',
            'carReqDto.aliasName': '',
            'carReqDto.seatcount': '5',
            'carReqDto.enrolldate': '2017/07/04',
            'mainReqDto.startDateBI': '2018/06/28',
            'mainReqDto.startHourBI': '0',
            'startHourBIReal': '0',
            'mainReqDto.endDateBI': '2019/06/27',
            'mainReqDto.endHourBI': '24',
            'carReqDto.haveOwnerChange': '',
            'platFormTrDate': '',
            'carReqDto.ownerChangeDate': '',
            'carReqDto.isHaveLoan': '0',
            'carReqDto.loanName': '',
            'insuredReqDtos[1].insuredname': '李泽',
            'insuredReqDtos[1].identifytype': '01',
            'insuredReqDtos[1].changeIdentifyFlag': '',
            'insuredReqDtos[1].identifyno': '130104198801015875',
            'insuredReqDtos[1].insuredSex': '1',
            'insuredReqDtos[1].birthday': '1988/01/01',
            'insuredReqDtos[1].age': '31',
            'insuredReqDtos[1].changeMobileFlag': '',
            'insuredReqDtos[1].mobile': '15510263256',
            'insuredReqDtos[1].changeEmailFlag': '',
            'insuredReqDtos[1].email': 'kyy_buaa2@163.com',
            'mainReqDto.soldierFlag': '',
            'insuredReqDtos[3].soldierrelations': '0',
            'insuredReqDtos[3].insuredname': '',
            'insuredReqDtos[3].soldieridentifytype': '000',
            'insuredReqDtos[3].soldieridentifynumber': ''
        }

        response = requests.post(
            'http://www.epicc.com.cn/newecar/proposal/preForCalBI?time={time}'.format(time=int(time.time() * 1000)),
            headers=self.headers, cookies=cookie, data=form_data)

        print("preForCalBI status = ", response.status_code)

    def is_reinsurance(self):
        """
        是否是转保客户
        :return:
        """
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "reinsuranceDiv"))
            )
        except:
            print("非转保客户")
            return False

        # 转保客户

        # 车辆识别码/车架号
        self.driver.find_element_by_id('frameNoBJ').send_keys(config_param["userinfo"]["frameNumber"])
        self.driver.find_element_by_id('engineNoBJ').send_keys(config_param['userinfo']['engineSerialNumber'])
        self.driver.find_element_by_id('carOwnerBJ').send_keys("张三")
        self.driver.find_element_by_id('reinsuranceBtn').click()
        return True

    def reinsuranceBJProposal(self):
        self.cur_save_file_name += self.cur_model_name + "_"
        result_code = self.select_style()
        if int(result_code) < 0:
            return result_code

        wait = WebDriverWait(self.driver, self.wait_present)
        # 商业险保单生效日期
        wait.until(EC.visibility_of_element_located((By.ID, "startDateBI")))
        try:
            self.driver.execute_script("arguments[0].value=arguments[1]",
                                       self.driver.find_element_by_id("startDateBI"),
                                       time.strftime("%Y/%m/%d", time.localtime(time.time() + 3600 * 2 * 24)))
            time.sleep(1.5)
        except:
            traceback.print_exc()
            print("商业险保单生效日期未正确输入")

        value_list = [config_param["userinfo"]["userName"], config_param["userinfo"]["CardNoforUMS"],
                      config_param["userinfo"]["mail"]]
        elem_id_list = ['insuredName', 'insuredIDNumber', 'insuredEmail']
        name_list = ["车主姓名", "证件号码", "邮箱"]
        for id_value in list(zip(elem_id_list, value_list, name_list)):
            wait.until(EC.visibility_of_element_located((By.ID, id_value[0])))
            try:
                yy = self.driver.find_element_by_id(id_value[0])
                yy.clear()
                yy.send_keys(id_value[1])
                time.sleep(0.5)
            except:
                pass
                print("不需要输入" + id_value[2])

        # 获取精准报价
        wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="toCalculate"]/input')))
        link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
        self.driver.execute_script('$(arguments[0]).click()', link)
        time.sleep(1)
        wait_short = WebDriverWait(self.driver, 5)
        try:
            # 商业险连接平台失败：指定查询地区代码值不在有效范围内。
            wait_short.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/p')))
            self.error_msg = self.driver.find_element_by_xpath(
                '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/p').text

            wait_short.until(EC.presence_of_element_located(
                (By.XPATH, '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/input')))
            self.driver.find_element_by_xpath(
                '//*[@class="pop_div1 pop_div pop_reminder helpReninder"]/div[2]/input').click()

            if len(self.error_msg) > 0 and re.search("系统已自动调整", self.error_msg) is None:
                return config_param["status"]['canNotSkipToInsurancePage']
            print(self.error_msg)
            link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
            self.driver.execute_script('$(arguments[0]).click()', link)
            time.sleep(1)
        except:
            traceback.print_exc()

        try:
            # 您的爱车品牌型号与车管所预留信息不符，请在列表中选择您的车辆
            cur_url = self.driver.current_url
            for i in range(2):
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="pop_div pop_div4_tra"]'))
                )
                self.driver.find_element_by_xpath('//*[@id="traCarInfo"]/tbody/tr[i]/td[7]'.format(i=i + 1)).click()
                self.driver.find_element_by_xpath('//*[@id="selectTrueCar"]').click()
                time.sleep(1)
                link = self.driver.find_element_by_xpath('//*[@id="toCalculate"]/input')
                self.driver.execute_script('$(arguments[0]).click()', link)
                all_hand = self.driver.window_handles
                self.driver.switch_to.window(all_hand[-1])
                if cur_url != self.driver.current_url:
                    return config_param["status"]["OK"]
        except:
            pass

        time.sleep(5)
        return config_param["status"]["OK"]

    def request_init_kind_info(self):
        """
        请求默认各个选项的 code 和 value
        在请求具体车险前使用
        examples:
            init_kind["amount050200"]
            init_kind['amount050200Min']
            init_kind['amount050200Max']
            for item in init_kind["items"]:
                {amountList: "0|10000|20000|30000|40000|50000|100000", kindCode: "050643", kindName: "精神损害抚慰金责任险"}
            init_kind["resUinqueMsg"] = ""
            init_kind["resUniqueCode"] = "0000"
            init_kind["resultCode"] = ""
            init_kind['resultMsg'] = ""
            init_kind['seatCount'] = 5
            init_kind['userpriceconf'] = 1
        :return:
        """
        'http://www.epicc.com.cn/newecar/calculate/initKindInfo'
        cookie = self.set_cookie()
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/loadCalculateInfo'

        response = requests.post(
            'http://www.epicc.com.cn/newecar/calculate/initKindInfo', headers=self.headers, cookies=cookie,
            data={"uniqueID": self.uuid})

        try:
            self.init_kind = json.loads(re.sub('\'', '\"', response.text))
        except:
            print(response.status_code, response.text)

    def quote_by_requests(self):
        """
        通过参数请求 完成全部的车险数据请求
        just for test
        :return:
        """
        # 获取精确报价

        detail_insurance_form_data = PICC._initial_insurance_form_data()

        cur_values = {
            'mainReqDto.areaCode': '13000000',
            'mainReqDto.cityCode': '13060000',
            'uniqueID': self.uuid,
        }

        detail_insurance_form_data = {
            'mainReqDto.pagestep': 'car',
            'insuredReqDtos[0].insuredFlag': '1000000',
            'insuredReqDtos[0].serialno': '1',
            'insuredReqDtos[1].insuredFlag': '0100000',
            'insuredReqDtos[1].serialno': '2',
            'insuredReqDtos[2].insuredFlag': '0010000',
            'insuredReqDtos[2].serialno': '3',
            'insuredReqDtos[3].insuredFlag': '0000000                 1     ',
            'insuredReqDtos[3].serialno': '4',
            'mainReqDto.isRenewal': '0',
            'mainReqDto.reuseFlag': '0',
            'TZFlag': '',
            'mainReqDto.areaCode': '13000000',
            'mainReqDto.cityCode': '13060000',
            'uniqueID': self.uuid,
            'licenseNo': '冀A1M7H7',
            'carReqDto.countryNature': '03',
            'serverDateTime': '2018/06/21',
            'carReqDto.frameNoFlag': '',
            'carReqDto.vinNoFlag': '',
            'carReqDto.engineNoFlag': '',
            'carReqDto.startdateFlagBI': '',
            'mainReqDto.packageType': '',
            'mainReqDto.entryID': '',
            'carReqDto.certificatedateSH': '',
            'carReqDto.engineno': '171540198',
            'carReqDto.frameno': 'LSGBC5343HG122189',
            'carReqDto.vehicle_modelsh': '别克SGM7152DMAB轿车',
            'carReqDto.carModelDetail': '威朗1.5L手动档别克SGM7152DMAB轿车 2017款 领先型 5座12.39万',
            'jyBrandName': '',
            'jyGroupName': '请选择',
            'jyDisplacement': '请选择',
            'jyGearboxName': '请选择',
            'jyParentVehName': '请选择',
            'jyFgwCode': '请选择',
            'carReqDto.aliasName': '',
            'carReqDto.seatcount': '5',
            'carReqDto.enrolldate': '2017/07/03',
            'mainReqDto.startDateBI': '2018/06/23',
            'mainReqDto.startHourBI': '0',
            'startHourBIReal': '0',
            'mainReqDto.endDateBI': '2019/06/22',
            'mainReqDto.endHourBI': '24',
            'carReqDto.haveOwnerChange': '',
            'platFormTrDate': '',
            'carReqDto.ownerChangeDate': '',
            'carReqDto.isHaveLoan': '0',
            'carReqDto.loanName': '',
            'insuredReqDtos[1].insuredname': '李泽',
            'insuredReqDtos[1].identifytype': '01',
            'insuredReqDtos[1].changeIdentifyFlag': '',
            'insuredReqDtos[1].identifyno': '130104198801015875',
            'insuredReqDtos[1].insuredSex': '1',
            'insuredReqDtos[1].birthday': '1988/01/01',
            'insuredReqDtos[1].age': '31',
            'insuredReqDtos[1].changeMobileFlag': '',
            'insuredReqDtos[1].mobile': '15510263256',
            'insuredReqDtos[1].changeEmailFlag': '',
            'insuredReqDtos[1].email': 'kyy_buaa2@163.com',
            'mainReqDto.soldierFlag': '',
            'insuredReqDtos[3].soldierrelations': '0',
            'insuredReqDtos[3].insuredname': '',
            'insuredReqDtos[3].soldieridentifytype': '000',
            'insuredReqDtos[3].soldieridentifynumber': ''
        }
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/normalProposal'
        response = requests.post('http://www.epicc.com.cn/newecar/proposal/preForCalBI?time={time}'.format(
            time=int(time.time()) * 1000 + 999), headers=self.headers, cookies=self.set_cookie(),
            data=detail_insurance_form_data)
        result_msg = json.loads(re.sub('\'', '\"', response.text))

        # 您的操作信息存在异常，可明天继续访问投保，如有疑问请拨打电话4001234567-2。
        self.error_msg = result_msg["resultMsg"]

    @staticmethod
    def _initial_insurance_form_data():
        return {'eadbuystyle': 1,
                'insuredcopies': 1,
                'othernumber': '',
                'othercopies': '',
                'yelAmount': '3000元',
                'yelPerminum': '100元',
                'yelengage': '本保单每份保险金额3000元。1.每次事故绝对免赔率为损失金额的10%。'
                             '2.特殊货物赔偿限额：购买单份保险的，手机、便携式摄影器材、便携式电脑、手提包、公文包类每类货物3000元；烟酒类每类货物2000元。购买多份保险的，赔偿限额按照投保份数累加，但最高不超过单份赔偿限额的3倍。'
                             '3.保险责任范围内的盗窃、抢劫、哄抢造成保险标的直接损失，无法提供或取得损失物品价值证明相关信息的，每次事故免赔率为损失金额的30%。'
                             '4.本保险扩展承保车辆玻璃贴膜损失责任，前挡玻璃、后挡玻璃、其他单片车窗玻璃贴膜的最高赔偿限额分别为500元、300元、200元。同一车辆购买多份的，赔偿限额最高不超过单份限额的2倍。'
                             '5.最高赔偿限额以保险单载明的保险金额为限。',
                'insuredYELcopies': 1,
                'uniqueID': "need_input",
                'isRenewal': 0,
                'reuseFlag': 0,
                'checkIsOffRenewal': 1,
                'areaCode': "need_input",
                'cityCode': "need_input",
                'lastBIPolicyNo': '',
                'ccaFlag': '',
                'userPriceConf': 1,
                'calInfoRollPos': '',
                'amount050200Min': "need_input",
                'amount050200Max': "need_input",
                'changeItemKind': 'need_input',
                'seatCount': "need_input",
                'useYears': "need_input",
                'TZFlag': '',
                'biselect': 1,
                'ciselect': 0,
                'BM_flag': 0,
                'isNeedCal': 1,
                'EADFlag': 0,  # 1, 与 eadsum 匹配
                'yelFlag': 0,  # 1
                'eadRenewalFlag': '',
                'eadsum': 0,  # 车上人员补充意外险, 90
                'sumYELpermium': 0,  # 随车行李保险, 100
                'isRevoke': '00',
                'backMobileNo': '',
                'isNeedCompare': 1,
                'checkEmail': '',
                'checkMobile': '',
                'sendEmail': '',
                'sendMobile': '',
                'entryID': '',
                'sumPremium': 0,
                'premiumCI': '0.00',
                'licenseFlag': 1,
                'rapidRenewalFlag': 0,
                'bonusEndDate': '',
                'haveOwnerSelect': '',
                'ownerChangeDateVal': '',
                'isHaveLoanFlag': '',
                'loanNameVal': '',
                'packageName': 'OptionalPackage',
                'startDateCI': "need_input",  # '2018/06/22'
                'startHourCI': 0,
                'endDateCI': "need_input",  # '2019/06/21'
                'endHourCI': 24,
                'payNo_sh': "",
                'department_sh': "",
                'taxFlag_sh': ""
                }

    def update_form_data(self, values):
        cur_form_data = PICC._initial_insurance_form_data().copy()
        cur_form_data.update(values)
        return cur_form_data

    def check_fill_configuration_information(self):
        """
        未完待续
        :return:
        """
        cookie = self.set_cookie()
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/backToCarPage'

        form_data = {'engineNo': config_param["engineSerialNumber"], 'uniqueID': self.uuid,
                     'areaCode': self.cityname_to_areacode[config_param['city']], 'countryNature': '',
                     'engineNoFlag': 1}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkEngineNo?time={time}'.format(time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=cookie,
            data=form_data)
        print("发动机 status = ", response.status_code)

        # 车架号
        form_data = {'frameNoObj': config_param['frameNumber'], 'uniqueID': self.uuid,
                     'areaCodeVal': self.cityname_to_areacode[config_param['city']],
                     'cityCodeVal': self.cityname_to_citycode[config_param['city']],
                     'EnrollDateVal': config_param["firstRegisterDate"], 'isRenewal': 0,
                     'frameNoFlag': 1}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkFrameNo?time={time}'.format(time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=cookie,
            data=form_data)
        print("车架号 status = ", response.status_code)

        # 车型
        form_data = {'carModelJYQuery.requestType': '02', 'carModelJYQuery.uniqueId': self.uuid,
                     'carModelJYQuery.areaCode': self.cityname_to_areacode[config_param['city']],
                     'carModelJYQuery.vehicleName': self.cur_model_name,
                     'carModelJYQuery.priceConfigKind': 2,
                     ' carModelJYQuery.engineDesc': "排量",
                     'carModelJYQuery.gearboxType': '档位',
                     'carModelJYQuery.pageNum': ''
                     }

        response = requests.post('http://www.epicc.com.cn/newecar/car/findCarModelJYQuery', headers=self.headers,
                                 cookies=cookie,
                                 data=form_data)
        print("车型 status = ", response.status_code)

        form_data = {'carModelQuery.requestType': '03',
                     'carModelQuery.areaCode': self.cityname_to_areacode[config_param['city']],
                     'carModelQuery.cityCode': self.cityname_to_citycode[config_param['city']],
                     'carModelQuery.uniqueId': self.uuid,
                     'carModelQuery.carModel': self.cur_model_name,  # '别克SGM7152DMAB轿车',
                     'carModelQuery.queryCode': 'SGM7152DMAB',
                     'carModelQuery.frameNo': '',
                     'carModelQuery.enrollDate': '',
                     'carModelQuery.parentId': '4028b2b64e28ee41014e43fb987a3510',
                     'carModelQuery.licenseType': '02',
                     'carModelQuery.engineNo': '',
                     'carModelQuery.findCarListfrom': '',
                     'carModelQuery.findCarByJYTime': '',
                     'carModelQuery.findCarByInput': '',
                     'carModelQuery.certificatedate': '',
                     'carModelQuery.startdatebi': time.strftime("%Y/%m/%d", time.localtime(time.time())),
                     'carModelQuery.starthourbi': 0,
                     'random': 0.3942096340559289
                     }

        response = requests.post('http://www.epicc.com.cn/newecar/car/findCarModel', headers=self.headers,
                                 cookies=cookie,
                                 data=form_data)
        print("车款 status = ", response.status_code)
        # seat
        form_data = {'seatCount': 5, 'uniqueID': self.uuid}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkSeatCount?time={time}'.format(time=int(time.time() * 1000)),
            headers=self.headers, cookies=cookie, data=form_data)
        print("seat status = ", response.status_code)

        # 注册日期
        form_data = {'uniqueID': self.uuid, 'areaCode': self.cityname_to_areacode[config_param['city']],
                     'cityCode': self.cityname_to_citycode[config_param['city']],
                     'startDateBI': time.strftime("%Y/%m/%d", time.localtime(time.time())),
                     'enrollDate': config_param["firstRegisterDate"].replace("-", '/'),
                     'isRenewal': 0, 'startHourBI': 0
                     }

        requests.post('http://www.epicc.com.cn/newecar/proposal/changeBIReal', headers=self.headers, cookies=cookie,
                      data=form_data)
        print("注册日期 status = ", response.status_code)

        # 姓名
        form_data = {'insuredName': config_param["userName"], 'uniqueID': self.uuid,
                     'areaCode': self.cityname_to_areacode[config_param['city']],
                     'cityCode': self.cityname_to_citycode[config_param['city']],
                     'isRenewal': 0}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkInsurdeName?time={time}'.format(
                time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=cookie,
            data=form_data)
        print("姓名 status = ", response.status_code)

        # 身份证
        form_data = {'insuredIDNumber': '130104198801015875', 'insuredIDType': '01', 'uniqueID': self.uuid,
                     'areaCode': 13000000}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkInsuredIDNumber?time={time}'.format(
                time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=cookie,
            data=form_data)
        print("身份证 status = ", response.status_code)

        # 邮箱
        form_data = {'email': 'kyy_buaa2@163.com', 'uniqueID': self.uuid}
        response = requests.post(
            'http://www.epicc.com.cn/newecar/ajaxcheck/checkInsuredEmail?time={time}'.format(
                time=int(time.time() * 1000)),
            headers=self.headers,
            cookies=cookie,
            data=form_data)
        print("邮箱 status = ", response.status_code)

    def show_car_info_log_all(self):
        cookie = self.set_cookie()
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/backToCarPage'
        response = requests.post(
            'http://www.epicc.com.cn/newecar/piccwxlog/showCarInfoLogAll', headers=self.headers, cookies=cookie,
            data={"uniqueID": self.uuid})
        print("show_car_info_log_all status = ", response.status_code)

    def construct_request_parameters_based_kindinfo(self):
        kindCode_dict = {"050231": [], '050252': [], '050600': [300000, 500000, 1000000]}
        kindCode_set = set([item["kindCode"] for item in self.init_kind["items"]])
        max_len = max([len(v) for v in kindCode_dict.values()])
        for item in self.init_kind['items']:
            if item['kindCode'] == "050231":
                kindCode_dict['050231'] = item['amountList'].split("|")[1:]
            elif item['kindCode'] == "050252":
                kindCode_dict['050252'] = item['amountList'].split("|")[1:]

        changeItemKind = {}
        for item in self.init_kind["items"]:
            if item["kindCode"] not in ['050600', "050231", "050252", "050701", '050702', "050643", "050210"]:
                changeItemKind[item["kindCode"]] = item['amountList'].split("|")[-1]
            elif item["kindCode"] in ["050701", '050702']:
                changeItemKind[item["kindCode"]] = 20000
            elif item["kindCode"] == "050643":
                changeItemKind[item["kindCode"]] = 10000
            elif item["kindCode"] == "050210":
                changeItemKind[item["kindCode"]] = 2000

        for kindcode in changeItemKind.keys():
            if kindcode not in kindCode_set:
                changeItemKind.pop(kindcode)
        if "050900" in changeItemKind:
            changeItemKind.pop("050900")

        changeItemKind_list = []
        for i in range(max_len):
            cur_changeItemKind = changeItemKind.copy()
            for kindcode, values in kindCode_dict.items():
                if len(values) == 0:
                    continue
                if i < len(kindCode_dict[kindcode]):
                    cur_changeItemKind[kindcode] = values[i]
                else:
                    cur_changeItemKind[kindcode] = values[-1]
            changeItemKind_list.append(",".join([k + ":" + str(v) for (k, v) in cur_changeItemKind.items()]) + ",")
        return changeItemKind_list

    def request_options(self):
        """
        请求不同险种的不同选项
        :param :
        :return:
        """
        cookie = self.set_cookie()
        self.headers["Referer"] = 'http://www.epicc.com.cn/newecar/proposal/loadCalculateInfo'

        values = {
            'eadbuystyle': 1,
            'insuredcopies': 1,
            'uniqueID': self.uuid,
            'amount050200Min': self.init_kind['amount050200Min'],
            'amount050200Max': self.init_kind['amount050200Max'],
            'seatCount': self.init_kind['seatCount'],
            'useYears': int(round((datetime.now() - datetime.strptime(config_param["userinfo"]["firstRegisterDate"],
                                                                      "%Y/%m/%d")).days / 365)),
            'packageName': 'OptionalPackage',
            'changeItemKind': '050200:106282.4,050600:300000',
            'startDateCI': time.strftime("%Y/%m/%d", time.localtime(time.time() + 24 * 3600)),
            # todo 判断是否是闰年
            'endDateCI': time.strftime("%Y/%m/%d", time.localtime(time.time() + 24 * 3600 * 365)),
            'areaCode': self.cityname_to_areacode[config_param["city"]],
            'cityCode': self.cityname_to_citycode[config_param['city']]
        }
        changeItemKind_list = self.construct_request_parameters_based_kindinfo()
        insurance_list = []

        for i in range(len(changeItemKind_list)):
            _values = values.copy()
            _values["changeItemKind"] = changeItemKind_list[i]
            cur_data = self.update_form_data(_values)

            response = requests.post(
                'http://www.epicc.com.cn/newecar/calculate/calculateBIForChangeItemKind?packageName=OptionalPackage&time={time}'.format(
                    time=int(time.time()) * 1000 + 999), headers=self.headers, cookies=cookie,
                data=cur_data)

            try:
                result = json.loads(re.sub('\'', '\"', response.text))
                if result["resultCode"] != "0000":
                    self.error_msg = result["resultMsg"]
                else:
                    optional_insurance = result["biviewmodel"]["opt"]
                    insurance_list.append([cur_data, optional_insurance])
            except:
                print(response.text)

        return insurance_list

    def run(self, examples_list):
        self.login_page()
        for K in range(0, len(examples_list)):
            for k, v in examples_list[K].items():
                if k == "city":
                    config_param[k] = examples_list[K][k]
                elif k == "CardNoforUMS":
                    config_param["userinfo"][k] = generate_idcard(examples_list[K][k], config_param["city"])
                else:
                    config_param["userinfo"][k] = examples_list[K][k]

            config_param["example"] = examples_list[K]["example"] + "\t" + config_param["userinfo"][
                "CardNoforUMS"]
            config_param["userinfo"]["mail"] = 'kyy_buaa@163.com'

            # config_param['userinfo']['firstRegisterDate'] = normalize_date_format(config_param['userinfo']['firstRegisterDate'])

            self.cur_model_name = examples_list[K]["model"]

            print("current examples: ", examples_list[K]["example"], "idcard = ",
                  config_param["userinfo"]["CardNoforUMS"])

            self.cur_table_row = 1

            if K > 0:
                self.driver.get("http://www.epicc.com.cn/")
            self.error_msg = ""
            self.quote_price()
            self.skip_select_picc_again()

            if self.is_reinsurance():
                if self.reinsuranceBJProposal() != config_param["status"]["OK"]:
                    save_finished_examples(config_param["work_dir"] + config_param["finished_filename"], examples_list[K]["example"],
                                           self.cur_style_name, self.error_msg)
                    continue
            else:
                if self.fill_configuration_information() != config_param["status"]["OK"]:
                    save_finished_examples(config_param["work_dir"] + config_param["finished_filename"], examples_list[K]["example"],
                                           self.cur_style_name, self.error_msg)
                    continue

            # ---------- 一下是通过 http 请求直接获取数据，尚未完成
            # self.preForCalBI()
            # self.show_car_info_log_all()
            # self.uuid_null_car()
            # self.init_uuidid_calcu()
            # self.check_fill_configuration_information()

            self.request_init_kind_info()
            # self.quote_by_requests()

            insurance_list = self.request_options()
            self.save_insurance_by_requests(examples_list[K], insurance_list)
            save_finished_examples(config_param["work_dir"] + config_param["finished_filename"], examples_list[K]["example"],
                                   self.cur_style_name, self.error_msg)


if __name__ == "__main__":
    home_page_url = "http://www.epicc.com.cn/idprovider/views/login.jsp?h=http://www.epicc.com.cn/"
    # data_dir = "E:/车险/人保/"
    data_dir = 'E:/Work/jobs/data/车险/人保/'
    finished_filename = "finished_examples_0705.txt"
    example_filename = "examples_0705.txt"

    picc_example_instance = PICC(home_page_url=home_page_url)

    open(data_dir + finished_filename, "a", encoding="utf-8").close()
    with open(data_dir + finished_filename, "r", encoding="utf-8") as file_read:
        finished_examples = [line.strip().split("\t")[0] for line in file_read]

    _examples_list = read_examples(data_dir + example_filename, "../data/city_licenceNo", finished_examples)
