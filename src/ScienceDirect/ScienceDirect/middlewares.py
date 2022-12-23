# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

# useful for handling different item types with a single interface
# from itemadapter import is_item, ItemAdapter


class SciencedirectSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SciencedirectDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2, 'permissions.default.stylesheet': 2}
        self.options.add_experimental_option("prefs", prefs)  # 禁止图片和css加载
        self.options.add_experimental_option("detach", True)
        # self.options.add_argument('--headless')  # 无界面运行
        self.options.add_argument('--disable-gpu')  # 禁止gpu加速
        self.options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        self.options.add_argument("no-sandbox")  # 取消沙盒模式
        # 禁用浏览器弹窗
        prefs = {
            'profile.default_content_setting_values': {
                'notifications': 2
            }
        }

        self.options.add_argument("--disable-javascript")  # 禁用JavaScript
        self.options.add_experimental_option('prefs', prefs)
        self.options.add_argument("disable-blink-features=AutomationControlled")  # 禁用启用Blink运行时的功能
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 开发者模式
        self.driver = webdriver.Chrome(options=self.options)
        # 如果IP被限制, 可以在此下载中间件添加代理
        self.IPPOOL = [
            {"ipaddr": "221.226.75.86:55443"},
            {"ipaddr": "112.250.107.37:53281"},
            {"ipaddr": "117.114.149.66:55443"},
            {"ipaddr": "120.24.76.81:8123"},
            {"ipaddr": "27.42.168.46:55481"},
            {"ipaddr": "112.14.47.6:52024"},
            {"ipaddr": "180.97.34.35:80"},
            {"ipaddr": "110.164.3.7:8888"},
            {"ipaddr": "106.14.255.124:80"},
            {"ipaddr": "118.31.2.38:8999"},
        ]
        # 代理头
        self.UA_LIST = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/55.0.2883.87 Safari/537.36',
                        'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)',
                        'Mozilla/5.0 (compatible; U; ABrowse 0.6;  Syllable) AppleWebKit/420+ (KHTML, like Gecko)',
                        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; '
                        '.NET CLR 3.5.30729)',
                        'Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Acoo Browser 1.98.744; '
                        '.NET CLR   3.5.30729)',
                        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0;   '
                        'Acoo Browser; GTB5; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1;   SV1) ; InfoPath.1; '
                        '.NET CLR 3.5.30729; .NET CLR 3.0.30618)',
                        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; Acoo Browser; '
                        '.NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; Avant Browser)',
                        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1;   '
                        '.NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)',
                        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; GTB5; '
                        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; '
                        'Maxthon; InfoPath.1; .NET CLR 3.5.30729; .NET CLR 3.0.30618)',
                        'Mozilla/4.0 (compatible; Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0;'
                        ' Trident/4.0; Acoo Browser 1.98.744; .NET CLR 3.5.30729); Windows NT 5.1; Trident/4.0)',
                        'Mozilla/4.0 (compatible; Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; '
                        'GTB6; Acoo Browser; .NET CLR 1.1.4322; .NET CLR 2.0.50727); Windows NT 5.1; '
                        'Trident/4.0; Maxthon; .NET CLR 2.0.50727; .NET CLR 1.1.4322; InfoPath.2)',
                        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; '
                        'Acoo Browser; GTB6; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; '
                        'InfoPath.1; .NET CLR 3.5.30729; .NET CLR 3.0.30618)']
        print("请在‘https://www.sciencedirect.com/science/article/abs/pii/S0140673621025022’点击蓝色按钮进行机构登陆")
        time.sleep(60)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called

        request.headers['User-Agent'] = random.choice(self.UA_LIST)  # UA
        ip = random.choice(self.IPPOOL)["ipaddr"]
        print("choosing ip:" + ip)
        request.meta["proxy"] = "http://" + ip  # IP池

        self.driver.get(request.url)
        # driver.implicitly_wait(10)
        # time.sleep(10)
        try:
            WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.XPATH, '//div[@class="Outline"]')))
            WebDriverWait(self.driver, 0.1).\
                until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="PreviewTableOfContents"]')))
        except Exception:
            pass
        finally:
            content = self.driver.page_source
            # self.driver.quit()
        return scrapy.http.HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
