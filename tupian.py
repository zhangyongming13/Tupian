#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import random
import pymongo
import os
import re
import threading
from lxml import etree
from bs4 import BeautifulSoup
from get_proxy import main_get


DEFAULT_REQUEST_HEADERS = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Language': "zh-CN,zh;q=0.9",
    "Accept-Encoding":"gzip, deflate",
    'Referer':'https://www.882te.com',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Upgrade-Insecure-Requests':'1',
    'Content-Type':'application/x-www-form-urlencoded'}

Header = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding':'gzip, deflate, br',
    'accept-language':'zh-CN,zh;q=0.9',
    'cookie':'__cfduid=dcf33740dc664a9670366dbeba0c291cc1549158154',
    'Upgrade-Insecure-Requests':'1'
}


next_page_postfix = 'https://www.882te.com'


def get_tiezi_data(url, Referer, number_tiezi):  # 获取页面内所有帖子的链接，标题
    header = DEFAULT_REQUEST_HEADERS
    header['Referer'] = Referer
    all_tiezi_data = requests.get(url, headers=header).content
    soup = BeautifulSoup(all_tiezi_data, 'html.parser')
    body = soup.body
    degree = number_tiezi
    try:
        data = body.find_all('a', {'class': 'video-pic loading'})  #查看页面内所有的帖子
        ip_list = main_get()
        flag = 1
        for each in data[number_tiezi:]:
            if flag == 6:
                flag = 1
                ip_list = main_get()
            else:
                flag = flag + 1
            tiezi_link = next_page_postfix + each['href']  # 当数据中有attr选项的时候可以这样引用数据
            tiezi_name = each['title']
            get_tupian_link(tiezi_name, tiezi_link, url, ip_list)
            degree = degree + 1
            time.sleep(10 + random.randint(20, 100) / 20)
    except:
        print('该页面爬取不成功，正在重新爬取！')
        time.sleep(15 + random.randint(20, 100) / 20)
        get_tiezi_data(url, Referer, degree)
    try:  # 获取下一页链接地址
        next_page = body.find('a', {'class':'next pagegbk'})
        next_page_url = next_page_postfix + next_page['href']
        time.sleep(15 + random.randint(10, 100) / 10)
        return next_page_url
    except:
        flag = 'No'
        return flag


def get_tupian_link(tiezi_name, tiezi_link, url, ip_list):  # 获取帖子内所有图片的链接
    header = DEFAULT_REQUEST_HEADERS
    header['Referer'] = url
    tupian_link = []
    proxy = random.choice(ip_list)
    data_tz = requests.get(tiezi_link, headers=header, proxies=proxy)
    # print(data_tz.text)
    tiezi_data = data_tz.content
    soup = BeautifulSoup(tiezi_data, 'html.parser')
    body = soup.body
    try:
        details = body.find('div',{'class':'details-content text-justify'})
        data = details.find_all('img')
        for each in data:
            src = each['src']
            tupian_link.append(src)
        # get_tupian_data(tiezi_name, tiezi_link, tupian_link, ip_list)
        threading_for_get_tupiandata(tiezi_name, tiezi_link, tupian_link, ip_list)
    except:
        print('该帖子爬取不成功，正在重新爬取！')
        time.sleep(30 + random.randint(20, 100) / 20)
        get_tupian_link(tiezi_name, tiezi_link, url, ip_list)


class MyThread(threading.Thread):  # 类继承多线程的方法threading.Thread，并加入返回数据的方法
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args
        self.result = self.func(*self.args)  # 接收函数返回的数据

    def get_result(self):
        try:
            return self.result  # 返回结果
        except Exception:
            return None


def threading_for_get_tupiandata(tiezi_name, tiezi_link, tupian_link, ip_list):
    tupian_data = []
    print('正在爬取帖子： %s 的图片!!!' % tiezi_name)
    tupian_link_range = range(len(tupian_link))
    start_time = time.time()
    # 第一种多线程，为list里面的每一个dict元素创建一个进程，这样的做法导致了创建太多的进程
    # 导致验证IP地址所耗费的时间比单线程的还低 大概在17秒，如果减少for循环，这样可以降低到10秒左右
    threads = []
    for i in tupian_link_range:
        t = MyThread(get_tupian_data_requests, (tupian_link[i], tiezi_link,ip_list,), get_tupian_data_requests.__name__)
        t.start()
        threads.append(t)
    [t.join() for t in threads]
    for t in threads:
        result = t.get_result()
        if result != None:
            tupian_data.append(result)
            # print(result)
        else:
            pass
    save_to_database_local(tiezi_name, tiezi_link, tupian_data, tupian_link)


def get_tupian_data_requests(tupian_link, tiezi_link,ip_list):
    header = Header
    header['Referer'] = tiezi_link
    proxy = random.choice(ip_list)
    try:
        req = requests.get(tupian_link, headers=header, timeout=30, proxies=proxy)
        # print(req.text)
        if req.content:
            return req.content
        else:
            pass
    except Exception as e:
        print(e)


def get_tupian_data(tiezi_name, tiezi_link, tupian_link, ip_list):  # 获取图片的数据
    tupian_data = []
    print('正在爬取帖子： %s 的图片!!!' %tiezi_name)
    num = 0
    for each in tupian_link:
        num = num  + 1
        if num >= 50:
            print('循环爬取图片，退出循环！')
            break
        if re.match(r'[0-9a-zA-Z\_]*.gif', each):
            continue
        header = Header
        header['Referer'] = tiezi_link
        proxy = random.choice(ip_list)
        try:
            req = requests.get(each, headers=header, timeout=30, proxies=proxy)
            # print(req.text)
            if req.content:
                tupian_data.append(req.content)
            else:
                break
            print('第%d张图片爬取成功' % num)
        except:
            print('第%d张图片爬取不成功' % num)
    save_to_database_local(tiezi_name, tiezi_link, tupian_data, tupian_link)


def save_to_database_local(tiezi_name, tiezi_link, tupian_data, tupian_link):  # 保存图片的数据
    host = 'localhost'
    port = 27017
    dbname = 'tupian'
    sheetname = 'tupian'
    client = pymongo.MongoClient(host=host, port=port)
    mydb = client[dbname]
    post = mydb[sheetname]
    item = {}
    item['tiezi_name'] = tiezi_name
    item['tiezi_link'] = tiezi_link
    item['tupian_link'] = tupian_link
    post.insert(item)

    dir_name = tiezi_name
    if not os.path.exists(dir_name):  # 创建每个帖子对应的图片存放文件夹
        os.mkdir(dir_name)
    else:  # 已经存在文件夹，所以数据已经保存过了
        return None
    num = 1
    for each in tupian_data:
        file_name = str(num)
        num = num + 1
        with open('{}//{}.jpg'.format(dir_name, file_name), 'wb') as f:
            f.write(each)



if __name__ == '__main__':
    url = 'https://www.882te.com/html/news/69/'
    Referer = 'https://www.882te.com/html/news/7/'
    zhang = url
    number_tiezi = 1  # 记录爬取到页面内的第几个帖子
    url = get_tiezi_data(url, Referer, number_tiezi)
    while url != 'No':
        Referer = zhang
        zhang = url
        url = get_tiezi_data(url, Referer, number_tiezi)
    print('爬取完毕！')
