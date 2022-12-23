import scrapy
import calendar
from scrapy.linkextractors import LinkExtractor
import re
# from pymongo import mongo_client
from ..items import SciencedirectItem


class ScienceDirectSpySpider(scrapy.Spider):
    name = 'science_direct_spy'
    allowed_domains = ['sciencedirect.com']
    start_urls = ['https://www.sciencedirect.com/science/article/pii/S2090123221001491']  # NMN
    # start_urls = ['https://www.sciencedirect.com/science/article/abs/pii/S1473309921007222']
    # start_urls = ['https://www.sciencedirect.com/science/article/pii/S1473309921007568']
    start_urls = ['https://www.sciencedirect.com/science/article/pii/B9780240812281000015']  # Art

    def parse(self, response):
        # 是否下载pdf
        download_pdf = False
        download_image = False

        pdf_item = {}
        science_direct_item = SciencedirectItem()

        # ScienceDirect论文标题
        title = ''.join(response.xpath('//span[@class="title-text"]//text()').extract())
        # 论文摘要
        abstract = ''.join(response.xpath('//div[@class="abstract author"]/div/p//text()').extract())
        # 姓名列表
        given_name_list = response.xpath(
            '//div[@class="author-group"]/button//span[@class="text given-name"]/text()').extract()  # 姓列表
        surname_list = response.xpath(
            '//div[@class="author-group"]/button//span[@class="text surname"]/text()').extract()  # 名列表
        authors = [a + ' ' + b for a, b in zip(given_name_list, surname_list)]
        # 论文doi
        doi = response.xpath('//a[@class="doi"]/@href').extract_first()
        # 论文主页
        url = response.request.url
        # 论文种类, 日期
        month = ''
        if len(response.xpath('//div[@class="text-xs u-margin-xs-bottom"]/text()')) and not len(
                response.xpath('//div[@class="text-xs"]')):  # conference
            type = "conference"
            date = response.xpath(
                '//div[@class="text-xs u-margin-xs-bottom"]/text()').extract_first().split(',')[1].strip().split(' ')
            try:
                if len(date) == 1:
                    month = ''
                elif len(date) == 2:
                    month = list(calendar.month_name).index(date[0].split('-')[0].split('–')[0])
                else:
                    month = list(calendar.month_name).index(date[1].split('-')[0].split('–')[0])
                year = date[-1]
            except Exception:
                print('ERROR PARSING DATE:' + url)
        else:  # journal Volume 37, March 2022, Pages 267-278
            type = "journal"
            if len(response.xpath('//div[@class="text-xs"]/text()').extract_first()) == 4 and (
                    response.xpath('//div[@class="text-xs"]/text()').extract_first()[0] == '2' or
                    response.xpath('//div[@class="text-xs"]/text()').extract_first() == '1'):  # 年份开头
                date = [response.xpath('//div[@class="text-xs"]/text()').extract_first()]
            else:
                date = response.xpath('//div[@class="text-xs"]/text()').extract()[1].split(' ')
            try:
                if len(date) == 1:
                    month = ''
                elif len(date) == 2:
                    month = list(calendar.month_name).index(date[0].split('-')[0].split('–')[0])
                else:
                    month = list(calendar.month_name).index(date[1].split('-')[0].split('–')[0])
                year = date[-1]
            except Exception:
                print('ERROR PARSING DATE:' + url)
        # 会议或期刊名称
        venue = response.xpath('//a[@class="publication-title-link"]/text()').extract_first()
        if not venue:
            venue = response.xpath('//a[@class="publication-brand-title-link"]//text()').extract_first()

        # 来源
        source = "Elsevier"
        # 图像在线链接
        graph_url = ''
        graph_path = ''
        if len(response.xpath('//figure[@class="figure text-xs"]')):
            # graph_url = response.xpath('//figure[@class="figure text-xs"]//img/@src').extract_first()  # 缩略图
            graph_url = response.xpath('//a[@class="anchor download-link u-font-sans"]/@href').extract_first()  # 高清大图
            image_item = {}
            image_item['image_urls'] = [graph_url]
            if download_image:
                yield image_item
            graph_path = "/download/image/" + graph_url.split('/')[-1]
        # 视频在线链接
        video_url = ''
        video_path = ''
        thumbnail_url = ''  # 视频缩略图
        # pdf链接--可下载  ['ViewPDF', 'DownloadFullIssue']
        pdf_options = response.xpath('//ul[@aria-label="PDF Options"]/li/@class').extract()
        pdf_url = ''
        pdf_path = ''
        if 'ViewPDF' in pdf_options:
            le = LinkExtractor(restrict_xpaths='//ul[@aria-label="PDF Options"]')
            pdf_url = le.extract_links(response)[0].url
            # pdf_url = response.xpath('//ul[@aria-label="PDF Options"]/li/a/@href').extract_first()
            if pdf_url:
                pdf_path = "/download/pdf/" + pdf_url.split('=')[-1]
                pdf_item['file_urls'] = [pdf_url]
                if download_pdf:
                    yield pdf_item
            else:
                pdf_url = ''

        # pdf链接--OpenManuscript
        elif "accessbar-item-hide-from-initial accessbar-item-hide-from-xs accessbar-item-show-from-md OpenManuscript" \
                in pdf_options:
            le = LinkExtractor(
                restrict_xpaths='//ul[@aria-label="PDF Options"]//li[@class="accessbar-item-hide-from-initial '
                                'accessbar-item-hide-from-xs accessbar-item-show-from-md OpenManuscript"]')
            pdf_url = le.extract_links(response)[0].url
            # pdf_url = response.xpath('//ul[@aria-label="PDF Options"]/li/a/@href').extract_first()
            if pdf_url:
                pdf_path = "/download/pdf/" + pdf_url.split('=')[-1]
                pdf_item['file_urls'] = [pdf_url]
                if download_pdf:
                    yield pdf_item
            else:
                pdf_url = ''
        # pdf链接--需购买
        else:
            le = LinkExtractor(restrict_xpaths='//ul[@aria-label="PDF Options"]')
            pdf_url = le.extract_links(response)[0].url

        # latex路径
        latex_url = ''
        latex_path = ''
        # PPT路径
        ppt_url = ''
        ppt_path = ''
        # 被引用数量
        inCitations = re.findall(r"\d+", response.xpath('//header[@id="citing-articles-header"]//text()').extract_first())[0]
        # 引用数量
        outCitations = ''

        # 构造item
        science_direct_item["title"] = title
        science_direct_item["abstract"] = abstract
        science_direct_item["authors"] = authors
        science_direct_item["doi"] = doi
        science_direct_item["url"] = url
        science_direct_item["year"] = year
        science_direct_item["month"] = month
        science_direct_item["type"] = type
        science_direct_item["venue"] = venue
        science_direct_item["source"] = source
        science_direct_item["graph_url"] = graph_url
        science_direct_item["graph_path"] = graph_path
        science_direct_item["video_url"] = video_url
        science_direct_item["video_path"] = video_path
        science_direct_item["thumbnail_url"] = thumbnail_url
        science_direct_item["pdf_url"] = pdf_url
        science_direct_item["pdf_path"] = pdf_path
        science_direct_item["latex_url"] = latex_url
        science_direct_item["latex_path"] = latex_path
        science_direct_item["ppt_url"] = ppt_url
        science_direct_item["ppt_path"] = ppt_path
        science_direct_item["inCitations"] = inCitations
        science_direct_item["outCitations"] = outCitations
        yield science_direct_item

        le_next = LinkExtractor(restrict_xpaths='//div[@id="recommended-articles"]//div[@class="sub-heading"]')
        pdf_url_list = [link.url for link in le_next.extract_links(response)]
        for next_url in pdf_url_list:
            yield scrapy.Request(next_url, callback=self.parse, dont_filter=False)
        # -*- coding: utf-8-*-
