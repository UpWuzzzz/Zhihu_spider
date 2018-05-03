# -*- coding: utf-8 -*-
"""
    模拟登陆知乎网站并抓取数据
    有验证码识别的功能
    破解hash加密
"""

import scrapy, re, base64, json, os, time, hmac, datetime
from hashlib import sha1
from PIL import Image
import matplotlib.pyplot as plt
from ZhihuSpider.items import ZhihuAnswerItem, ZhihuQuestionItem

# 头部信息
HEADERS = {
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }
# 表单数据
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    # 改为'cn'是倒立汉字验证码
    'lang': 'en',
    'ref_source': 'homepage'
}
# 固定值
authorization = 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20'
# 知乎首页
INDEX_URL = "https://www.zhihu.com/"
# 知乎登陆网址
LOGIN_URL = 'https://www.zhihu.com/signup'
# 知乎登陆发送表单网址
LOGIN_API = 'https://www.zhihu.com/api/v3/oauth/sign_in'
# 通过这个API的get方法查询用户信息。
USER_API = 'https://www.zhihu.com/api/v4/me?include=following_question_count'
# 更新获取页面推荐信息
ACTION_API = 'https://www.zhihu.com/api/v3/feed/topstory?action_feed=True&limit=7&' \
             'session_token=11b5dbb352002e7418c0a968be86f27e&action=down&after_id=13&' \
             'desktop=true'
# 获取首要回答信息
FRIST_ANSWERS_API = 'https://www.zhihu.com/api/v4/questions/{0}/answers?include=' \
                   'data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2' \
                   'Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason' \
                   '%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment' \
                   '%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2' \
                   'Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2' \
                   'Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2' \
                   'Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B%2A%5D.mark_infos' \
                   '%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%3F%28' \
                   'type%3Dbest_answerer%29%5D.topics&limit=5&offset=0&sort_by=default'
# 相关问题
UNION_PROBLEM_API = 'https://www.zhihu.com/api/v4/questions/275339383/similar-questions'
# 点击倒立字符验证码
CAPTCHA_API_cn = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
# 常见字符型验证码
CAPTCHA_API_en = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'


