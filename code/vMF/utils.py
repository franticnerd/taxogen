'''
__author__: Jiaming Shen
__description__: utility functions of rejection-vMF clustering
__latest_updates__: 10/21/2017
'''
import numpy as np
def extract_keyword_embeddings_from_all_embeddings(f_keyword,f_embeddings, f_out_embeddings):
  ''' Extract the embeddings for interested keywords from a global embedding files

  :param f_keyword:
  :param f_embeddings:
  :param f_out_embeddings:
  :return:
  '''

  keywords = []
  with open(f_keyword, "r") as fin:
    for line in fin:
      line = line.strip()
      if line:
        keywords.append(line.strip())
  print("Finish loading %s keyword" % len(keywords))

  keyword2embedding = {}
  with open(f_embeddings, 'r') as fin:
    header = fin.readline() # skip the header line
    for line in fin:
      items = line.strip().split()
      word = items[0]
      vec = [float(v) for v in items[1:]]
      keyword2embedding[word] = vec
  print("Finish loading full embedding")

  with open(f_out_embeddings, "w") as fout:
    for keyword in keywords:
      if keyword in keyword2embedding:
        fout.write(keyword+"\t")
        fout.write(str(keyword2embedding[keyword]))
        fout.write("\n")
      else:
        print("[Error] keyword %s does not have embedding")

def load_keyword_embeddings(f_embeddings):
  keyword2id = {}
  id2keyword = {}
  cnt = 0
  ret = []
  with open(f_embeddings, "r") as fin:
    for line in fin:
      line = line.strip()
      if line:
        segs = line.split("\t")
        keyword = segs[0]
        keyword2id[keyword] = cnt
        id2keyword[cnt] = keyword
        cnt += 1

        vec = np.array(eval(segs[1]))
        ret.append(vec)
  embeddings = np.array(ret)
  print("[INFO] Finish loading keyword embeddings")

  return keyword2id, id2keyword, embeddings



if __name__ == '__main__':
  # '''Function 1: Extract keyword embeddings from a global embedding file'''
  # f_keyword = "../../data/eecs/raw/keywords.txt"
  # f_embeddings = "../../data/eecs/input/embeddings.txt"
  # f_out_embeddings = "../../data/eecs/keyword_embeddings.txt"
  # extract_keyword_embeddings_from_all_embeddings(f_keyword, f_embeddings, f_out_embeddings)

  '''Function 2: load keyword'''
  f_embeddings = "../../data/eecs/keyword_embeddings.txt"
  keyword2id, id2keyword, embeddings = load_keyword_embeddings(f_embeddings)
  print(embeddings.shape)

