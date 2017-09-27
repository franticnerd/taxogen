'''
__author__: Jiaming Shen
__description__: A baseline method for extract faceted taxonomy from a global taxonomy
__latest_updates__: 09/27/2017
'''

def main(global_taxonomy, faceted_keyword_list, outputPath, topK=10):
  keywords = set()
  with open(faceted_keyword_list, "r") as fin:
    for line in fin:
      line = line.strip()
      keywords.add(line)

  with open(global_taxonomy, "r") as fin, open(outputPath, "w") as fout:
    for line in fin:
      line = line.strip()
      segs = line.split("\t")
      cluster_name = segs[0]
      phrases = segs[1].split(",")

      cnt = 0
      faceted_keywords = []
      for idx, phrase in enumerate(phrases):
        if phrase in keywords:
          faceted_keywords.append((phrase, idx))
          cnt += 1
          if cnt >= topK:
            break

      fout.write(cluster_name)
      fout.write("\t")
      fout.write(",".join([ele[0]+":"+str(ele[1]) for ele in faceted_keywords]))
      fout.write("\n")


if __name__ == "__main__":
  corpusName = "dblp"
  taxonName = "global_taxonomy"
  facetName = "keywords_application"

  global_taxonomy = "../../data/"+corpusName+"/taxonomies/"+taxonName+".txt"
  faceted_keyword_list = "../../data/"+corpusName+"/facets/"+facetName+".txt"
  outputPath = "../../data/"+corpusName+"/taxonomies/taxonomy_"+facetName+".txt"

  main(global_taxonomy, faceted_keyword_list, outputPath)