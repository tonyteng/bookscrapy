# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from tonyscrapy.items import BookItem
from scrapy.loader import ItemLoader

class ItpandaSpider(CrawlSpider):
    name = "itpanda"
    allowed_domains = ["itpanda.net"]
    start_urls = ["https://itpanda.net/"]
    __exts = {}
    rules = (
        Rule(LinkExtractor(allow=r"book\/category"), follow=True),
        Rule(LinkExtractor(allow=r"book\/\d+$"), callback="parse_info", follow=True),
        Rule(LinkExtractor(allow=r"download\/"), callback="parse_book", follow=False),
        Rule(LinkExtractor(allow=r"baidu"),  follow=False),

    )
    custom_settings = {
        'ITEM_PIPELINES': {'tonyscrapy.pipelines.BookPipeLine': 300},
        'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }

    def parse_book(self, response):
        self.log("Parse book url:%s"%response.url)
        name = response.xpath('//div[contains(@class,"alert-success")]/h5/text()').get()
        name = name.replace(" 的下载地址", "")
        pwd = response.xpath("//p/text()[3]").get()
        pwd = pwd.replace(", 提取码:", "")
        loader=ItemLoader(BookItem(),response)
        loader.add_value('pwd',pwd)
        loader.add_value('src',response.url)
        loader.add_xpath('url','//p/a[contains(@class,"text-danger") and contains(@href,"baidu")]/@href')
        loader.add_value('ext',self.__exts[hash(name)])
        loader.add_value('name',name)
        yield loader.load_item()

    def parse_info(self, response):
        self.log('Parse info url:%s'%response.url)
        title = response.xpath('//div[contains(@class,"container")]//h4/text()').get().strip()
        ext = response.xpath('//p[@class="text-dark"]/text()').get().strip()
        url=response.xpath('//p/a[contains(text(),"百度网盘")]/@href').get().strip()
        self.log('Bookinfo:%s.%s:%s'%(title,ext,url))
        if "mobi" in ext:
            ext = "mobi"
        else:
            ext = "pdf"
        self.__exts[hash(title)] = ext
        self.log("Get a info %s:%s" % (ext, title))
        yield scrapy.Request(response.urljoin(url),callback=self.parse_book)