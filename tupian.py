#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import random
import pymongo
import os
from lxml import etree
from bs4 import BeautifulSoup


DEFAULT_REQUEST_HEADERS = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Language': "zh-CN,zh;q=0.9",
    "Accept-Encoding":"gzip, deflate",
    'Referer':'https://www.612zh.com',
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


next_page_postfix = 'https://www.287zh.com'


def get_tiezi_data(url, Referer):  # 获取页面内所有帖子的链接，标题
    header = DEFAULT_REQUEST_HEADERS
    header['Referer'] = Referer
    all_tiezi_data = requests.get(url, headers=header).content
    soup = BeautifulSoup(all_tiezi_data, 'html.parser')
    body = soup.body
    try:
        data = body.find_all('a', {'class': 'video-pic loading'})
        for each in data:
            tiezi_link = next_page_postfix + each['href']
            tiezi_name = each['title']
            get_tupian_link(tiezi_name, tiezi_link, url)
            time.sleep(8 + random.randint(40, 160) / 10)
    except:
        print('该页面爬取不成功，正在重新爬取！')
        time.sleep(15 + random.randint(20, 100) / 20)
        get_tiezi_data(url)
    try:  # 获取下一页链接地址
        next_page = body.find('a', {'class':'next pagegbk'})
        next_page_url = next_page_postfix + next_page['href']
        time.sleep(15 + random.randint(10, 100) / 10)
        return next_page_url
    except:
        flag = 'No'
        return flag


def get_tupian_link(tiezi_name, tiezi_link, url):  # 获取帖子内所有图片的链接
    header = DEFAULT_REQUEST_HEADERS
    header['Referer'] = url
    tupian_link = []
    tiezi_data = requests.get(tiezi_link, headers=header).content
    soup = BeautifulSoup(tiezi_data, 'html.parser')
    body = soup.body
    try:
        details = body.find('div',{'class':'details-content text-justify'})
        data = details.find_all('img')
        for each in data:
            src = each['src']
            tupian_link.append(src)
        get_tupian_data(tiezi_name, tiezi_link, tupian_link)
    except:
        print('该帖子爬取不成功，正在重新爬取！')
        time.sleep(30 + random.randint(20, 100) / 20)
        get_tupian_link(tiezi_name, tiezi_link, url)


def get_tupian_data(tiezi_name, tiezi_link, tupian_link):  # 获取图片的数据
    try:
        tupian_data = []
        for each in tupian_link:
            s = requests.session()
            # s.keep_alive = False
            header = Header
            header['Referer'] = tiezi_link
            # print(DEFAULT_REQUEST_HEADERS)
            # print(header)
            req = s.get(each, headers=header)
            tupian_data.append(req.content)
        save_to_database_local(tiezi_name, tiezi_link, tupian_data, tupian_link)
    except:
        print('帖子图片数据获取不成功，正在重新爬取！')
        time.sleep(10 + random.randint(20, 100) / 20)
        get_tupian_data(tiezi_name, tiezi_link, tupian_link)


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
    url = ''
    Referer = ''
    zhang = url
    url = get_tiezi_data(url, Referer)
    while url != 'No':
        Referer = zhang
        zhang = url
        url = get_tiezi_data(url, Referer)
    print('爬取完毕！')
