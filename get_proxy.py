#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import time
import random
import threading
import re


url_xici = 'https://www.xicidaili.com/nn/'
header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0', 'Connection':'keep-alive'}
header_ip3366 = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36'}
header_kuaidaili = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:65.0) Gecko/20100101 Firefox/65.0'}
url_check = 'http://www.baidu.com/s?wd=ip'
# url_check = 'https://movie.douban.com/subject/3878007/comments'


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


def threading_for_check_ip(uncheck_ip, ip_list):
    uncheck_ip_range = range(len(uncheck_ip))
    start_time = time.time()
    # 第一种多线程，为list里面的每一个dict元素创建一个进程，这样的做法导致了创建太多的进程
    # 导致验证IP地址所耗费的时间比单线程的还低 大概在17秒，如果减少for循环，这样可以降低到10秒左右
    threads = []
    for i in uncheck_ip_range:
        t = MyThread(check_ip, (uncheck_ip[i],), check_ip.__name__)
        t.start()
        threads.append(t)
    # for i in uncheck_ip_range:
    #     threads[i].start()
    # for i in uncheck_ip_range:
    #     threads[i].join()
    [t.join() for t in threads]
    # for i in uncheck_ip_range:
    #     result = threads[i].get_result()
    #     if result != None:
    #         ip_list.append(result)
    #         print(result)
    #     else:
    #         pass
    for t in threads:
        result = t.get_result()
        if result != None:
            ip_list.append(result)
            # print(result)
        else:
            pass
    print('Time_consuming:', time.time() - start_time)


# 返回的数据是一个list里面包含多个dict,dict的内容是protocol+ip+port
# dict样例 {'HTTP': '125.105.105.2319999'}
def get_ip_xici(html, uncheck_ip):
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('table', {'id':'ip_list'})
    ip_list = body.find_all('tr', {'class':'odd'})
    for i in ip_list:
        data = i.find_all('td')
        pro = {}
        ip = data[1].string
        port = data[2].string
        protocol = data[5].string
        pro[protocol] = ip + ':' + port
        uncheck_ip.append(pro)


# 返回的数据是一个list里面包含多个dict,dict的内容是protocol+ip+port
# dict样例 {'HTTP': '125.105.105.2319999'}
def check_ip(pro_ip):
        try:
            response = requests.get(url=url_check, proxies=pro_ip, timeout=5)
            if response.status_code == 200:
                return pro_ip
            else:
                return None
        except:
            pass


def save_to_txt(ip_list):
    with open('ip_list.txt', 'a', encoding='utf-8')as f:
        for i in ip_list:
            # print(i)
            for key, value in i.items():  # 将一个dict的key以及value同时获取的方法
                f.writelines(key + ':' + value + u'\n')
                # print(key + value)


def get_proxy_xici():
    start_time = time.time()
    page = 0
    next_page = url_xici
    ip_list = []
    uncheck_ip = []
    degree = 0
    while page < 2:
        try:
            html = requests.get(url=next_page, headers=header).content
            if html:
                get_ip_xici(html, uncheck_ip)
            # threading_for_check_ip(uncheck_ip, ip_list)
            page = page + 1
            if page == 2:
                break
            next_page = url_xici + str(page)
            page = int(page)
            time.sleep(20 + random.randint(20, 100) / 20)
        except Exception as e:
            print(e)
            if page > 0:
                page = page - 1
            time.sleep(40 + random.randint(20, 100) / 10)
    threading_for_check_ip(uncheck_ip, ip_list)
    # print(ip_list)
    end_time = time.time()
    print('爬取完毕，整个爬取时间：', end_time - start_time)
    return ip_list


def get_proxy_ip3366():
    start_time = time.time()
    url_ip3366 = 'http://www.ip3366.net/free/?stype=1&page={}'
    number = 1
    ip_list = []
    uncheck_ip_list = []
    while number < 3:
        try:
            html = requests.get(url_ip3366.format(str(number)), headers=header_ip3366).text
            ip_init = re.findall('<td>\d+\.\d+\.\d+\.\d+</td>', html)
            port_init = re.findall('<td>\d*</td>', html)
            proc_init = re.findall('<td>HTTP\w?</td>', html)
            split_built_init_data(ip_init, port_init, proc_init, uncheck_ip_list)
            number = number + 1
            time.sleep(14 + random.randint(20, 100) / 20)
        except Exception:
            print(Exception)
            if number > 1:
                number = number - 1
            time.sleep(40 + random.randint(20, 100) / 10)
    threading_for_check_ip(uncheck_ip_list, ip_list)
    end_time = time.time()
    print('爬取完毕，整个爬取时间：', end_time - start_time)
    return ip_list


def get_proxy_kuaidaili():
    start_time = time.time()
    url_kuaidaili = 'https://www.kuaidaili.com/free/inha/{}/'
    number = 1
    ip_list = []
    uncheck_ip_list = []
    while number < 3:
        try:
            html = requests.get(url_kuaidaili.format(str(number)), headers=header_kuaidaili).text
            ip_init = re.findall('<td data-title="IP">\d+\.\d+\.\d+\.\d+</td>', html)
            port_init = re.findall('<td data-title="PORT">\d*</td>', html)
            proc_init = re.findall('<td data-title="类型">HTTP\w?</td>', html)
            split_built_init_data(ip_init, port_init, proc_init, uncheck_ip_list)
            number = number + 1
            time.sleep(14 + random.randint(20, 100) / 20)
        except Exception:
            print(Exception)
            if number > 1:
                number = number - 1
            time.sleep(40 + random.randint(20, 100) / 10)
    threading_for_check_ip(uncheck_ip_list, ip_list)
    end_time = time.time()
    print('爬取完毕，整个爬取时间：', end_time - start_time)
    return ip_list


# 处理由正则表达式匹配到的数据，正则表达式匹配到的数据是这样的形式：<td data-title="IP">113.122.169.10</td>
# 需要先切割，然后找到数据，最后把ip、port和proc构建成这样的形式[{'HTTPS': '116.209.55.63:9999'}, {'HTTPS': '49.85.179.47:9999'}]
def split_built_init_data(ip_init, port_init, proc_init, uncheck_ip_list):
    for i in range(len(ip_init)):
        ip_init[i] = re.split('[><]+', ip_init[i])[2]
        port_init[i] = re.split('[<>]+', port_init[i])[2]
        proc_init[i] = re.split('[<>]', proc_init[i])[2]
    for i in range(len(ip_init)):
        dict = {}
        dict[proc_init[i]] = ip_init[i] + ':' + port_init[i]
        uncheck_ip_list.append(dict)


def main_get():
    number = [1, 2, 3]
    while True:
        flag = random.choice(number)
        # flag = 1
        ip_list = []
        if flag == 1:
            print('使用西刺代理！')
            ip_list = get_proxy_xici()
            if ip_list == []:
                number.remove(1)
            else:
                return ip_list
        elif flag == 2:
            print('使用IP66代理！')
            ip_list = get_proxy_ip3366()
            if ip_list == []:
                number.remove(2)
            else:
                return ip_list
        elif flag == 3:
            print('使用快代理！')
            ip_list = get_proxy_kuaidaili()
            if ip_list == []:
                number.remove(3)
            else:
                return ip_list


if __name__ == '__main__':
    final_list = main_get()
    print(final_list)
    # save_to_txt(final_list)
