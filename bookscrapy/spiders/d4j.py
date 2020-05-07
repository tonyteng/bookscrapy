# -*- coding: utf-8 -*-
import scrapy
from tonyscrapy.items import BookItem
from scrapy.loader import ItemLoader


class D4jSpider(scrapy.Spider):
    name = "d4j"
    allowed_domains = ["d4j.cn"]
    custom_settings = {
        "ITEM_PIPELINES": {"tonyscrapy.pipelines.BookPipeLine": 300},
        #'DOWNLOADER_MIDDLEWARES':{'tonyscrapy.middlewares.UserAgengtMiddleware': 543,}
    }
    # start_urls = ['https://www.d4j.cn/wp-login.php']
    links = [
        #"https://www.d4j.cn/xuexi-ganhuo/biancheng-kaifa",  # 编程开发 6页
        #'https://www.d4j.cn/hejitaozhuang/qita-heji', #中亚合集 85页
        #'https://www.d4j.cn/hejitaozhuang/lixiangguo-yicong',#理想国译丛 3
        #'https://www.d4j.cn/hejitaozhuang/hanqingtang-congshu',#汗青堂丛书 2
        #'https://www.d4j.cn/hejitaozhuang/jiaguwen-congshu',#甲骨文丛书 6
        'https://www.d4j.cn/changxiao-tushu/manhua-ziyuan',#漫画
    ]

    def start_requests(self):
        url = "https://www.d4j.cn/wp-login.php"
        data = {
            "log": "tonyteng",
            "pwd": "internet",
            "testcookie": "1",
            "wp-submit": "登录",
        }
        yield scrapy.FormRequest(url, formdata=data)

    def parse(self, response):
        status = response.status
        self.log("login status:%d" % status)
        if status != 200:
            self.log(response.text)
            return None
        self.log("login success,begin scraw...")
        return [
            scrapy.Request(link, callback=self.parsebook) for link in D4jSpider.links
        ]

    def parsebook(self, response):
        self.log("passbook %s" % response.url)
        books = [
            scrapy.Request(response.urljoin(u), callback=self.parsedownload)
            for u in response.xpath("//article//h2/a/@href").getall()
        ]
        next = response.xpath('//a[@class="next"]/@href').get()
        if next:
            books += [scrapy.Request(next, callback=self.parsebook)]
        return books

    def parsedownload(self, response):
        self.log("get status:%d" % response.status)
        self.log("parse download url:%s" % response.url)
        url = response.xpath("//div/p/strong/a/@href").get()
        yield scrapy.Request(response.urljoin(url), callback=self.parsebaidupan)

    def parsebaidupan(self, response):
        self.log("get status:%d" % response.status)
        self.log("parse baidupan url:%s" % response.url)
        l = ItemLoader(item=BookItem(), response=response)
        l.add_xpath("name", "//div/h2/text()")
        l.add_xpath("pwd", "//ul/li/font/text()")
        l.add_xpath("url", "//div/span/a/@href")
        l.add_value("ext", "book")
        l.add_value("src", response.url)
        yield l.load_item()
