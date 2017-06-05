# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb as mdb
import json
from spider_toutiao_article.items import LSpiderArticleInfo

class SpiderToutiaoArticlePipeline(object):
    """数据爬取完成之后对数据进行处理
    meijutt站点数据爬取之后存储mysql数据库

    Attributes:
        client (:obj): 数据库操作游标
    """

    client = None

    def get_config(self):
        file_reader = open("config.json", "r")
        config_info = file_reader.read()
        config = json.loads(config_info)
        file_reader.close()
        return config

    def open_spider(self, spider):
        """爬虫开启之后的回调
        爬虫开启之后，连接上数据库

        Args:
            spider (scrapy.Spider) 爬虫对象
        """
        config = self.get_config()
        self.client = mdb.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            passwd=config["passwd"],
            db='spider_rough_base',
            charset=config["charset"]
        )
        self.client.autocommit(True)

    def process_article(self, item, cursor):
        article_info = [
            item.get('abstract'),
            item.get('go_detail_count'),
            item.get('article_type'),
            item.get('comments_count'),
            item.get('channel'),
            item.get('cover_image_url'),
            item.get('title'),
            item.get('source'),
            item.get('detail_url'),
            item.get('created_time'),
            item.get('update_time'),
            item.get('published_time'),
            item.get('custom_item_id'),
            item.get('context')
        ]

        article_insert_sql = 'INSERT IGNORE INTO rough_article_info (abstract, go_detail_count, article_type, comments_count, channel, cover_image_url, title, source, detail_url, created_time, update_time, published_time, custom_item_id, context) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(article_insert_sql, article_info)

    def process_item(self, item, spider):
        """处理item数据

        Args:
            item (scrapy.Item): scrapy.Item数据对象
            spider (scrapy.Spider): scrapy.Spider爬虫对象

        Returns:
            item (scrapy.Item): scrapy.Item数据对象
        """

        cursor = self.client.cursor()

        if type(item) is LSpiderArticleInfo:
            self.process_article(item, cursor)

        # 每次完成之后都需要关闭游标
        cursor.close()
        return item

    def close_spider(self, spider):
        """关闭spider
        每次关闭spider时候关闭数据库连接
        """

        if self.client is not None:
            self.client.close()
