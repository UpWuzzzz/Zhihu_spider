# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ZhihuQuestionItem(scrapy.Item):
    """
        知乎问题的Item设计
    """
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 具体item的insert语句
        insert_sql = """
                    insert into zhihu_question(zhihu_id, topics, url, title, content,
                    answer_num, comments_num, watch_user_num, click_num, crawl_time)
                    VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        params =(self['zhihu_id'], self['topics'], self['url'], self['title'],
                 self['content'], self['answer_num'],self['comments_num'],
                 self['watch_user_num'], self['click'],self['crawl_time'])

        return insert_sql, params


class ZhihuAnswerItem(scrapy.Item):
    """
        知乎回答的Item设计
    """
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()

    def get_insert_sql(self):
        # 具体item的insert语句
        insert_sql = """
                    insert into zhihu_answer(zhihu_id, url, question_id, author_id, content,
                    praise_num, comments_num, create_time, update_time, crawl_time)
                    VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        params =(self['zhihu_id'], self['url'], self['question_id'], self['author_id'],
                 self['content'], self['praise_num'], self['comments_num'],
                 self['create_time'], self['update_time'], self['crawl_time'])

        return insert_sql, params