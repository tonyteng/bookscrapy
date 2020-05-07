# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from tonyscrapy.items import BookItem
import re
re_url=re.compile(r'.*?url=(.*)')
re_pwd=re.compile(r'.*(\w{4})')
re_title=re.compile(r'《(.*)》.*?\+?([a-zA-Z0-9+]*)$')

class KindleerSpider(scrapy.Spider):
    name = 'kindleer'
    allowed_domains = ['kindleer.com']
    start_urls = ['https://kindleer.com/tag/kaifa/page/1/']
    custom_settings = {
        'ITEM_PIPELINES': {'tonyscrapy.pipelines.BookPipeLine': 300},
        'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }

    def parse(self, response):
        self.logger.debug('parse %s'%response.url)
        urls=[scrapy.Request(u,callback=self.parse_book)  for u in response.xpath('//article/span[@class="entry-more"]/a/@href').getall()]
        next=response.xpath('//nav/div/a[contains(@class,"next")]/@href').get()
        if next:
            urls.append(scrapy.Request(next))
        return urls

    def parse_book(self,response):
        loader=ItemLoader(BookItem(),response)
        self.logger.debug('parse_book %s'%response.url)
        url=response.xpath('//div/div/p/a[text()="百度网盘"]/@href').get()
        if url:
            self.log('regexp_book_url:%s'%url)
            url=re_url.match(url)[1]
        else:
            url=''
            
        #pwd=response.xpath('//div[@class="single-content"]/p/text()').getall()
        pwd=response.xpath('//div[@id="content"]/p/text()').getall()
        if not pwd:
            pwd=response.xpath('//div[@class="single-content"]/p/text()').getall()
        if pwd:
            pwd='|'.join(pwd)
            self.log('regexp_book_pwd:%s'%pwd)
            pwd=re_pwd.match(pwd)[1]
        else:
            pwd=''
        title=response.xpath('//header/h1/text()').get()
        self.log('regexp_book_title:%s'%title)
        title=re_title.match(title)
        name=title[1]
        ext=title[2]
        loader.add_value('name',[name])
        loader.add_value('ext',[ext])
        loader.add_value('pwd',[pwd])
        loader.add_value('url',[url])
        loader.add_value('src',[response.url])
        return loader.load_item()


        
