'''
__author__: Jiaming Shen
__description__: Obtain top-ranked documents for each node in taxonomy
__latest_update__: 10/02/2017
'''
import math
import time
import argparse
from elasticsearch import Elasticsearch
from collections import Counter

INDEX_NAME = "dblp"
TYPE_NAME = "dblp_papers"

def obtain_allowed_doc_ids(taxonName, root):
  filePath = root + taxonName[1:] + "/doc_ids.txt"
  allowed_ids = []
  with open(filePath, "r") as fin:
    for line in fin:
      docID = int(line.strip())
      allowed_ids.append(docID)
  return set(allowed_ids)



def main(args):
  es = Elasticsearch()
  if (not args.N):
    args.N = 10
  else:
    args.N = int(args.N)
  with open(args.input, "r") as fin, open(args.output, "w") as fout:
    for line in fin:
      line = line.strip()
      segs = line.split("\t")
      taxonName = segs[0]
      print("Ranking document under node %s" % taxonName)
      if len(segs) < 2:
        print("[Warning] No terms under node %s" % taxonName)
        fout.write(taxonName + "\t" + "Query: None" + "\n")
        fout.write("=" * 80 + "\n")
        continue

      terms = segs[1].split(",")
      allowed_ids = obtain_allowed_doc_ids(taxonName, args.root)

      num_terms = len(terms)
      ## use top-10 terms as query
      query_terms_list = [taxonName.split("/")[-1]]
      query_terms_list.extend([ele.split(":")[0] for ele in terms][:max(10, num_terms)])
      query_string = " OR ".join(query_terms_list)

      search_body = {
        "size": 100,
        "query": {
          "query_string": {
            "default_field": "document",
            "query": query_string
          }
        }
      }

      res = es.search(index=INDEX_NAME, request_timeout=180, body=search_body)
      documents = []
      for hit in res["hits"]["hits"]:
        docID = hit["_source"]["docID"]
        if docID in allowed_ids:
          documents.append(hit["_source"]["document"])

      ## output to file
      fout.write(taxonName + "\t" + "Query: " + query_string + "\n")
      for idx, doc in enumerate(documents):
        fout.write(str(idx+1) + "\t")
        fout.write(doc + "\n")
        if idx >= args.N:
          break
      fout.write("="*80+"\n")

if __name__ == '__main__':
  # python3 obtain_facet_document.py -input ../../data/dblp/taxonomies/global_taxonomy.txt -output ./global_taxon_doc.txt -root ../../data/dblp/our-l3-0.15 -N 10
  parser = argparse.ArgumentParser(prog='obtain_facet_document.py',
                                   description='Obtain top-ranked documents for each node in faceted taxonomy.')
  parser.add_argument('-input', required=True, help='Input path of taxonomy')
  parser.add_argument('-output', required=True, help='Output path of documents')
  parser.add_argument('-root', required=True, help='The root path of taxonomy, no slash in the end')
  parser.add_argument('-N', required=False, help='Number of top ranked documents.')
  args = parser.parse_args()

  start = time.time()
  main(args)
  end = time.time()
  print("Finish extracting documents, using %s seconds" % (end-start))
