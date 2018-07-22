# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 21:04:57 2018

@author: Xavier
"""

import requests
from requests.exceptions import RequestException
from urllib.parse import urlencode #用于在网址链接中加入参数
from multiprocessing import Pool
import json
from bs4 import BeautifulSoup
import re
import os
import time


def get_page_index(page, query_word):
    '''
    Desc:
        抓取通过offset实现Ajax异步加载的URL，返回当前offset的内容
    param:
        offset -- 为了实现Ajax异步加载，使用offset实现动态分页
        keyword -- 搜索用的关键词
    return:
        res.text -- 当前offset的requests.text内容
    '''
    url = 'https://image.baidu.com/search/index?'
    param = {
        'tn':'resultjson_com',
        'ipn':'rj',
        'ct':201326592,
        'is':'',
        'fp':'result',
        'queryWord':query_word,#用query_word参数传入
        'cl':2,
        'lm':-1,
        'ie':'utf-8',
        'oe':'utf-8',
        'adpicid':'',
        'st':'',
        'z':'',
        'ic':'',
        'word':query_word, #用query_word参数传入
        's':'',
        'se':'',
        'tab':'',
        'width':'',
        'height':'',
        'face':'',
        'istype':'',
        'qc':'',
        'nc':'',
        'fr':'',
        'pn':page, #用page参数传入
        'rn':30
    }
    url = url + urlencode(param)
    try:
        res = requests.get(url)
        res.encoding = 'utf-8'
        #返回的状态码是整型
        if res.status_code == 200:
            return res.text
        return None
    except RequestException:
        print("请求索引页面出错")
        return None


def parse_page_index(html):
    '''
    Desc:
        解析当前offset的requests.text内容
    param:
        html -- 当前offset的res.text内容
    return:
        item.get('article_url') -- 组图中的文章链接
    '''
    data = json.loads(html) #将网页的js数据格式转换为json
    if data and 'data' in data.keys():
        for item in data.get('data'):
            if item.get('middleURL') != None:
                yield item.get('middleURL')


def download_one_image(url, file_name):
    '''
    Desc:
        下载图片到指定的文件file_name中
    param:
        url -- 每一张图片的url
    '''
    print("正在下载", url)
    try:
        res = requests.get(url)
        if res.status_code == 200:
            if not os.path.exists(file_name):
                with open(file_name, 'wb') as f:
                    f.write(res.content)
                    f.close()
    except RequestException:
        print("下载图片出错")


# i=1
# # image_urls = []
# def main(page):
#     # global image_urls
#     global i
#     html = get_page_index(page, '猫')
#     for url in parse_page_index(html):
#         path = "I:/文档/爬虫数据/baidu_cat_images" #图片存储目录
#         if not os.path.exists(path):
#             os.mkdir(path)
#         file_name = '{0}/{1}{2}'.format(path, i, '.jpg')
#         download_one_image(url, file_name)
        # image_url = {}
        # image_url[str(i)] = url
        # image_urls.append(image_url)
        # i += 1
    # with open('result.json', 'a', encoding='utf-8') as f:
    #         f.write(json.dumps(image_urls, ensure_ascii=False) + '\n')


# if __name__ == '__main__':
#     start_page = 1
#     end_page = 3
#     groups = [i*30 for i in range(start_page, end_page)]
#     start_time = time.time()
#     pool = Pool()
#     pool.map(main, groups)
#     end_time = time.time()
#     print("cost time : %.2fs" % (end_time-start_time))


def main():
    i=1
    image_urls = []
    start_page = 1
    end_page = 3
    for page in range(start_page, end_page):
        html = get_page_index(30*page, '猫')
        for url in parse_page_index(html):
            print(url)
            path = "I:/文档/爬虫数据/baidu_cat_images" #图片存储目录
            file_name = '{0}/{1}{2}'.format(path, i, '.jpg')
            download_one_image(url, file_name)
            image_url = {}
            image_url[str(i)] = url
            image_urls.append(image_url)
            i += 1
    with open('result.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(image_urls, ensure_ascii=False) + '\n')

if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("cost time : %.2fs" % (end_time-start_time))