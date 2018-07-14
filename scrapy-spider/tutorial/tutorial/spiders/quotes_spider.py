import scrapy
import json

class QuotesSpider(scrapy.Spider):
    #爬虫名字，必须唯一
    name = "quotes"

    start_urls = [
        'http://quotes.toscrape.com/page/1/',
    ]

    def parse(self, response):
        '''
        Desc:
            解析并处理响应
        param:
            response -- 响应返回的内容 ，相当于response = requests.get(url)
        '''
        for quote in response.css('div.quote'):
            #yield课以简单的理解为return,只不过在下一次迭代时，追加在上一次迭代后的位置继续迭代
            #这里返回一个字典
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
        #读取下一页中的内容
        next_page =  response.css('li.next a::attr(href)').extract_first() # 结果为'/page/2/'
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse) #继续调用parse函数

