# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from tonyscrapy.items import BookItem
regexp=re.compile(r'.*《(.*)》')
class Fast8Spider(scrapy.Spider):
    name = "fast8"
    allowed_domains = ["fast8.com"]
    custom_settings = {
        'ITEM_PIPELINES': {'tonyscrapy.pipelines.BookPipeLine': 300},
        #'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }
    def start_requests(self):
        url='http://fast8.com/phome/index.php'
        formdata={
            'phome': 'login',
            'ecmsfrom': '9',
            'username': 'tonyteng',
            'password': 'internet'}
        yield scrapy.FormRequest(url,formdata=formdata)

    def parse(self, response):
        if response.status!=200:
            self.log('Login failure ,quit ....')
            return None
        self.log("login success,begin scraw...")
        return scrapy.Request('http://www.fast8.com/list/8_1.html',callback=self.parse_page)

    def parse_page(self, response):
        self.log('parse_page %s'%response.url)
        books=[
            scrapy.Request(response.urljoin(book),callback=self.parse_download) 
            for book in response.xpath('//div[@align="center"]/a[@target="_blank"]/@href').getall()]
        next=response.xpath('//div/a[text()="下一页"]/@href').get()
        if next:
            books+=[scrapy.Request(response.urljoin(next),callback=self.parse_page)]
        return books

    def parse_download(self, response):
        self.log('parse_download %s'%response.url)
        #return [scrapy.Request(response.urljoin(x),callback=self.parse_pan) 
        books=[]
        for a in response.xpath('//a[@class="button"]'):
            item=BookItem()
            name=a.xpath("./font/text()").get().split('/')
            item['url']=[response.urljoin(a.xpath("./@href").get())]
            item['src']=[response.url]
            title=name[0].strip()
            g=regexp.match(title)
            if g:
                title=g[1].replace('《','').replace('》','')
            item['name']=[title]
            item['ext']=[name[-1]]
            item['pwd']=['']
            books.append(item)
        return books
