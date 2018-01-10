'''
__author__: Jiaming Shen
__description__: use wikipedia to determine the noun phrases
__latest_updates__: 10/19/2017
'''
import wikipedia
import re
import sys
import time
import math
import multiprocessing as mp
from collections import Counter

class WikiLinker:
  """A class for Wikipedia"""
  _version = 0.2

  def __init__(self):
    None

  def save_to_file(self, res, phrases2score=None, filepath="./results.txt"):
    with open(filepath, "w") as fout:
      if phrases2score:
        for ele in sorted(phrases2score.items(), key = lambda x:-x[1]):
          phrase = ele[0]
          fout.write(phrase + "\t")
          link_res = res[phrase]
          fout.write(str(link_res[0]) + "\t" + link_res[1] + "\t")
          fout.write(str(ele[1])) # add phrase score to the last column
          fout.write("\n")
      else:
        for phrase in res:
          fout.write(phrase+"\t")
          link_res = res[phrase]
          fout.write(str(link_res[0])+"\t"+link_res[1])
          fout.write("\n")

  def get_wiki_online(self, phrase):
    try:
      m = wikipedia.page(title = phrase, pageid=None, auto_suggest=False, redirect=True, preload=False)
      print("[{}]Directly linking phrase: {}".format(mp.current_process().name, phrase, ))
      return (3, m.original_title)
    except:
      try:
        m2 = wikipedia.page(title = phrase, pageid=None, auto_suggest=True, redirect=True, preload=False)
        print("[{}]Indirectly linking phrase: {}".format(mp.current_process().name, phrase, ))
        return (2, m2.original_title)
      except wikipedia.exceptions.DisambiguationError as e:
        options = e.options
        print("[{}]Indirectly linking phrase with ambiguity: {}".format(mp.current_process().name, phrase, ))
        return (1, re.sub("\n"," ", "|".join(options))) # some options has "\n" in text ...
      except:
        print("[{}]Unlinkable phrase: {}".format(mp.current_process().name, phrase, ))
        return (0, "")

  def get_wiki_batch(self, phrases, save=False):
    if phrases is None:
      return {}

    res = {}
    for e in phrases:
      link_res = self.get_wiki_online(e)
      res[e] = link_res

    return res


  def get_wiki_parallel(self, phrases, phrases2score, num_workers = 1, save = False):
    num_workers += 1
    pool = mp.Pool(processes=num_workers)

    num_lines = len(phrases)
    batch_size = math.floor(num_lines/(num_workers-1))
    print("batch_size: %d" % batch_size)

    start_pos = [i * batch_size for i in range(0, num_workers)]
    results = [pool.apply_async(self.get_wiki_batch, args=(phrases[start:start + batch_size], False)) for i, start in
               enumerate(start_pos)]
    results = [p.get() for p in results]

    res = {}
    for r in results:
      res.update(r)

    ## simple analysis
    for ele in Counter([ele[0] for ele in res.values()]).items():
      print(ele)

    if (save):
      self.save_to_file(res, phrases2score, "linked_results.wiki.txt")

def get_phrases(phrase_file, sep="\t", first_nrow=0):
  phrases = []
  phrases2score = {}
  cnt = 0
  with open(phrase_file, "r") as fin:
    for line in fin:
      cnt += 1
      s = line.strip().split(sep)
      phrase = re.sub(r"_"," ", s[0])
      phrases.append(phrase)
      phrases2score[phrase] = float(s[1])
      if first_nrow != 0 and cnt > first_nrow:
        break

  print('Done: get_phrases')
  return phrases, phrases2score

def main():
  # filepath = "/shared/data/jiaming/semantic_scholar/cs/keywords.txt"
  filepath = "/shared/data/jiaming/local-embedding/SegPhrase/results/salient.csv"
  phrases, phrases2score = get_phrases(filepath, sep=",", first_nrow=0)
  print("Number of phrases")

  w = WikiLinker()
  start = time.time()
  w.get_wiki_parallel(phrases, phrases2score, num_workers=30, save=True)
  end = time.time()
  print("Linking %s phrases using time %s (seconds)" % (len(phrases), end - start))

if __name__ == '__main__':
  main()

