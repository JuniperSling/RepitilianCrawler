# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import re
import pymongo
import os
from itemadapter import ItemAdapter
import requests
import tarfile

logger = logging.getLogger(__name__)


def untar(fname, dirs):
    """
    解压tar.gz文件
    :param fname: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """

    try:
        t = tarfile.open(fname)
        t.extractall(path=dirs)
        return True
    except Exception as e:
        print(e)
        return False


class ArxivMetaPipeline:

    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'download_files')
        self.pdf_path = os.path.join(self.path, 'pdf')
        self.latex_path = os.path.join(self.path, 'latex')
        if not os.path.exists(self.pdf_path):
            os.mkdir(self.pdf_path)
        if not os.path.exists(self.latex_path):
            os.mkdir(self.latex_path)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings['MONGO_URI'],
            mongo_db=crawler.settings['MONGO_DATABASE'],
            mongo_collection=crawler.settings['MONGO_COLLECTION'],
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        # 将论文标题设置为唯一索引
        self.collection.create_index([('title', 1)], unique=True)

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item = ItemAdapter(item).asdict()

        try:
            intab = r'[?*/\|.:><]'
            filename = re.sub(intab, '', item['title'])
            pdf_path = os.path.join(self.pdf_path, filename + '.pdf')
            latex_path = os.path.join(self.latex_path, filename + '.tar.gz')
            out_path = os.path.join(self.latex_path, filename)
            pdf_path_save = f'/download_files/pdf/{item["title"]}.pdf'
            latex_path_save = f'/download_files/latex/{item["title"]}.tar.gz'
            item['pdf_path'] = pdf_path_save
            item['latex_path'] = latex_path_save
            item['graph_url'] = ''
            item['graph_path'] = ''
            item['video_url'] = ''
            item['video_path'] = ''
            item['thumbnail_url'] = ''
            item['ppt_url'] = ''
            item['ppt_path'] = ''
            item['inCitations'] = ''
            item['outCitations'] = ''
            self.collection.insert_one(item)
            logger.info(f'Mongodb Insert: {item["title"]}')

            # 下载pdf
            r = requests.get(url=item['pdf_url'])
            with open(pdf_path, 'wb+') as f:
                f.write(r.content)
            # 下载latex
            r = requests.get(url=item['latex_url'])
            with open(latex_path, 'wb+') as f:
                f.write(r.content)

            untar(latex_path, out_path)
        except Exception:
            logger.info(f'Already exist:{item["title"]} ')
        return item
