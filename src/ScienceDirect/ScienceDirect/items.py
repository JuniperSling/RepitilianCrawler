# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SciencedirectItem(scrapy.Item):
    title = scrapy.Field()
    abstract = scrapy.Field()
    authors = scrapy.Field()
    doi = scrapy.Field()
    url = scrapy.Field()
    year = scrapy.Field()
    month = scrapy.Field()
    type = scrapy.Field()
    venue = scrapy.Field()
    source = scrapy.Field()
    graph_url = scrapy.Field()
    graph_path = scrapy.Field()
    video_url = scrapy.Field()
    video_path = scrapy.Field()
    thumbnail_url = scrapy.Field()
    pdf_url = scrapy.Field()
    pdf_path = scrapy.Field()
    latex_url = scrapy.Field()
    latex_path = scrapy.Field()
    ppt_url = scrapy.Field()
    ppt_path = scrapy.Field()
    inCitations = scrapy.Field()
    outCitations = scrapy.Field()
