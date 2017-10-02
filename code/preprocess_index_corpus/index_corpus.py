'''
__author__: Jiaming Shen
__description__: Index corpus
__latest_update__: 10/02/2017
'''
import time
import re
import sys 
import os
import json
from collections import defaultdict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

if __name__ == '__main__':
    inputFilePath = "/shared/data/jiaming/local-embedding/data/dblp/raw/papers.txt"
    logFilePath = "./log_20171002.txt"
    
    INDEX_NAME = "dblp"
    TYPE_NAME = "dblp_papers"

    es = Elasticsearch()

    with open(inputFilePath, "r") as fin, open(logFilePath, "w") as fout:
        start = time.time()
        bulk_size = 5000 # number of document processed in each bulk index
        bulk_data = [] # data in bulk index

        cnt = 0
        for line in fin: ## each line is single document
            line = line.strip()

            data_dict = {}
            data_dict["docID"] = cnt
            data_dict["document"] = line


            ## Put current data into the bulk
            op_dict = {
                "index": {
                    "_index": INDEX_NAME,
                    "_type": TYPE_NAME,
                    "_id": data_dict["docID"]
                }
            }

            bulk_data.append(op_dict)
            bulk_data.append(data_dict)       
                    
            ## Start Bulk indexing
            cnt += 1
            if cnt % bulk_size == 0 and cnt != 0:
                tmp = time.time()
                es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
                fout.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
                print("bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
                bulk_data = []
        
        ## indexing those left papers
        if bulk_data:
            tmp = time.time()
            es.bulk(index=INDEX_NAME, body=bulk_data, request_timeout = 180)
            fout.write("bulk indexing... %s, escaped time %s (seconds) \n" % ( cnt, tmp - start ) )
            print("bulk indexing... %s, escaped time %s (seconds) " % ( cnt, tmp - start ) )
            bulk_data = []

        end = time.time()
        fout.write("Finish all indexing. Total escaped time %s (seconds) \n" % (end - start) )
        print("Finish all indexing. Total escaped time %s (seconds) " % (end - start) )