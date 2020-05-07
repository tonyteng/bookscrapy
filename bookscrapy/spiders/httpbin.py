# -*- coding: utf-8 -*-
import scrapy
import json

class HttpbinSpider(scrapy.Spider):
    name = 'httpbin'
    allowed_domains = ['httpbin.org']
    agent_url='http://www.httpbin.org/user-agent'
    ip_url='http://www.httpbin.org/ip'

    def parse_agent(self, response):
        self.log('status:%s,%s,user-agent:%s'%(response.status,json.loads(response.text)['user-agent']))
        yield scrapy.Request(response.urljoin(self.agent_url),dont_filter=True,callback=self.parse_agent)

    def parse_ip(self, response):
        self.log('status:%s,ip:%s'%(response.status,json.loads(response.text)['origin']))
        yield scrapy.Request(response.urljoin(self.ip_url),dont_filter=True,callback=self.parse_ip)

    def start_requests(self):
        yield scrapy.Request(self.agent_url,dont_filter=True,callback=self.parse_agent)
        yield scrapy.Request(self.ip_url,dont_filter=True,callback=self.parse_ip)