import random
import re
import scrapy
from ..items import SemanticItem
import requests
from lxml import etree
import numpy as np
class TxsrSpider(scrapy.Spider):
    name = 'txsr'
    allowed_domains = ['semanticscholar.org']
    start_urls = ['https://www.semanticscholar.org/paper/Ionic-interactions-in-biological-and-physical-a-Eisenberg/ecfef9c5676d16271690552323e29899de70d2a6']
    headers = {"User-agent": "Mozilla/5.0 (Windows; U; Windows NT 6.1) AppleWebKit/531.27.5 (KHTML, like Gecko) Version/5.1 Safari/531.27.5",
           "Accept": "text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",'Connection': 'close'}

    offset = 0
    handle_httpstatus_list = [404,400]
    url_list=[]
    def parse(self, response):

        if len(self.url_list)<10:
            for a in range(1, 11):
                url = "https://www.semanticscholar.org/paper/Energy-and-Policy-Considerations-for-Deep-Learning-Strubell-Ganesh/d6a083dad7114f3a39adc65c09bfbb6cf3fee9ea?sort=relevance&page={}".format(a)
                headers = {
                    "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
                    "Accept": "text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
                resp = requests.get(url, headers=headers).text
                html = etree.HTML(resp)
                citing_num = html.xpath('//*[@id="citing-papers"]/div[2]/div/div[1]')
                for i in citing_num:
                    url_add = i.xpath('./div/a/@href')
                    self.url_list.extend(url_add)
                print(len(self.url_list))
        #上面是爬取第一个文献的参考文献
        #下面递归爬取每一篇文献的第一页参考文献和被引文献，都加入url_list里
        if isinstance(response.xpath('//*[@id="citing-papers"]/div[2]/div/div[1]/div[1]/a/@href').get(),str):
            citing_num = response.xpath('//*[@id="citing-papers"]/div[2]/div/div[1]')
            for i in citing_num:
                url_add = i.xpath('./div/a/@href').extract()
                self.url_list.extend(url_add)
        else:
            references_sum=response.xpath('//*[@id="references"]/div[2]/div/div[2]')
            for i in references_sum:
                url_add = i.xpath('./div/a/@href').extract()
                self.url_list.extend(url_add)


        #title
        items = SemanticItem()
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/h1/text()').get(), str):
            items['title']= response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/h1/text()').get()
        else:
            items['title']='null'

        #abstract
        if isinstance(response.xpath('//body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/span/text()').get(), str):
            items['abstract'] = response.xpath('//body/div[1]/div[1]/div[2]/div/div[1]/div/div/div[1]/div/div[1]/div/span/text()').get()
        else:
            items['abstract'] = 'null'

        #authors
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[1]/span/span').get(), str):
            authors=response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[1]/span/span')
            for i in authors:
                a = i.xpath('./span/a/span/span/text()').extract()
                items['authors'] = a
        else:
            items['authors'] = 'null'

        #doi
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[1]/li[1]/section/a/text()').get(), str):
            items['doi'] = response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[1]/li[1]/section/a/text()').get()
        else:
            items['doi'] = 'null'

        #url
        items['url'] = response.xpath('/html/head/link[1]/@href').get()
        #year
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[2]/span/span/span/span/text()').get(), str):
            date = response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[2]/span/span/span/span/text()').get()
            items['year'] = date[-4:]
            items['month'] = re.sub("[\u4e00-\u9fa5\0-9\,\。]", "", date)
        else:
            items['year'] = 'null'
            items['month'] = 'null'
        #month
        #type
        items['type'] = 'conference'
        #source
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[3]/text()').get(), str):
            items['source'] = response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[3]/text()').get()
        else:
            items['source'] = 'null'
        #先检查一下其是否有，如果没有直接赋值空，其他同理
        #venue
        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[4]/span/text()').get(), str):
            items['venue'] = response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/ul[2]/li[4]/span/text()').get()
        else:
            items['venue'] = 'null'


        #graph
        if isinstance(response.xpath('//*[@id="extracted"]/div[2]/div/div/ul').get(), str):
            graph = response.xpath('//*[@id="extracted"]/div[2]/div/div/ul')
            for i in graph:
                a = i.xpath('./li/a/figure/div/img/@src').extract()
                items['graph_url'] = a
        else:
            items['graph_url'] = 'null'


        items['graph_path'] = 'D:\VSCode\scrapy爬虫\Semantic\graph'
        #video
        items['video_url'] = 'null'
        items['video_path'] = 'null'
        items['thumbnail_url'] = 'null'

        if isinstance(response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/a/@href').get(), str):
            items['pdf_url'] = response.xpath('//*[@id="main-content"]/div[1]/div/div/div[1]/div/div[2]/div[1]/div/div[2]/div/a/@href').get()
        else:
            items['pdf_url'] = 'null'

        items['pdf_path'] = 'null'
        items['latex_url'] = 'null'
        items['latex_path'] = 'null'
        items['ppt_url'] = 'null'
        items['ppt_path'] = 'null'
        #inCitations
        #参考文献取得是第一页的部分文章题目
        if isinstance(response.xpath('//*[@id="citing-papers"]/div[2]/div/div[1]').get(), str):
            inCitations = response.xpath('//*[@id="citing-papers"]/div[2]/div/div[1]')
            for i in inCitations:
                a = i.xpath('./div/a/h3/text()').extract()
                items['inCitations'] = a
        else:
            items['inCitations'] = 'null'


        #OutCitations
        #参考文献取得是第一页的部分文章题目
        if isinstance(response.xpath('//*[@id="references"]/div[2]/div/div[2]').get(), str):
            OutCitations=response.xpath('//*[@id="references"]/div[2]/div/div[2]')
            for i in OutCitations:
                a = i.xpath('./div/a/h3/text()').extract()
                items['outCitations'] = a
        else:
            items['outCitations'] = 'null'


        yield items
        print(self.offset)
        self.url_list= np.unique(self.url_list)
        self.url_list = self.url_list.tolist()
        url = 'https://www.semanticscholar.org' + self.url_list[self.offset]
        self.offset += 1
        #每一次都将url_list去重，保证加进来的之前没有加过

        yield scrapy.Request(url=url, callback=self.parse,dont_filter=True)
        print(len(self.url_list))
        #print(self.url_list)
        print('success')
        #pass


