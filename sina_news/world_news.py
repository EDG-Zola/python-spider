# -*- coding: utf-8 -*-
"""
这是一个抓取当天的新浪新闻中国际新闻的爬虫
"""

import re
import requests
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup

def getCommentsCount(newsurl):
    '''获取单个新闻正文后面的评论数'''
    m = re.search('doc-i(.*).shtml',newsurl)#使用正则表达式搜索newsid
    newsid = m.group(1) #参数1表示只搜索通配符*中的内容，0表示搜索引号中''全部的内容
    res_comments = requests.get(news_comments_url.format(newsid)) #news_comments_url这个参数在函数外定义
    news_comments_json = json.loads(res_comments.text.strip('var data=')) #加载json数据
    total_comments_number = news_comments_json['result']['count']['show']
    return total_comments_number

#建立评论数抽取函数式
##验证函数getCommentsCount
#single_news_url = 'http://news.sina.com.cn/w/2018-07-09/doc-ihezpzwu8436387.shtml'
#getCommentsCount(single_news_url)


def getNewsContend(newsurl):
    '''传入单个新闻的url,返回该新闻的标题、时间与来源、文章正文内容、责任编辑、评论数'''
    result = {}
    res = requests.get(single_news_url)
    res.encoding = 'utf-8'

    #用BeautifulSoup解析网页
    soup = BeautifulSoup(res.text, 'html.parser')
    #抓取新闻标题
    result['title'] = soup.select('.main-title')[0].text
    news_time_str = soup.select('.date-source')[0].contents[1].text
    result['dt'] = datetime.strptime(news_time_str,'%Y年%m月%d日 %H:%M')#新闻时间，存储格式为元组
    result['source'] = soup.select('.date-source a')[0].text #新闻来源
    result['article'] = ' '.join([p.text.strip() for p in soup.select('.article p')[1:-1]])#文章正文内容，以空格作为每段的分割
    result['editor'] = soup.select('.article p')[-1].text.strip('责任编辑：').strip(' ')
    result['comments_number'] = getCommentsCount(newsurl) #还需要在调用这个函数前设置参数news_comments_url
    return result

#将抓取新闻内文整理成一个函数
##验证getNewsContend函数
#single_news_url = 'http://news.sina.com.cn/w/2018-07-09/doc-ihezpzwt6845530.shtml'
#news_comments_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gj&\
#newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&\
#h_size=3&thread=1' #把newsid部分用{}替换掉
#getNewsContend(single_news_url)
    

def getListLinks(page_news_url):
    '''获取一页新闻列表中每个新闻的连接'''
    news_link = []
    res = requests.get(url).text.lstrip('  newsloadercallback(').rstrip(');')
    js = json.loads(res)
    for new_link in js['result']['data']:
        news_link.append(new_link['url'])
    return news_link

##验证getListLinks函数
#url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gjxw&level==1||=2&\
#show_ext=1&show_all=1&show_num=22&tag=1&format=json&page=1&\
#callback=newsloadercallback&_=1531207624777'
#getListLinks(url)


#整合所有，抓取每一条国际新闻的所有内容
##1.产生每一条新闻的链接
url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gjxw&level==1||=2&\
show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}&\
callback=newsloadercallback&_=1531207624777'#这里用{}换page=1中的1

news_link_total = []
news_total = []
for i in range(1,6): #产生1-5页的所有新闻的链接
    fromat = url.format(i)
    news_link_total.extend(getListLinks(url.format(i))) #用extend方法而不是append方法
    
##2.使用for循环，获取每一条新闻链接里面的内容
for single_news_url in news_link_total:
    #news_comments_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gj&\
    #newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&page_size=3&t_size=3&\
    #h_size=3&thread=1' #把newsid部分用{}替换掉
    
    news_comments_url = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gj&\
newsid=comos-{}&group=undefined&compress=0&ie=utf-8&oe=utf-8&page=1&\
page_size=3&t_size=3&h_size=3&thread=1'
    news_total.append(getNewsContend(single_news_url))#每一个链接返回一个字典
    
##3.使用pandas整理数据
df = pd.DataFrame(news_total)
df.to_excel('sina_world_news.xlsx')

