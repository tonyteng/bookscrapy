# -*- coding: utf-8 -*-
import scrapy
import re
from tonyscrapy.items import BookItem
from scrapy.loader import ItemLoader

class SalttigerSpider(scrapy.Spider):
    name = "salttiger"
    allowed_domains = ["saletiger.com"]
    start_urls = ["https://salttiger.com/archives/"]
    custom_settings = {
        'ITEM_PIPELINES': {'tonyscrapy.pipelines.BookPipeLine': 300},
        'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }
    def parse(self, response):
        return [
            scrapy.Request(
                response.urljoin(url), callback=self.parsebook, dont_filter=True
            )
            for url in response.xpath('//ul[@class="car-list"]//a/@href').getall()
        ]

    def parsebook(self, response):
        self.log("Parse book url:%s"%response.url)
        #item=BookItem()
        urls=[]
        exts=set()
        # item['url']={
        #     u.xpath('./text()').get():u.xpath('./@href').get() 
        #     for u in response.xpath('//div[@class="entry-content"]/p//a') 
        #     if u!=None
        # }

        for u in response.xpath('//div[@class="entry-content"]/p//a') :
            key=u.xpath('./text()').get()
            if 'PDF' in key:
                exts.add('PDF')
            if 'MOBI' in key:
                exts.add('MOBI')
            if 'EPUB' in key:
                exts.add('EPUB')
            if 'AZW' in key:
                exts.add('AZW')
            href=u.xpath('./@href').get()
            pwd=''
            if 'pan.baidu' in href:
                pwd=u.xpath('../text()[last()]').get()
                if pwd:
                    g=re.match(r'提取码.*?(\w+)$',pwd.strip())
                    if g:
                        pwd=g[1]
                        href+=':'+pwd
            urls.append('%s:%s'%(key,href))
        loader=ItemLoader(BookItem(),response)
        loader.add_xpath('name','//header/h1/text()')
        loader.add_value('url',';'.join(urls)+';')#结尾增加;方便正则
        loader.add_value('ext','|'.join(exts))
        loader.add_value('src',response.url)
        loader.add_value('pwd','')
        yield loader.load_item()

