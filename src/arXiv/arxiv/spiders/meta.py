import re
import json

import scrapy
from scrapy.utils.spider import iterate_spider_output
# from scrapy.pipelines.files import FilesPipeline


class MetaSpider(scrapy.spiders.XMLFeedSpider):
    name = 'meta'
    allowed_domains = ['export.arxiv.org']
    start_urls = ['http://export.arxiv.org/oai2?verb=ListRecords&set=q-fin&metadataPrefix=arXiv']
    itertag = 'record'
    cs_map_file = 'cs.json'
    math_map_file = 'math_area.json'
    stat_map_file = 'statistic_area.json'
    econ_map_file = 'economic_area.json'
    eess_map_file = 'eess_area.json'
    physics_map_file = 'physics_area.json'
    qbio_map_file = 'qbio_area.json'
    qfin_map_file = 'qfin_area.json'

    custom_settings = {
        'ITEM_PIPELINES': {
            'arxiv.pipelines.ArxivMetaPipeline': 300,
        },
        'MONGO_COLLECTION': 'arXiv',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(self.qfin_map_file) as f:
            self.qfin_cate_map = json.load(f)

    def parse_node(self, response, node):
        node.register_namespace('n', 'http://arxiv.org/OAI/arXiv/')

        item = {}
        item['arxiv_id'] = node.xpath('n:metadata/n:arXiv/n:id/text()').get()
        # 论文标题
        title = node.xpath('n:metadata/n:arXiv/n:title/text()').get()
        item['title'] = ' '.join(title.split())
        # 论文摘要
        abstract = node.xpath('n:metadata/n:arXiv/n:abstract/text()').get()
        item['abstract'] = ' '.join(abstract.split())
        # 论文年月
        item['arxiv_created_date'] = node.xpath('n:metadata/n:arXiv/n:created/text()').get()
        item['year'] = item['arxiv_created_date'].split('-')[0]
        item['month'] = str(int(item['arxiv_created_date'].split('-')[1]))
        # 论文DOI
        doi = node.xpath('n:metadata/n:arXiv/n:doi/text()').get()
        if doi is None:
            item['doi'] = ''
        else:
            item['doi'] = f'https://doi.org/{doi}'
        # 论文作者
        item['authors'] = []
        for author in node.xpath('n:metadata/n:arXiv/n:authors/n:author'):
            first_name = author.xpath('n:forenames/text()').get('')
            last_name = author.xpath('n:keyname/text()').get('')
            name = first_name + ' ' + last_name
            item['authors'].append(name)
        # 论文主页
        item['url'] = f'https://arxiv.org/abs/{item["arxiv_id"]}'
        # 论文PDF链接
        item['pdf_url'] = f'https://arxiv.org/pdf/{item["arxiv_id"]}.pdf'
        # 论文latex链接
        item['latex_url'] = f'https://arxiv.org/e-print/{item["arxiv_id"]}'

        cates_tag = node.xpath('n:metadata/n:arXiv/n:categories/text()').get().split()
        # cates_abbr = [c[3:] for c in cates_tag if c.startswith('cs.')]
        cates_abbr = [c[6:] for c in cates_tag if c.startswith('q-fin.')]
        # cates = [c + ' - ' + self.cs_cate_map.get(c, 'Other') for c in cates_abbr]
        cates = [c + ' - ' + self.qfin_cate_map.get(c, 'Other') for c in cates_abbr]
        item['arxiv_categories'] = cates

        journal_ref = node.xpath('n:metadata/n:arXiv/n:journal-ref/text()').get()
        if journal_ref is None:
            item['venue'] = 'Quantitative Finance'
            item['type'] = 'journal'
        else:
            item['venue'] = journal_ref
            if "conference" in journal_ref:
                item['type'] = 'conference'
            else:
                item['type'] = 'journal'

        comments = node.xpath('n:metadata/n:arXiv/n:comments/text()').get()
        if comments is None:
            item['source'] = ''
        else:
            if "Springer" in comments:
                item['source'] = 'Springer'
            else:
                item['source'] = ''

        acm = node.xpath('n:metadata/n:arXiv/n:acm-class/text()').get()
        if acm is None:
            item['source'] = ''
        else:
            item['source'] = 'ACM'

        msc = node.xpath('n:metadata/n:arXiv/n:msc-class/text()').get()
        if msc is None:
            item['source'] = ''
        else:
            item['source'] = 'MSC'

        return item

    def parse_nodes(self, response, nodes):
        match = re.search(
            '<resumptionToken .*>(.*)</resumptionToken>',
            response.text[-150:],
        )
        if match is not None:
            resumption_token = match.group(1).strip()
            self.logger.info(f'resumption_token: {resumption_token}')
            if resumption_token != '':
                yield scrapy.Request(
                    f'http://export.arxiv.org/oai2?verb=ListRecords&resumptionToken={resumption_token}',
                    callback=self._parse,
                )

        for selector in nodes:
            ret = iterate_spider_output(self.parse_node(response, selector))
            for result_item in self.process_results(response, ret):
                yield result_item
