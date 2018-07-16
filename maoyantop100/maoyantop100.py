# -*- coding: utf-8 -*-
"""
Created on Mon Jul 16 19:48:31 2018

@author: Xavier
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from multiprocessing import Pool
import time

def get_one_page_soup(url):
    '''
    Desc:
        用BeautifulSoup解析一页中的电影信息，并返回单页的soup信息
    param:
        url -- 单页的链接地址
    return:
        soup -- 用BeautifulSoup解析的单页的内容
    '''
    headers = {'user-agent':'Mozilla/5.0'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup


def one_page_parser(soup):
    '''
    Desc:
        用于解析单页的电影信息内容，并返回一个电影信息列表
    param:
        soup -- 用BeautifulSoup解析的单页的内容
    return:
        movies -- 单页的电影信息列表，列表中的每一个元素存储了一个字典，字典中包含了一部电影信息
    '''
    index = list(range(0,20,2)) #遍历每一页中的个电影
    movies = [] #列表中的每一个元素存储了一个字典，字典中包含了一部电影信息
    for i in index:
        movie_info = {}
        #1电影名字
        movie_name =  soup.select('.board-wrapper dd a')[i]['title']
        #2主演
        stars = soup.select('.board-wrapper .star')[int(i/2)].text.lstrip('\n                主演：').rstrip('\n ')
        #3上映时间
        release_time = soup.select('.board-wrapper .releasetime')[int(i/2)] \
        .text.split('上映时间：')[-1].split('(')[0]
        #4上映地点
        release_place = soup.select('.board-wrapper .releasetime')[int(i/2)] \
        .text.split('上映时间：')[-1].split('(')[-1].split(')')[0]
        #5排名
        rank = soup.select('.board-wrapper dd i')[int(i/2*3)].text
        #6得分
        score = soup.select('.board-wrapper dd i')[int(i/2*3)+1].text + \
        soup.select('.board-wrapper dd i')[int(i/2*3)+2].text
        #7海报图片链接
        image_link = soup.select('.board-wrapper dd img')[i+1]["data-src"] #0,1,2表示第一步影片

        movie_info['movie_name'] = movie_name #电影名字
        movie_info['stars'] = stars #主演
        movie_info['release_time'] = release_time #上映时间
        movie_info['release_place'] = release_place #上映地点
        movie_info['rank'] = rank #排名
        movie_info['score'] = score #得分
        movie_info['image_link'] = image_link #海报图片链接
        movies.append(movie_info)
    return movies


def write_to_file(movies_list):
    '''
    Desc:
        将单页的电影信息列表存储为json格式
    param:
        movies_list -- 单页的电影信息列表
    '''
    file_name = 'movies.json'
    with open(file_name, 'a', encoding='utf-8') as f:
        json.dump(movies_list, f, ensure_ascii=False)

def main():
    movies_lists = []
    for i in range(10):
        url = 'https://maoyan.com/board/4?offset=' + str(i*10) #总共10页，构建每一页的url
        soup = get_one_page_soup(url)
        movies_list = one_page_parser(soup)
        movies_lists.extend(movies_list)
        write_to_file(movies_list)
    ##3.使用pandas整理数据
    # df = pd.DataFrame(movies_lists) 
    # print(df)


if __name__ == '__main__':
    start_time = time.time()
    main()
    end_time = time.time()
    print("cost time : %.2fs" % (end_time-start_time))
    