### 数据清洗

arXiv、SemanticScholar空字段统一为null，并记录存在空字段记录数以统计字段覆盖率：

```js
db.arXiv.updateMany({ doi: "" }, { $set: { "doi": null }});
db.arXiv.updateMany({ source: "" }, { $set: { "source": null }});
db.arXiv.updateMany({ }, { $set: { "graph_url": null, "graph_path": null, "video_url": null, "video_path": null, "thumbnail_url": null,  "ppt_url": null, "ppt_path": null,  "inCitations": null, "outCitations": null}});

db.SemanticScholar.updateMany({ abstract: "null" }, { $set: { "abstract": null }});
db.SemanticScholar.updateMany({ doi: "null" }, { $set: { "doi": null }});
db.SemanticScholar.updateMany({ year: "null" }, { $set: { "year": null }});
db.SemanticScholar.updateMany({ month: "null" }, { $set: { "month": null }});
db.SemanticScholar.updateMany({ venue: "null" }, { $set: { "venue": null }});
db.SemanticScholar.updateMany({ source: "null" }, { $set: { "source": null }});
db.SemanticScholar.updateMany({ graph_url: "null" }, { $set: { "graph_url": null, "graph_path": null }});
db.SemanticScholar.updateMany({ pdf_url: "null" }, { $set: { "pdf_url": null, "pdf_path": null }});
db.SemanticScholar.updateMany({ }, { $set: { "video_url": null, "video_path": null, "thumbnail_url": null, "latex_url": null, "latex_path": null, "ppt_url": null, "ppt_path": null }});
db.SemanticScholar.updateMany({ inCitations: "null" }, { $set: { "inCitations": null }});
db.SemanticScholar.updateMany({ outCitations: "null" }, { $set: { "outCitations": null }})
```
SemanticScholar“doi”字段统一格式，拼接特定字符串
```shell
db.SemanticScholar.find({"doi": {$ne:null} }).forEach(function(item){
    db.SemanticScholar.update(
        {"_id":item._id}, 
        { $set : { "doi" : "http://doi.org" + item.doi}} 
    )
})
```
统一文件存储路径
```shell
db.arXiv.updateMany(
  {pdf_url:{"$exists":true}},
  [{
    $set: {pdf_path: {
      $replaceOne: { input:"$pdf_path", find:"download_files/pdf", replacement:"download/arXiv/pdf" }
    }}
  }]
);
db.arXiv.updateMany(
  {latex_url:{"$exists":true}},
  [{
    $set: {latex_path: {
      $replaceOne: { input:"$latex_path", find:"download_files/latex", replacement:"download/arXiv/latex" }
    }}
  }]
);
db.ScienceDirect.updateMany(
  {pdf_url:{"$exists":true}},
  [{
    $set: {pdf_path: {
      $replaceOne: { input:"$pdf_path", find:"download/pdf", replacement:"download/ScienceDirect/pdf" }
    }}
  }]
);
db.ScienceDirect.updateMany(
  {graph_url:{"$exists":true}},
  [{
    $set: {graph_path: {
      $replaceOne: { input:"$graph_path", find:"download/image", replacement:"download/ScienceDirect/image" }
    }}
  }]
);
db.SemanticScholar.updateMany(
  {pdf_url:{"$exists":true}},
  [{
    $set: {pdf_path: {
      $replaceOne: { input:"$pdf_path", find:"download_files/pdf", replacement:"download/SemanticScholar/pdf" }
    }}
  }]
)
```

### 合并操作

下载MongoDB Developer Tools，将数据导出为JSON格式存档：
```shell
mongoexport -d IR -c ScienceDirect -o ./SD.json
mongoexport -d IR -c arXiv -o ./aX.json
mongoexport -d IR -c SemanticScholar -o ./SS.json
```

新建唯一索引title，作为去重依据（存在doi字段为空的记录，故不使用doi去重）：
```shell
db.src.createIndex({title: 1}, {unique: true})
```

依次导入之前存档的JSON文件数据（--upsert 会根据唯一索引去掉重复记录）：
```shell
mongooimport -d IR -c ScienceDirect --upsert -o ./SD.json
mongoexport -d IR -c arXiv --upsert -o ./aX.json
mongoexport -d IR -c SemanticScholar --upsert -o ./SS.json
```
 统计arXiv表中arxiv_categories字段中各标签记录数

下载MongoDB Developer Tools，将数据导出为JSON格式存档：
```shell
db.test.aggregate([
  {$unwind:"$arxiv_categories"},
  {$group:{_id:"$arxiv_categories",num_of_tag:{$sum:1}}},
  {$project:{_id:0,arxiv_categories:"$_id",num_of_tag:1}},
  {$sort:{num_of_tag:-1}}
  ])
```