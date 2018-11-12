import xlsxwriter
from bs4 import BeautifulSoup
import re
from urllib import request
from utils import generate_allurl,writer_to_text

#把应用名、类别、url、下载次数写入excel,因为只需要打开一次文件，所以把file和sheet定义为全局变量
def write_excel(name, type_name, url, download):
    # 全局变量row代表行号 0-4代表列数
    global row
    sheet.write(row, 0, row)
    sheet.write(row, 1, name)
    sheet.write(row, 2, type_name)
    sheet.write(row, 3, url)
    sheet.write(row, 4, download)
    row += 1


def get_list(url):
    # 请求url
    req = request.Request(url)
    # 设置请求头
    req.add_header("User-Agent", "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0")
    # 得到响应对象
    response = request.urlopen(req)
    # 得到Beautiful对象
    soup = BeautifulSoup(response, "html.parser")
    # 找到第一个class为key-select txt-sml的标签
    type_name = soup.find(attrs={"class": "key-select txt-sml"})
    # 找到所有应用名title所在的标签
    title_divs = soup.find_all(attrs={"class": "title"})
    applist = []
    for title_div in title_divs:
        if title_div.a is not None:
            name = title_div.a.text
            # a['href']得到a的herf属性内容
            url = "http://app.hicloud.com" + title_div.a['href']
            # string[3:]截取从第三个字符开始到末尾
            download = title_div.parent.find(text=re.compile("下载:"))[3:]
            try:
                applist.append([name, type_name.text])
            except:
                pass
    writer_to_text(applist)
    #         write_excel(name, type_name.text, url, download)
#
# #全局变量:row用来定义行数,方便写入excel行数一直累加,file和sheet因为创建一次就可以
# row = 1
# # 新建一个excel文件
# file = xlsxwriter.Workbook('applist1.xlsx')
# # # 新建一个sheet
# sheet = file.add_worksheet()


def get_data():
    # cities,pages = get_city_dict()
    # for i in range(len(cities)):
    #     user_in_nub = pages[i]
    #     city = cities[i]
    #     get_city_house(user_in_nub, city)

    urls = generate_allurl(91)
    for url in urls:
        print(url)
        get_list(url)




if __name__ == '__main__':
    #暂时列出两个类型
    # url_1 = "http://app.hicloud.com/soft/list_23"
    # url_2 = "http://app.hicloud.com/soft/list_24"
    #
    #
    # get_list(url_1)
    # get_list(url_2)
    # file.close()
    get_data()