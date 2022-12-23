from elasticsearch import Elasticsearch
import json

hosts = 'http://43.143.163.72:9200/'

es = Elasticsearch(hosts=hosts)

datas = []

for i in range(500):
    f = open('./tmp/database'+str(i)+".json")
    for line in f.readlines():
        dic = json.loads(line)
        datas.append(dic)


pbar = tqdm(datas)
for data in pbar:
    es.index(index='citations', body=data)