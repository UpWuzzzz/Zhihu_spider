# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi


class ZhihuspiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用Twisted将Mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql,params = item.get_insert_sql()
        cursor.execute(insert_sql, params)
        # insert_sql = """
        #     insert into article(title, create_date, url, url_object_id, front_image_url,
        #     comment_nums, fav_nums, praise_nums, tags, content, front_image_path)
        #     VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        # """
        # cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'],
        #                                  item['front_image_url'], item['comment_nums'],
        #                                  item['fav_nums'], item['praise_nums'], item['tags'], item['content'], item['front_image_path']))

