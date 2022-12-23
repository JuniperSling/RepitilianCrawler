curl -X DELETE http://43.143.163.72:9200/citations
curl -H 'Content-Type: application/json' -X PUT 'http://43.143.163.72:9200/citations?pretty' -d'
{
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "title" : {"type": "text"},
      "authors" : {"type": "text"},
      "abstract" : {"type": "text"},
      "doi" : {"type": "keyword"},
      "year" : {"type": "keyword"},
      "venue" : {"type": "text"}
    }
  }
}
'
