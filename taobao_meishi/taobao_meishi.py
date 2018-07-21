# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 20:13:36 2018

@author: Xavier
"""
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from configure import *
import  pymongo

client = pymongo.MongoClient(MONGO_URL) #创建一个MONGO客户端
db = client[MONGO_DB] #指定一个数据库

#不过，截止目前2018.07.21，selenium已经不在只是PhantomJS了，我们还是乖乖使用Chrome吧
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
# browser.set_window_size(1400,900)#设置窗口大小
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10) #等待
keyword = '美食'

def search(keyword):
    '''
    Desc:
        模拟搜索关键字keyword，并点击搜索按钮，进行跳转
    param:
        keyword -- 搜索用的关键词
    return:
        total.text -- 当前关键字下的总页数
    '''
    try:
        print('正在搜索')
        browser.get('https://www.taobao.com/') #模拟浏览器进入淘宝网
        #等待直到局部元素显示出来,这里的局部元素为淘宝网页搜索框部分
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
        )
        #等待直到元素可被点击,这里的元素为搜索按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys(keyword) #在输入框调用send_keys方法模拟输入关键字
        submit.click() #模拟点击搜索按钮操作
        #点击之后，等待页面刷新，这里的条件为直到局部元素显示出来,这里的局部元素为下一页的总页数部分
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        return total.text
    #发生延时异常时，重新调用search()方法
    except TimeoutException:
        search(keyword)


def next_page(page_number):
    '''
    Desc:
        输入下一页页码，并点击确定，进行跳转
    param:
        page_number -- 搜索下一页的页码
    '''
    try:
        print('正在翻页', page_number)
         #等待直到局部元素显示出来,这里的局部元素为到第[2]页中的[..]
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input"))
        )
        #等待直到元素可被点击,这里的元素为输入页码后的的确定按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear() #清除当前输入框中的内容
        input.send_keys(page_number) #把下一页的页码传入输入框中
        submit.click() #模拟点击确定按钮，跳转到下一页的操作
        #点击之后，等待页面刷新，这里的条件为直到局部元素显示出来,这里的局部元素为数字页码在填充方框这个元素中
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, \
                                              '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_number))
                  )
        get_products() #解析每一页产品的信息
    #发生延时异常时，重新调用next_page(page_number)方法
    except TimeoutException:
        next_page(page_number)


def get_products():
    '''
    Desc:
        使用BeautifulSoup解析每一个产品的信息（图片、价格、付款人数、标题、店铺名、店铺地点）
    '''
    #等待每一个图片元素加载出来
    print('获取产品信息')
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-itemlist .items .item")))
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('#mainsrp-itemlist .items .item')
    for item in items:
        product = {
            'image': item.select('.pic img')[0]['src'],
            'price': item.select('.price')[0].text.strip(),
            'deal_number': item.select('.deal-cnt')[0].text[:-3],
            'title': item.select('.title')[0].text.strip(),
            'shop': item.select('.shop')[0].text.strip(),
            'location': item.select('.location')[0].text.strip()
        }
        print(product)
        save_to_mongo(product) #保存到Mongo数据库中

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到Mongo数据库成功', result)
    except Exception:
        print('存储到Mongo数据库失败', result)


def main():
    total = search(keyword)
    #使用strip方法去除字符串中的不需要的内容，取出其中的数字
    #也可以使用正则表达式, \d表示匹配任意的一个10进制数，+表示匹配前边的原子1次或多次
    #total = int(re.compile('(\d+)').search(total).group(1))
    total = int(total.lstrip('共 ').rstrip(' 页，'))
    #这里只模拟前两页页
    for i in range(1,3):
        next_page(i)


if __name__ == '__main__':
    main()
