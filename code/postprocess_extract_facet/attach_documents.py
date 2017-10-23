'''
__author__: Jiaming Shen
__description__: Obtain allowed documents for each node in taxonomy
__latest_update__: 10/22/2017
'''
import time
import argparse

def obtain_allowed_doc_ids(taxonName, root):
  filePath = root + taxonName[1:] + "/doc_ids.txt"
  allowed_ids = []
  with open(filePath, "r") as fin:
    for line in fin:
      docID = int(line.strip())
      allowed_ids.append(docID)
  return set(allowed_ids)

def main(args):
  if (not args.N):
    args.N = 10
  else:
    args.N = int(args.N)
  with open(args.input, "r") as fin, open(args.output, "w") as fout:
    for line in fin:
      line = line.strip()
      segs = line.split("\t")
      taxonName = segs[0]
      print("Assign documents to node %s" % taxonName)
      allowed_ids = obtain_allowed_doc_ids(taxonName, args.root)
      fout.write(taxonName)
      fout.write("\t")
      fout.write(",".join([str(id) for id in allowed_ids]))
      fout.write("\n")

if __name__ == '__main__':
  # python3 attach_documents.py -input ../../data/eecs/taxonomies/our-l3.txt -output ../../data/eecs/doc_assignments.txt -root ../../data/eecs/our-l3 -N -1
  parser = argparse.ArgumentParser(prog='attach_documents.py',
                                   description='Obtain top-ranked documents for each node in faceted taxonomy.')
  parser.add_argument('-input', required=True, help='Input path of taxonomy')
  parser.add_argument('-output', required=True, help='Output path of documents')
  parser.add_argument('-root', required=True, help='The root path of taxonomy, no slash in the end')
  parser.add_argument('-N', required=False, help='Number of top ranked documents. -1 means obtain all')
  args = parser.parse_args()

  start = time.time()
  main(args)
  end = time.time()
  print("Finish extracting documents, using %s seconds" % (end-start))
