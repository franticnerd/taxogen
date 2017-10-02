'''
__author__: Jiaming Shen
__description__: Create index with static mapping in ES (a.k.a. define schema).
__latest_update__: 10/02/2017
'''
import time
import re
import sys
import os
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

if __name__ == '__main__':
    INDEX_NAME = "dblp"
    TYPE_NAME = "dblp_papers"
    NUMBER_SHARDS = 1 # keep this as one if no cluster
    NUMBER_REPLICAS = 0 

    '''
    following is the defined schema
    totally 2 fields: 
    id, sentence
    '''
    request_body = {
        "settings": {
            "number_of_shards": NUMBER_SHARDS,
            "number_of_replicas": NUMBER_REPLICAS
        },
        "mappings": {
            TYPE_NAME: {
                "properties": {
                    "docID": {
                        "type": "keyword"
                    },
                    "document": {
                        "type": "text"
                    }
                }
            }
        }
    }

    es = Elasticsearch()
    if es.indices.exists(INDEX_NAME):
        res = es.indices.delete(index = INDEX_NAME)
        print("Deleting index %s , Response: %s" % (INDEX_NAME, res))
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print("Create index %s , Response: %s" % (INDEX_NAME, res))