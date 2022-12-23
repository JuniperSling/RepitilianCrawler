import requests
from lxml import etree
import numpy as np
#url = "https://www.sciencedirect.com/science/article/pii/S2090123221001491"
#headers = {"User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
           #"Accept": "text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",'Connection': 'close'}
#response=requests.get(url,headers=headers).text
#html=etree.HTML(response)
#print(html.xpath('//*[@id="screen-reader-main-title"]/span/text()'))
#a={"User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",}
#a['Connection']='close'
# print(a)
lists = ['1','1','2','3','4','6','6','2','2','9']
print(lists[0])
lists = np.unique(lists)
lists = lists.tolist()
print(type(lists))