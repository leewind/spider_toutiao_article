# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class LSpiderArticleInfo(scrapy.Item):
    abstract = scrapy.Field()
    go_detail_count = scrapy.Field()
    article_type = scrapy.Field()
    comments_count = scrapy.Field()
    channel = scrapy.Field()
    cover_image_url = scrapy.Field()
    title = scrapy.Field()
    source = scrapy.Field()
    detail_url = scrapy.Field()
    created_time = scrapy.Field()
    update_time = scrapy.Field()
    published_time = scrapy.Field()
    custom_item_id = scrapy.Field()
    context = scrapy.Field()
