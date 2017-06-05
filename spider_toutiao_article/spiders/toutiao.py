# -*- coding: utf-8 -*-
import scrapy


class ToutiaoSpider(scrapy.Spider):
    name = "toutiao"
    allowed_domains = ["www.toutiao.com"]
    start_urls = ['http://www.toutiao.com/']

    def parse(self, response):
        pass
