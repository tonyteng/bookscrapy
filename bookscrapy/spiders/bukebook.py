# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.loader import ItemLoader
from tonyscrapy.items import BookItem
class BukebookSpider(scrapy.Spider):
    name = 'bukebook'
    allowed_domains = ['www.bukebook.cn']
    start_urls = ['https://www.bukebook.cn/category/%e7%bc%96%e7%a8%8b%e5%bc%80%e5%8f%91']
    custom_settings = {
        'ITEM_PIPELINES': {'tonyscrapy.pipelines.BookPipeLine': 300,},
        'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }    
    regexp=re.compile(r'.*?《(.*)》.*?((\w|\+)+)$')

    def parse(self, response):
        self.log('parse %s'%response.url)
        books=[
            scrapy.Request(response.urljoin(b),callback=self.parse_book) 
            for b in response.xpath('//div/h3/a/@href').getall()]
        next=response.xpath('//*[@id="greatwp-posts-wrapper"]//nav//div[@class="nav-previous"]/a/@href').get()
        if next:
            books.append(scrapy.Request(response.urljoin(next)))
        return books

    def parse_book(self, response):
        self.log('parse_book %s'%response.url)
        url=response.xpath('//div[@class="ordown"]/a/@href').get()
        yield scrapy.Request(response.urljoin(url),callback=self.parse_download)

    def parse_download(self, response):
        self.log('parse_download %s'%response.url)
        loader=ItemLoader(BookItem(),response)
        loader.add_value('src',response.url)
        loader.add_xpath('url','//*[@id="focus"]//div/a[1]/@href')
        loader.add_xpath('pwd','//*[@id="focus"]/div/div[@class="ordown-header"]/div/p[@class="ordown-alert"]/strong[1]/text()')
        name=response.xpath('//*[@id="focus"]//div/h2/a/text()').get()
        g=BukebookSpider.regexp.match(name)
        loader.add_value('name',g[1].strip())
        loader.add_value('ext',g[2].strip())
        return loader.load_item()