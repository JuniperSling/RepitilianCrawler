from pyspark import SparkConf, TaskContext
from pyspark.sql import SparkSession
import json

PART = 500
MONGOURI = 'mongodb://IR:bit2022ir@43.143.163.72:27017/IR.src'

myconf = SparkConf() \
    .set("spark.jars.packages",
         "org.mongodb.spark:mongo-spark-connector_2.12:2.4.1") \
    .set("spark.local.dir", "./public_place1/tmp, ./public_place2/tmp") \
    .set("spark.driver.memory", "100G") \
    .set("spark.driver.maxResultSize", "100G") \
    .set("spark.executor.heartbeatInterval", "60s") \
    .set("spark.network.timeout", "600s")
spark = SparkSession.builder \
    .config(conf=myconf) \
    .getOrCreate()

data = spark.read.format("com.mongodb.spark.sql.DefaultSource") \
    .option("uri", MONGOURI).load().repartition(PART).rdd

print('data loading finish\n')


def save_json(part):
    pid = TaskContext().partitionId()
    f = open('./tmp/database{}.json'.format(pid), 'w')
    for raw in part:
        payload = raw
        record = {
            'title': payload[17],
            'abstract': payload[1],
            'authors': payload[2],
            'doi': payload[3][8:],
            'year': payload[23],
            'venue': payload[20]
        }
        f.write('{}\n'.format(json.dumps(record)))
    f.close()


data.foreachPartition(save_json)
