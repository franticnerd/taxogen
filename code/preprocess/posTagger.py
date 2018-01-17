from textblob import TextBlob
import time
import math

def main():
  input_filepath = "/Users/shenjiaming/Desktop/local-embedding/SegPhrase/small/linked_results.wiki.txt"
  output_filepath = "/Users/shenjiaming/Desktop/local-embedding/SegPhrase/small/linked_results.wiki.pos.tsv"
  start = time.time()
  np_phrase_cnt = 0
  phrase_only = True
  with open(input_filepath, "r") as fin, open(output_filepath, "w") as fout:
    cnt = 0
    fout.write("\t".join(["Phrase", "Combined Score", "Phrase Quality Score", "Wiki Linking Score",
                          "NP Count Score", "\n" ]))
    for line in fin:
      cnt += 1
      if cnt % 1000 == 0:
        print(cnt)
      line = line.strip()
      segs = line.split("\t")
      phrase = segs[0]
      phrase_quality_score = float(segs[-1])
      wiki_score = int(segs[1])
      np_cnt_score = len(TextBlob(phrase).noun_phrases)

      combined_score = math.sqrt(phrase_quality_score * (wiki_score+1) * (np_cnt_score+1))
      fout.write("\t".join(["_".join(phrase.split()), str(combined_score), str(phrase_quality_score),
                            str(wiki_score), str(np_cnt_score), "\n"]))





      #
      #
      # if score > 0 and phrase_quality_score >= 0.5:
      #   if phrase_only:
      #     fout.write("_".join(phrase.split()) + "\n")
      #   else:
      #     fout.write("_".join(phrase.split()) + "\t" + str(score) + "\t" + str(phrase_quality_score) + "\n")
      #
      #
      # if score != 0:
      #   fout.write(line+"\n")
      # else: # deal with noun_phrase
      #   tmp = TextBlob(phrase)
      #   if len(tmp.noun_phrases) == 0:
      #     fout.write(line+"\n") # still zero
      #   else:
      #     np_phrase_cnt += 1
      #     nps = str("|".join([ele for ele in tmp.noun_phrases]))
      #     fout.write(phrase+"\t"+"0.5"+"\t"+nps+"\t"+segs[-1]+"\n")

  end = time.time()
  print("Number of additional noun phrases: %s" % np_phrase_cnt)
  print("Finish using POS Tagger for NP extraction using %s seconds" % (end-start))

if __name__ == '__main__':
  main()