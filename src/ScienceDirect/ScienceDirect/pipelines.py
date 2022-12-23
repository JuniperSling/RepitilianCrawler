# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import pymongo
from scrapy.utils.project import get_project_settings
import csv

settings = get_project_settings()


class SciencedirectPipeline:
    def process_item(self, item, spider):
        return item


class CsvPipeline(object):
    def __init__(self):
        # 生成用于存储除内容外所有内容,分行存储
        self.cfile = open('result.csv', 'a+', encoding='utf-8')
        self.writer = csv.writer(self.cfile)
        self.writer.writerow(['title', 'abstract', 'authors', 'doi', 'url', 'year', 'month', 'type',
                              'venue', 'source', 'graph_url', 'graph_path', 'video_url', 'video_path', 'thumbnail_url',
                              'pdf_url', 'pdf_path', 'latex_url', 'latex_path', 'ppt_url', 'ppt_path', 'inCitations',
                              'outCitations'])

    def process_item(self, item, spider):
        self.writer.writerow([item['title'], item['abstract'], item['authors'], item['doi'], item['url'],
                              item['year'], item['month'], item['type'], item['venue'], item['source'],
                              item['graph_url'], item['graph_path'], item['video_url'], item['video_path'],
                              item['thumbnail_url'], item['pdf_url'], item['pdf_path'], item['latex_url'],
                              item['latex_path'], item['ppt_url'], item['ppt_path'], item['inCitations'],
                              item['outCitations']])
        return item

    def file_close(self):
        # 关闭文件
        self.cfile.close()


class MongoDBPipeline(object):
    def __init__(self):
        # 链接数据库
        self.client = pymongo.MongoClient('mongodb://IR:bit2022ir@43.143.163.72:27017/')
        self.db = self.client['IR']  # 获得数据库的句柄
        self.coll = self.db['ScienceDirect']  # 获得collection的句柄

    def process_item(self, item, spider):
        postItem = dict(item)  # 把item转化成字典形式
        self.coll.insert_one(postItem)  # 向数据库插入一条记录
        # return item  # 在控制台输出原item数据
