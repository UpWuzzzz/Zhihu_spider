#### 知乎爬虫
模拟登陆知乎爬取问题和回答并入库。

##### 爬取与入库流程
![Scrapy框架结构](https://images2015.cnblogs.com/blog/931154/201703/931154-20170314141524729-978666187.png)

##### 该项目用到的库
+scrapy
+requests
+PIL(识别点击图片验证码时候要用)

# Zhihu_spider
模拟登陆知乎爬取问题和回答。

# 采用的是scrapy爬虫框架进行数据爬取。调用的第三方库有：requests，json，PIL,scrapy，

在模拟登陆知乎时，有头部的X-Xsrftoken和authorization需要加入头部信息，

表单信息很好查找，signature是一个hash加密，可以在js中找到，还有一个是时间戳去除小数点后的数字。

在访问验证码时候，有两种一种是常见的字符验证码，一种是点击图片验证码。一般采用字符验证码进行登陆。验证码输入后需要提交到访问网站，再加入表单发送。

登陆后会根据热门推荐进行爬取，没有采用深度爬取，暂时爬取数量较少，回答会根据回答数量进行爬取。

欢迎大家来补充代码信息，使其更加完善。
