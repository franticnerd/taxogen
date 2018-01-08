'''
__author__: Jiaming Shen
__description__: Obtain a unified id for each taxon in the hierarchy and return each document's matched taxonID
__latest_update__: 10/22/2017
'''
import time
import argparse
from collections import defaultdict

def main(args):
  taxonName2taxonID = {}
  taxonLevel2taxonName = defaultdict(list)

  ## generate taxonID
  with open(args.hier_in, "r") as fin, open(args.hier_out, "w") as fout:
    global_cnt = 0
    for line in fin:
      line = line.strip()
      segs = line.split("\t")
      taxonName = segs[0]
      taxonLevel = taxonName.count("/")
      global_cnt += 1

      taxonLevel2taxonName[taxonLevel].append(taxonName)
      level_cnt = len(taxonLevel2taxonName[taxonLevel])

      taxonID = str(taxonLevel)+"_"+str(level_cnt)+"_"+str(global_cnt)
      taxonName2taxonID[taxonName] = taxonID
      fout.write(taxonID+"\t"+line+"\n")

  ## attach documents
  docID2taxonIDs = defaultdict(list)
  with open(args.doc_assign_in, "r") as fin, open(args.doc_assign_out, "w") as fout:
    for line in fin:
      line = line.strip()
      if line:
        segs = line.split("\t")
        taxonID = taxonName2taxonID[segs[0]]
        doc_ids = segs[1].split(",")
        for doc_id in doc_ids:
          docID2taxonIDs[doc_id].append(taxonID)

    for docID in docID2taxonIDs:
      fout.write(docID+"\t")
      fout.write(",".join(docID2taxonIDs[docID]))
      fout.write("\n")


if __name__ == '__main__':
  # python3 generate_taxon_ids.py -hier_in ../../data/eecs/taxonomies/our-l3.txt -hier_out ../../data/eecs/taxonomies/sample_taxonomy.txt  -doc_assign_in ../../data/eecs/doc_assignments.txt -doc_assign_out ../../data/eecs/doc_assignments-ids.txt
  parser = argparse.ArgumentParser(prog='generate_taxon_ids.py',
                                   description='Obtain a unified id for each taxon in the hierarchy and return each document'
                                               '\'s matched taxonID')
  parser.add_argument('-hier_in', required=True, help='Input path of taxonomy')
  parser.add_argument('-hier_out', required=True, help='Output path of taxonomy')
  parser.add_argument('-doc_assign_in', required=False, help='Input path of documnet assignment file')
  parser.add_argument('-doc_assign_out', required=False, help='Output path of document assignment path, each line is a '
                                                              'document id with a list of attachment TaxonID')
  args = parser.parse_args()

  start = time.time()
  main(args)
  end = time.time()
  print("Finish getting a unified id for each taxon in the hierarchy and "
        "return each document with attached taxonID, using %s seconds" % (end-start))
