# 爬虫请求
import requests
# 正则表达式
import re
# url参数转码
from urllib import parse
# 记录时间
import time
# 进程池
from multiprocessing import Pool
# 网页源代码解析
from bs4 import BeautifulSoup
# 表格话显示
from prettytable import PrettyTable
# 文件夹操作
import os
# 引入代理方法
import http_proxy as proxy

# 正则解析
content_rule = re.compile(r'<dt>.*正文</dt>(.*?)</dl>',re.S)
url_rule = re.compile(r'<a href="(.*?)">',re.S)

headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",}

# 代理变量全局处理，被网站封了以后，重新请求
global proxies
proxies = {}

#创建文件夹，并切换到该目录
def mkdir(path):
    path = path.strip()
    isExists = os.path.exists(path)
    if not isExists:
        print('创建名字叫做', path, '的文件夹')
        os.makedirs(path)

    else:
        print(path, '文件夹已经存在')

# 下载章节
def get_chapter(url):
    global proxies
    # 如果请求次数过多，大概率被封
    time.sleep(0.5)
    response = requests.get(url, headers=headers,proxies=proxies)
    # 网站经常会触发反爬机制，先进行返回结果状态判断
    code = response.status_code
    # 如果触发反爬机制，获取代理后重新请求
    while (code == 503):
        proxies = proxy.get_proxy()
        response = requests.get(url, headers=headers,proxies=proxies, verify=False,)
        code = response.status_code
    html = response.text
    bs = BeautifulSoup(html,"lxml")
    title = bs.find("h1").text.strip()
    print(title + "，下载成功")
    content = bs.select("#content")[0]
    # 添加标题
    text = title + "\n"
    # 正文拼接成字符串
    for item in content.select("p"):
        if (item.text.strip()):
            text += item.text.strip().strip(";") + "\n"
    # 写入文件
    with open(title+".txt","w") as file:
        file.write(text)

# 获取需要下载的小说目录
def get_menu(url):
    response = requests.get(url,headers=headers)
    html = response.text
    bs = BeautifulSoup(html,"lxml")
    title = bs.find("h1").text
    book_dir = "./"+title+"/"
    # 创建小说名的文件夹，切换到该目录
    mkdir(book_dir)
    os.chdir(book_dir)
    # 解析页面获取目录链接
    content = re.findall(content_rule,html)[0]
    menu_list = re.findall(url_rule,content)
    time1 = time.time()
    print(title,"，开始下载！")
    # 代理变量全局维护，被网站封了再重新请求
    global proxies
    proxies=proxy.get_proxy()

    # 多进程异步并不能提高效率，所以放弃了
    # p = Pool(8)
    # for url in menu_list:
    #     p.apply_async(get_chapter,(url,proxies,))
    # p.close()
    # p.join()
    for url in menu_list:
        get_chapter(url)
    time2 = time.time()
    print('耗时：',time2-time1)

# 搜索想要下载的小说链接
def get_book():
    url="http://www.b520.cc/modules/article/search.php?searchkey="
    while True:
        # 获取搜索结果
        searchkey = input("请输入想要搜索的小说或作者：")
        response = requests.get(url + parse.quote(searchkey, "gbk"), headers=headers)
        html = response.text
        result_list = []
        bs = BeautifulSoup(html, "lxml")
        # 获取记录条数
        count = len(bs.select("tr")) - 1
        # 如果没有结果，重新搜索
        if count == 0:
            print("没有搜索结果，请重试！")
            continue
        tr_list = bs.select("tr")
        # 表格规范显示列表信息
        table=PrettyTable()
        for index, tr in enumerate(tr_list):
            result = []
            # 标题行单独处理
            if index == 0:
                result = ["编号","小说链接","文章名称","最新章节","作者","字数","最后更新","状态"]
                table.field_names =result
                result_list.append(result)
                continue
            result.append(index)
            # 获取小说链接
            href = tr.find("a").get("href")
            result.append(href)
            # 其他内容都是td的文本内容
            for item in tr.select("td"):
                result.append(item.text)
            table.add_row(result)
            result_list.append(result)
        print(table)
        # 选择下载的小说
        index = int(input(f"一共有{count}条搜索结果，请输入需要下载的小说编号："))
        book_url = result_list[index][1]
        # 先获取小说的目录进行下载
        get_menu(book_url)

if __name__=='__main__':
    get_book()

