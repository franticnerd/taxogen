from textblob import TextBlob
import time

def main():
  input_filepath = "/Users/shenjiaming/Desktop/linked_results.wiki.txt"
  output_filepath = "/Users/shenjiaming/Desktop/linked_results.wiki.pos.txt"
  start = time.time()
  np_phrase_cnt = 0
  with open(input_filepath, "r") as fin, open(output_filepath, "w") as fout:
    cnt = 0
    for line in fin:
      cnt += 1
      if cnt % 1000 == 0:
        print(cnt)
      line = line.strip()
      segs = line.split("\t")
      phrase = segs[0]
      score = int(segs[1])
      if score != 0:
        fout.write(line+"\n")
      else: # deal with noun_phrase
        tmp = TextBlob(phrase)
        if len(tmp.noun_phrases) == 0:
          fout.write(line+"\n")
        else:
          np_phrase_cnt += 1
          nps = str("|".join([ele for ele in tmp.noun_phrases]))
          fout.write(phrase+"\t"+"0.5"+"\t"+nps+"\t"+segs[3]+"\n")
  end = time.time()
  print("Number of additional noun phrases: %s" % np_phrase_cnt)
  print("Finish using POS Tagger for NP extraction using %s seconds" % (end-start))

if __name__ == '__main__':
  main()