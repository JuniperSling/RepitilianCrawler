# [IR_ReptiliaCrawler](https://github.com/orgs/BITCS-Information-Retrieval-2022/teams/ir_reptiliacrawler)

## 1. 概述

我们组使用Scrapy框架进行爬虫的搭建，针对[arXiv](https://arxiv.org), [Semantic Scholar](https://www.semanticscholar.org), [Science Direct](https://www.sciencedirect.com)三个不同的网页，由三位不同的成员进行页面分析和抓取工作，由于居家期间独自完成，因此虽然采用同一套框架，但是在具体实现的细节上可能存在区别，这里分别介绍三个爬虫的实现，为了证明爬虫的下载能力，我们也下载了一部分的`pdf`, `latex`和`image`文件。最后我们组对爬取到的数据进行数据库的合并和统计工作，并基于`Kibana`搭建了搜索界面。

## 2. arXiv 

> 该网页爬虫由郭思涵[@GSHLiberty](https://github.com/GSHLiberty)实现

**主要功能**

通过调用ArXiv提供的 [OAI-PMH API](https://arxiv.org/help/oa/index) 接口实现爬虫，从arXiv上爬取标题、作者、摘要、PDF链接、latex文档等信息。爬取PDF链接、latex文档时需验证是否可下载，并下载一定量的论文以表明爬虫代码具有下载能力。

**文件结构**

> 相关文件位于`/src/arXiv`路径下

```bash
arXiv
    |——arxiv
    |    ├─spiders
    |        │   __init__.py  
    |        │ meta.py       # 爬虫文件
    |    |     __init__.py 
    |    │  items.py         # 定义字段信息 
    |    │  middlewares.py   # 中间件文件
    |    │  pipelines.py     # 管道，持久化文件
    |    │  settings.py      # 详细的配置文件
    |——download_files        # 存储下载到本地的文件
    |    	├─ latex           # 存储LaTeX
    |    	├─pdf              # 存储PDF
    |——scrapy.cfg            # 默认使用的配置文件  
    |——economic_area.json    # Economics 类别缩写对应文件
    |——eess_area.json        # Electrical Engineering and Systems Science 类别缩写对应文件  
    |——math_area.json        # Mathematics 类别缩写对应文件
    |——physics_area.json     # Physics 类别缩写对应文件
    |——qbio_area.json        # Quantitative Biology 类别缩写对应文件
    |——qfin_area.json        # Quantitative Finance 类别缩写对应文件
    |——statistic_area.json   # Statistics 类别缩写对应文件
    |——cs.json               # Computer Science 类别缩写对应文件
```

**页面解析**

```python
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
```

**文章下载**

```python
# 下载pdf
r = requests.get(url=item['pdf_url'])
with open(pdf_path, 'wb+') as f:
    f.write(r.content)
# 下载latex
r = requests.get(url=item['latex_url'])
with open(latex_path, 'wb+') as f:
    f.write(r.content)
```

**增量爬取，进度展示，多线程，用户代理和IP池**

```python
# 对item进行去重。在持久化数据之前判断数据是否已经存在，mongodb的特点是插入块，查询慢，所以采用直接插入方法，将论文标题设为唯一索引。
self.collection.create_index([('title', 1)], unique=True)
try:
    .....
    self.collection.insert_one(item)
    logger.info(f'Mongodb Insert: {item["title"]}')
except Exception:
    logger.info(f'Already exist:{item["title"]} ')
# 链接数据库，获得数据库句柄
def open_spider(self, spider):
    self.client = pymongo.MongoClient(self.mongo_uri)
    self.db = self.client[self.mongo_db]
    self.collection = self.db[self.mongo_collection]
# 日志展示爬取进度
LOG_LEVEL = 'INFO'
logger.info(f'Mongodb Insert: {item["title"]}')
# 在settings.py中设置多线程，提高爬虫效率
CONCURRENT_REQUESTS = 32
# 设置用户代理以及IP池
USER_AGENTs = [
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
  	......
]
PROXY_LIST = [
    {"ip_port": "114.233.40.197:40053"},
    {"ip_port": "117.95.225.77:40011"},
    ....
]
def process_request(self, request, spider):
    user_agent = random.choice(USER_AGENTs)
    request.headers['User-Agent'] = user_agent  # UA
    proxy = random.choice(PROXY_LIST)  # IP
    if 'user_passwd' in proxy:
        # 对账号密码进行编码
        b64_up = base64.b64encode(proxy['user_passwd'].encode())
        # 设置认证
        request.headers['Proxy-Authorization'] = 'Basic ' + b64_up.decode()
        # 设置代理
        request.meta['proxy'] = "http://" + proxy['ip_port']
    else:
        request.meta['proxy'] = "http://" + proxy['ip_port']
```

**启动方法**

1. 运行环境

   - [x] Python == 3.7.0
   - [x] Scrapy == 2.7.1
   - [x] Twisted == 22.4.0
   - [x] lxml == 4.9.1
   - [x] pyOpenSSL == 22.1.0

2. 命令行中切换到工作目录

   ```bash
   cd /src/arXiv
   ```

3. 输入以下命令运行爬虫

   ```bash
   scrapy crawl meta
   ```

## 3. Semantic Scholar

> 该网页爬虫由彭炜[@Crueyl123](https://github.com/Crueyl123)实现

**主要功能**

对于一个给定的文献网址列表，首先爬取第一个文章的参考文献和被引文献，加入文献网址列表，然后依次爬取列表中的文献，同时爬取时也将其参考文献和被引文献加入文献网址列表，并且进行去重操作，保证文献没有重复。
`txsr`第`22`行为第一个文章的地址，改成自己想要的即可

**文件结构**

> 相关文件位于`/src/SemanticScholar`路径下

| 文件名          | 作用         |
| --------------- | ------------ |
| settings.py     | 参数设置     |
| pipelines.py    | 数据保存     |
| ImgPipelines.py | 图片保存     |
| spiders/txsr.py | 主要功能编写 |

**运行方式**

1. 若未安装scrapy环境，请先安装scrapy环境和相关依赖

   ```bash
   conda env create -f requirements.yaml  # Anaconda
   ```

2. cmd切换到`SemanticScholar`文件夹

   ```bash
   cd /src/SemanticScholar
   ```

3. 执行以下命令启动爬虫，该爬虫可自动爬取

   ```bash
   scrapy crawl txsr
   ```

## 4. Science Direct

> 该网页爬虫由于翔[@JuniperSling](https://github.com/JuniperSling)实现

**主要功能**

对于一个给定的网址，爬虫首先解析该页面所有信息。接着将右侧栏的“Recommended Articles”列表下所有文章加入待爬取列表进行爬取。为了实现对pdf下载链接，引用数等动态加载内容的解析，代码中使用了selenium配合ChromeDriver实现。

**文件结构**

> 相关文件位于`/src/ScienceDirect`路径下

| 文件名                        | 作用                             |
| ----------------------------- | -------------------------------- |
| settings.py                   | 参数设置                         |
| pipelines.py                  | 数据格式化和保存                 |
| middlewares.py                | 中间件实现，包含更换UA和IP池功能 |
| spiders/science_direct_spy.py | 爬虫实现，主要页面解析和处理逻辑 |

**运行方式** 

1. 若未安装scrapy环境，请先安装scrapy环境和相关依赖

   ```bash
   conda env create -f requirements.yaml  # Anaconda
   ```

2. 请安装Chrome浏览器和配套版本的[ChromeDriver](https://chromedriver.chromium.org/downloads)，并添加到系统环境变量

3. 在命令行中，cd切换到爬虫文件夹

   ```bash
   cd /src/ScienceDirect
   ```

4. 执行以下命令运行爬虫，该爬虫可自动爬取

   ```bash
   scrapy crawl science_direct_spy
   ```

5. 爬虫启动后，会打开Chrome浏览器界面，请点击网页中的“机构登陆”选项登陆你的机构账号，以获得部分付费pdf的下载权限。就算没有账号，爬虫也会在一分钟后自动开始爬取。

   <img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/Screenshot%202022-12-10%20at%205.31.21%20AM.png" alt="Screenshot 2022-12-10 at 5.31.21 AM" style="zoom:30%;" />

   <img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/Screenshot%202022-12-10%20at%203.35.13%20AM.png" alt="Screenshot 2022-12-10 at 3.35.13 AM" style="zoom:30%;" />

## 5. MongoDB数据库去重和统计

> 数据库的去重和统计由闫羽[@yy823](https://github.com/yy823)实现
>
> 数据库处理源代码见`/src/mongoDB/readme.md`，下文数据来自表格`/src/mongoDB/字段覆盖率.xlsx`

**数据来源及基本信息**

| 字段覆盖率    | ScienceDirect | arXiv   | SemanticScholar |
| ------------- | ------------- | ------- | --------------- |
| title         | 100.00%       | 100.00% | 100.00%         |
| abstract      | 93.83%        | 100.00% | 83.38%          |
| authors       | 100.00%       | 100.00% | 99.99%          |
| doi           | 100.00%       | 40.80%  | 100.00%         |
| url           | 100.00%       | 100.00% | 45.12%          |
| year          | 100.00%       | 100.00% | 99.63%          |
| month         | 96.41%        | 100.00% | 86.71%          |
| type          | 100.00%       | 100.00% | 100.00%         |
| venue         | 100.00%       | 100.00% | 81.30%          |
| source        | 100.00%       | 16.00%  | 100.00%         |
| graph_url     | 68.20%        | 0.00%   | 53.90%          |
| graph_path    | 68.20%        | 0.00%   | 53.90%          |
| video_url     | 0.00%         | 0.00%   | 0.00%           |
| video_path    | 0.00%         | 0.00%   | 0.00%           |
| thumbnail_url | 0.00%         | 0.00%   | 0.00%           |
| pdf_url       | 100.00%       | 100.00% | 54.88%          |
| pdf_path      | 100.00%       | 100.00% | 54.88%          |
| latex_url     | 0.00%         | 100.00% | 0.00%           |
| latex_path    | 0.00%         | 100.00% | 0.00%           |
| ppt_url       | 0.00%         | 0.00%   | 0.00%           |
| ppt_path      | 0.00%         | 0.00%   | 0.00%           |
| inCitations   | 100.00%       | 0.00%   | 79.14%          |
| outCitations  | 0.00%         | 0.00%   | 98.17%          |
| 总记录数      | 19412         | 37695   | 296197          |

<img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/2.png" alt="2" style="zoom:15%;" />

**去重合并后数据信息**

|                | 字段覆盖率 |
| -------------- | ---------- |
| title          | 100.00%    |
| abstract       | 90.68%     |
| authors        | 100.00%    |
| doi            | 73.72%     |
| url            | 100.00%    |
| year           | 99.82%     |
| month          | 92.66%     |
| type           | 100.00%    |
| venue          | 90.50%     |
| source         | 72.05%     |
| graph_url      | 38.79%     |
| graph_path     | 38.79%     |
| video_url      | 0.00%      |
| video_path     | 0.00%      |
| thumbnail_url  | 0.00%      |
| pdf_url        | 72.23%     |
| pdf_path       | 72.23%     |
| latex_url      | 32.45%     |
| latex_path     | 32.45%     |
| ppt_url        | 0.00%      |
| ppt_path       | 0.00%      |
| inCitations    | 89.59%     |
| outCitations   | 82.49%     |
| 合并后总记录数 | 116161     |

<img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/1.png" alt="1" style="zoom:15%;" />


其中各数据源占比为

|        | ScienceDirect | arXiv  | SemanticScholar |
| ------ | ------------- | ------ | --------------- |
| 记录数 | 19259         | 37691  | 59211           |
| 占比   | 16.58%        | 32.45% | 50.97%          |

<img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/3.png" alt="3" style="zoom:15%;" />

**arXiv爬虫领域分布**

> 数据源`/src/mongoDB/arxiv领域标签统计.xlsx`

<img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/0EE321A0144F2F7C48037618F397AC19.png" alt="0EE321A0144F2F7C48037618F397AC19" style="zoom:60%;" />

## 5. elasticsearch + Kibana 

> 该检索前端由赵曰皓[@zyhsuperman](https://github.com/zyhsuperman)实现

**主要功能**

我们的搜索前端网页部署在远程服务器上，通过`43.143.163.72:9200`和`43.143.163.72:5601`公网访问。

检索效果主要由`Kibana`的`view`展示。

**文件结构**

> 相关文件位于`/Code/Kibana`路径下

| 文件名            | 作用                                                         |
| ----------------- | ------------------------------------------------------------ |
| getdata.py        | 分多线程从数据库中读取数据，对数据字段进行简单的处理，存入json文件中，为创建elasticsearch的索引做数据准备 |
| build_ciations.sh | shell脚本文件，建立elasticsearch索引，索引字段包括题目、作者、摘要、doi、期刊和年份。其中题目、作者、摘要、期刊为模糊查询，doi和年份主要为精确查询。 |
| ES.py             | 为脚本文件建立的索引添加数据，数据为getdata.py处理之后得到的数据。 |

**Kibana部署**

1. 检查系统是否安装java，没有java环境需要手动配置java

2. 下载Kibana服务安装包： <https://www.elastic.co/cn/downloads/kibana>

3. 修改配置文件如下：（使Kibana可以公网访问）

   ```sh
   server.port:5601
   server.host:0000
   ```

**部署结果**

- 网页访问 <http://43.143.163.72:5601> 进入Kibana页面

- 打开侧边栏选择`Discover`，可以看到test这个view下的结果：

  <img src="https://milagro-pics.oss-cn-beijing.aliyuncs.com/img/result.png" alt="avatar" style="zoom:30%;" />

## 6. PPT 最终展示

> PPT和最终效果展示由刘昕飏[@summerevel](https://github.com/summerevel)实现

PPT可以在我们的[GitHub提交](https://github.com/BITCS-Information-Retrieval-2022/project-1-ir_reptiliacrawler/blob/main/信息检索.pptx)中找到

## 7. 组员名单

> 只是几个学生的仓促应付作业，再次感谢以下组员们的支持和帮助（排名不分先后）

| 姓名                                                 | 任务                |
| ---------------------------------------------------- | ------------------- |
| 郭思涵[@GSHLiberty ](https://github.com/GSHLiberty)  | arXiv爬虫           |
| 刘昕飏[@summerevel](https://github.com/summerevel)   | PPT和效果展示汇报   |
| 彭炜[@Crueyl123](https://github.com/Crueyl123)       | SemanticScholar爬虫 |
| 于翔[@JuniperSling](https://github.com/JuniperSling) | ScienceDirect爬虫   |
| 闫羽[@yy823](https://github.com/yy823)               | 数据库去重和统计    |
| 赵曰皓[@zyhsuperman](https://github.com/zyhsuperman) | Kibana前端          |
