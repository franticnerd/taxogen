'''
__author__: Jiaming Shen
__description__: Add taxonID field in the input json file
__latest_update__: 10/22/2017
'''
import time
import argparse
import json
from collections import defaultdict

def main(args):
  docID2taxonIDs = {}
  with open(args.doc_assign_in, "r") as fin:
    for line in fin:
      line = line.strip()
      if line:
        segs = line.split("\t")
        docID2taxonIDs[segs[0]] = segs[1]

  doc_ids = []
  with open(args.doc_cnt2doc_id, "r") as fin:
    for line in fin:
      line = line.strip()
      doc_ids.append(line)

  cnt = 0
  with open(args.json_in, "r") as fin, open(args.json_out, "w") as fout:
    for line in fin:
      line = line.strip()
      new_doc_id = doc_ids[cnt]
      cnt += 1
      if cnt % 10000 == 0:
        print("Processed %s documents" % cnt)

      paper = json.loads(line)
      if (new_doc_id == "-1") or (new_doc_id not in docID2taxonIDs): # not appear in taxonGen interested documents
        taxonIDs = "0_0_0"
      else:
        taxonIDs = "0_0_0," +  docID2taxonIDs[new_doc_id]

      paper["taxonIDs"] = taxonIDs
      json.dump(paper, fout)
      fout.write("\n")


if __name__ == '__main__':
  # python3 complete_json.py -json_in /shared/data/jiaming/semantic_scholar/cs/semantic_scholar_jsons.txt -json_out /shared/data/jiaming/semantic_scholar/cs/semantic_scholar_jsons_with_taxon.txt -doc_assign_in ../../data/eecs/doc_assignments-ids.txt -doc_cnt2doc_id ../../data/eecs/input/doc_cnt2doc_id.txt
  parser = argparse.ArgumentParser(prog='complete_json.py',
                                   description='Obtain a unified id for each taxon in the hierarchy and return each document'
                                               '\'s matched taxonID')
  parser.add_argument('-json_in', required=True, help='Input path of JSON')
  parser.add_argument('-json_out', required=True, help='Output path of JSON')
  parser.add_argument('-doc_assign_in', required=True, help='Input path of documnet assignment file')
  parser.add_argument('-doc_cnt2doc_id', required=False, help='Mapping file of raw document id to new document id')
  args = parser.parse_args()

  start = time.time()
  main(args)
  end = time.time()
  print("Finish Adding taxonID field in the json file "
        "using %s seconds" % (end-start))
