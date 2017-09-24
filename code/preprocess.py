'''
__author__: Chao Zhang
__description__: Construct inverted index from input corpus and keyword list
__latest_updates__: 09/24/2017
'''
from os import listdir
from os.path import isfile, join

def get_candidates(folder, o_file):
  files = ['%s%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f))]
  quality_phrases = set()

  for file in files:
    with open(file) as f:
      for line in f:
        phrase = line.split(' ')[0]
        quality_phrases.add(phrase)

  print('Quality phrase count: ' + str(len(quality_phrases)))

  with open(o_file, 'w+') as g:
    for phrase in quality_phrases:
      g.write('%s\n' % phrase)


def get_reidx_file(text, cand_f, o_file):
  '''
  :param text: input corpus (papers.txt)
  :param cand_f: candidate phrase (keywords.txt)
  :param o_file: output inverted index file (index.txt)
  :return: 
  '''

  candidates = []
  with open(cand_f) as f:
    for line in f:
      candidates.append(line.strip('\r\n'))

  pd_map = {x:set() for x in candidates}
  candidates_set = set(candidates)

  with open(text) as f:
    idx = 0
    for line in f:
      tokens = line.strip('\r\n').split(' ')
      for t in tokens:
        if t in candidates_set:
          pd_map[t].add(str(idx))
      idx += 1
      if idx % 10000 == 0:
        print("[Construct Inverted Index] Parse %s documents" % idx)

  with open(o_file, 'w+') as g:
    for ph in pd_map:
      if len(pd_map[ph]) > 0:
        doc_str = ','.join(pd_map[ph])
      else:
        doc_str = ''
      g.write('%s\t%s\n' % (ph, doc_str))


# Generate inverted index
# get_reidx_file('../data/paper_phrases.txt.frequent.hardcode', '../data/candidates.txt', '../data/reidx.txt')
# get_reidx_file('../data/toy/input/papers.txt', '../data/toy/input/keywords.txt', '../data/toy/input/index.txt')
# get_reidx_file('../data/dblp/input/papers.txt', '../data/dblp/input/keywords.txt', '../data/dblp/input/index.txt')
# get_reidx_file('../data/sp/input/papers.txt', '../data/sp/input/keywords.txt', '../data/sp/input/index.txt')
get_reidx_file('../data/dblp/input/papers.txt', '../data/dblp/input/keywords_method.txt', '../data/dblp/input/index_method.txt')
exit(1)

folder = '../data/leef/query_relevant/'
o_file = '../data/candidates.txt'

get_candidates(folder, o_file)


