# -*- coding: utf-8 -*-
import urllib
import json
import time
import MySQLdb as mdb
import scrapy
from ..items import LSpiderArticleInfo


class ToutiaoSpider(scrapy.Spider):
    name = u"toutiao"
    allowed_domains = [u"www.toutiao.com"]
    start_urls = [u'http://www.toutiao.com/']

    domain = u"http://www.toutiao.com"

    # 头条号用户id列表
    user_id_list = [
        60194326279,  # 三水爱推文
        52250643875,  # 优读书馆
        5837040655,  # 读什么
        6636746831,  # 豆瓣阅读
        4129746201,  # 新京报书评周刊
        6056678147,  # 多看阅读
        5969449783,  # 书单迷
        5227932186,  # 青阅读
        5763745249,  # 喜文乐荐
        5232017767,  # 商务印书馆
        5955144630,  # 三联书店三联书情
        50877676495,  # 知书
        6885606472,  # 读思之所
    ]

    article_list_path = u"/c/user/article/"

    queries = {
        "page_type": 1,
        "user_id": 0,
        "max_behot_time": 0,
        "count": 20
    }

    client = None

    def get_config(self):
        file_reader = open("config.json", "r")
        config_info = file_reader.read()
        config = json.loads(config_info)
        file_reader.close()
        return config
    
    def check_not_exist(self, custom_item_id):
        # 查看数据库中是否已经存在爬取数据
        cursor = self.client.cursor()
        query_count_sql = 'SELECT COUNT(*) FROM rough_article_info WHERE custom_item_id=%s'
        cursor.execute(query_count_sql, [
            custom_item_id
        ])
        count = cursor.fetchone()
        cursor.close()

        if count[0] == 0:
            return True
        else:
            return False

    def start_requests(self):
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

        for user_id in self.user_id_list:
            url = self.create_request_url(user_id, 0)
            yield scrapy.Request(url, callback=self.parse, meta={'user_id': user_id})

    def create_request_url(self, user_id, max_behot_time):
        queries = self.queries

        queries["user_id"] = user_id
        queries["max_behot_time"] = max_behot_time

        url = self.domain + self.article_list_path + "?" + urllib.urlencode(queries)
        return url

    def parse(self, response):
        content = json.loads(response.body_as_unicode())

        scrapy_count = 0
        now = int(time.time())
        for item in content['data']:

            cover_image_url = None
            if item.has_key('image_url'):
                cover_image_url = item['image_url']

            article_info = LSpiderArticleInfo(
                abstract=item['abstract'],
                go_detail_count=item['go_detail_count'],
                article_type=item['article_genre'],
                comments_count=item['comments_count'],
                channel=self.name,
                cover_image_url=cover_image_url,
                title=item['title'],
                source=item['source'],
                detail_url=self.domain + item['source_url'],
                created_time=now,
                update_time=now,
                published_time=item['behot_time'],
                custom_item_id='toutiao_' + item['item_id'],
            )

            # 查看数据库中是否已经存在爬取数据
            if self.check_not_exist(article_info.get('custom_item_id')):
                scrapy_count = scrapy_count + 1
                print article_info['detail_url']
                yield scrapy.Request(url=article_info['detail_url'],
                                     callback=self.parse_content,
                                     meta={'article_info': article_info})

        if content['has_more'] and scrapy_count == len(content['data']):
            next_page = self.create_request_url(
                response.meta['user_id'],
                content['next']['max_behot_time']
            )
            yield scrapy.Request(url=next_page,
                                 callback=self.parse,
                                 meta={'user_id': response.meta['user_id']})

    def parse_content(self, response):
        article_info = response.meta['article_info']

        context = response.css('div.article-content').extract_first()
        article_info['context'] = context

        return article_info