class ZhihuSpiderSpider(scrapy.Spider):
    name = 'Zhihu_Spider'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/']
    headers = HEADERS.copy()
    post_data = FORM_DATA.copy()
    timestamp = str(int(time.time() * 1000))

    def parse(self, response):
        """
            提取出html页面的所有url 并跟踪这些url进一步爬取。
        """
        question_urls = re.findall(r'<div class="ContentItem AnswerItem".*?itemProp="url" content="(.*?)".*?>',
                                  response.text)
        for url in question_urls:
            question_id = re.findall('.*zhihu.com/question/(\d+)', url)
            yield scrapy.Request(url=url, meta={'question_id':question_id}, headers=self.headers,
                                 callback=self.parse_question)
        # 继续访问其他热门推荐
        pass

    def parse_question(self, response):
        """
            处理question页面从中提取出question具体的item
        """
        item_loader = ZhihuQuestionItem()

        response_content = response.text

        question_content = re.findall('<div class="QuestionHeader-topics">.*?</h4>', response.text)[0]
        question_id = response.meta.get('question_id')[0]

        topics = re.findall('<div class="Tag QuestionTopic">.*?aria-owns="null-content">(.*?)</div>', question_content)
        topics = ','.join(topics)
        url = response.url
        title = re.findall('<h1 class="QuestionHeader-title">(.*?)</h1>', question_content)[0]
        content = re.findall('<span class="RichText" itemProp="text">(.*?)</span>', question_content)
        content = str(content[0]) if len(content) > 0 else ' '
        answer_num = re.findall('<h4 class="List-headerText">.*?(\d+).*?</h4>', question_content)
        answer_num = int(answer_num[0]) if len(answer_num) >0 else 0
        comments_num = re.findall('</span>(\d+) 条评论</button>', question_content)
        comments_num = int(comments_num[0]) if len(comments_num) > 0 else 0
        watch_user_num = re.findall('关注者.*?title="(\d+)">', question_content)
        watch_user_num = int(watch_user_num[0]) if len(watch_user_num) >0 else 0
        click = re.findall('被浏览.*?title="(\d+)">', question_content)
        click = int(click[0]) if len(click) > 0 else 0

        item_loader['zhihu_id'] = int(question_id)
        item_loader['topics'] = topics
        item_loader['url'] = url
        item_loader['title'] = title
        item_loader['content'] = content
        item_loader['answer_num'] = answer_num
        item_loader['comments_num'] = comments_num
        item_loader['watch_user_num'] = watch_user_num
        item_loader['click'] = click
        item_loader['zhihu_id'] = question_id
        item_loader['crawl_time'] = datetime.datetime.now() #.strftime('%Y-%m-%d %H:%M:%S')

        yield scrapy.Request(url=FRIST_ANSWERS_API.format(question_id), meta={'question_id':question_id},
                             headers=self.headers, callback=self.parse_answer)

        yield item_loader

    def parse_answer(self, response):
        """
            处理用户回答的消息。并提取出具体的item。
        """
        ans_json = json.loads(response.text)
        question_id = response.meta.get('question_id')[0]
        is_end = ans_json['paging']['is_end']
        next_url = ans_json['paging']['next']
        totals = ans_json['paging']['totals']

        for answer in ans_json['data']:
            item_loader = ZhihuAnswerItem()

            item_loader['zhihu_id'] = answer['id']
            item_loader['url'] = answer['url']
            item_loader['question_id'] = question_id
            item_loader['author_id'] = answer['author']['id'] if 'id' in answer['author'] else None
            item_loader['content'] = answer['content']
            item_loader['praise_num'] = answer['voteup_count']
            item_loader['comments_num'] = answer['comment_count']
            item_loader['create_time'] =  datetime.date.fromtimestamp(answer['created_time']).\
                strftime("%Y-%m-%d") if 'created_time' in answer else ''
            item_loader['update_time'] = datetime.date.fromtimestamp(answer['updated_time']).\
                strftime("%Y-%m-%d") if 'updated_time' in answer else ''
            item_loader['crawl_time'] = datetime.datetime.now()

            yield item_loader

        if not is_end:
            yield scrapy.Request(url=next_url, meta={'question_id':question_id},
                                 headers=self.headers, callback=self.parse_answer)


    def start_requests(self):
        """
            重构Spider入口方法，查找xsrf值。
        """
        yield scrapy.Request(url=INDEX_URL, headers=self.headers, callback=self._get_Xsrftoken)


    def _get_Xsrftoken(self, response):
        """
        通过respnose返回的头部获取xsrf值，正则匹配更改访问headers
        然后去确认是否需要验证码识别。
        """
        Xsrftoken = re.findall('_xsrf=(.*?);', response.headers.getlist('Set-Cookie')[0].decode('utf-8'))
        self.headers.update({
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': Xsrftoken[0]
        })

        # 确定要访问验证码的格式，并访问网址确认
        lang = self.headers.get('lang', 'en')
        if lang == 'cn':
            url = CAPTCHA_API_cn
        else:
            url = CAPTCHA_API_en
        yield scrapy.Request(url=url, headers=self.headers, callback=self._get_captcha)

    def _get_captcha(self, response):
        """
            如果要验证码再次访问网址获取图片的base64值，
            不需要的话，更新表单数据，直接登陆
        """
        show_captcha = re.search(r'true', response.text)
        if show_captcha:
            yield scrapy.Request(
                url=response.url,
                headers=self.headers,
                callback=self._input_captcha,
                method='PUT'
            )
        else:
            self.post_data.update({
                'input_text': ''
            })
            yield scrapy.Request(url=LOGIN_URL, headers=self.headers, callback=self.login)

    def _input_captcha(self, response):
        """
            将验证码下载到本地，用默认图片查看器查看，
            并输入验证码信息，更新表单数据，将输入验证码
            发送到验证码网址（知乎专属），再进行登陆。
        """
        # 图片为base64加密，用64解密加载到本地。
        captcha = response.body
        img_base64 = base64.b64decode(json.loads(captcha)['img_base64'])

        spiders_path = os.path.dirname(__file__)
        with open(spiders_path+'/captcha.jpg', 'wb') as f:
            f.write(img_base64)
        # 先用im打开图片，防止图片还没有写完全就被os读取。
        img = Image.open(spiders_path+'/captcha.jpg')
        if 'lang=cn' in response.url:
            # 这段代码是网上找的，获取图片点击位置并返回数据信息。
            plt.imshow(img)
            print('点击所有倒立的汉字，按回车提交')
            points = plt.ginput(7)
            capt = json.dumps({'img_size': [200, 44],
                               'input_points': [[i[0] / 2, i[1] / 2] for i in points]})
        else:
            os.startfile(spiders_path+'/captcha.jpg')
            capt = input('请输入图片里的验证码：')
        # 这里必须先把参数 POST 验证码接口
        self.post_data.update({
            'input_text':capt,
        })
        capt_data={'input_text': capt}
        yield scrapy.FormRequest(
            url=response.url,
            formdata=capt_data,
            headers=self.headers,
            callback=self.login
        )

    def login(self, response):
        """
            发送表单数据登陆。
        """
        url = LOGIN_API
        user = input('请输入用户账号：\n>')
        passwd = input('请输入用户密码：\n>')
        self.post_data.update({
            'username': user,
            'password': passwd,
        })

        # 这里表单数据需要时间戳和哈希加密算法得到的值。
        self.post_data.update({
            'timestamp': self.timestamp,
            'signature': self._get_signature()
        })
        yield scrapy.FormRequest(
            url=url,
            formdata=self.post_data,
            headers=self.headers,
            callback=self._check_login
        )

    def _get_signature(self):
        """
            通过 Hmac 算法计算返回签名
            实际是几个固定字符串加时间戳
            timestamp: 时间戳
        """
        hm1 = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)
        hm1.update(self.post_data['grant_type'].encode('utf8'))
        hm1.update(self.post_data['client_id'].encode('utf8'))
        hm1.update(self.post_data['source'].encode('utf8'))
        hm1.update(self.timestamp.encode('utf8'))
        return hm1.hexdigest()

    def _check_login(self, response):
        """
            检查登录状态，访问知乎首页，
        """
        yield scrapy.Request(url=LOGIN_URL, dont_filter=True, headers=self.headers)