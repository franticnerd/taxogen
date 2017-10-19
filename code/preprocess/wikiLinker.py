'''
__author__: Jiaming Shen
__description__: use wikipedia to determine the noun phrases
__latest_updates__: 10/18/2017
'''
import wikipedia
import re
import sys
import time
import math
import multiprocessing as mp

class WikiLinker:
  """A class for Wikipedia"""
  _version = 1.0

  def __init__(self):
    None

  def save_to_file(self, res, filepath):
    with open(filepath, "w") as fout:
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
        return (1, "|".join(options))
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


  def get_wiki_parallel(self, phrases, num_workers = 1, save = False):
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

    if (save):
      self.save_to_file(res, "linked_results.wiki.txt")

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
  filepath = "../../data/semantic_scholar/keywords_segphrase_no_hypen.txt"
  phrases, phrases2score = get_phrases(filepath, sep="\t", first_nrow=0)
  print("Number of phrases")

  w = WikiLinker()
  start = time.time()
  w.get_wiki_parallel(phrases, num_workers=30, save=True)
  end = time.time()
  print("Linking %s phrases using time %s (seconds)" % (len(phrases), end - start))

if __name__ == '__main__':
  main()

