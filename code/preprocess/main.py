'''
__author__: Jiaming Shen
__description__: Based on AutoPhrase output, generate 1) papers.txt, 2) keywords.txt
__latest_update__: Auguest 2, 2017
'''
from config import *
# from AutoPhraseOutput import AutoPhraseOutput
from SegPhraseOutput import SegPhraseOutput
import re
# from pattern.en import parsetree
# from pattern.en import parse
# from pattern.search import search
# from pattern.en import pprint
# from textblob import TextBlob
# from collections import deque
# import time
# from collections import Counter
# from itertools import groupby
# import itertools

def rmTag_concat(line):
    def concat(matched):
        phrase = matched.group()
        phrase = re.sub('<phrase>', '', phrase)
        phrase = re.sub('</phrase>', '', phrase)
        return '_'.join(phrase.split())

    res = re.sub("<phrase>(.*?)</phrase>", concat, line)
    return res

def rmTag_concat_segphrase(line, no_hypen = False, remove_noise=False):
    line = re.sub(r"\[", "<phrase>", line)
    line = re.sub(r"\]", "</phrase>", line)

    if remove_noise:
        line = re.sub(r'[^\x00-\x7F]+', ' ', line)
        ## add space before and after special characters
        line = re.sub(r"([.,!:?()])", r" \1 ", line)
        ## replace multiple continuous whitespace with a single one
        line = re.sub(r"\s{2,}", " ", line)

    def concat(matched):
        phrase = matched.group()
        phrase = re.sub('<phrase>', '', phrase)
        phrase = re.sub('</phrase>', '', phrase)
        if no_hypen: # remove hypen in matched keywords
            phrase = re.sub('-', '_', phrase)
        return '_'.join(phrase.split())

    res = re.sub("<phrase>(.*?)</phrase>", concat, line)


    return res


def main():
    ### Step 1: obtain phrase_to_pos_sequence files
    # segphraseOutput = SegPhraseOutput()
    # inputPath = "/Users/shenjiaming/Desktop/linked_results.wiki.pos.txt"
    # outputPath = "/Users/shenjiaming/Desktop/keywords.txt"
    # segphraseOutput.obtain_candidate_phrase_wiki(inputPath, outputPath)



    # cnt = 0
    # start = time.time()
    # with open(RAW_SEGMENTATION, "r") as fin:
    #     for line in fin:
    #         cnt += 1
    #         # if cnt == 100:
    #         #     break
    #         if cnt % 1000 == 0:
    #             print(cnt)
    #         line = line.strip()
    #         segphraseOutput.parse_one_doc(line)
    # end = time.time()
    #
    # print(len(segphraseOutput.phrase_to_pos_sequence))
    # for k in segphraseOutput.phrase_to_pos_sequence:
    #     print(k, segphraseOutput.phrase_to_pos_sequence[k])
    #
    # output_file_path = "../../data/phrase_chunk_info_segphrase_w_unigram.txt"
    # segphraseOutput.save_phrase_to_pos_sequence(output_file_path)
    # print("[INFO] Using time = ", (end - start))

    ### Step 2: Heuristically select NP
    # segphraseOutput = SegPhraseOutput()
    # input_file_path = "../../data/phrase_chunk_info_segphrase_w_unigram.txt"
    # segphraseOutput.load_phrase_to_pos_sequence(input_file_path)
    # segphraseOutput.obtain_pos_sequence_to_score()
    # segphraseOutput.obtain_candidate_phrase(threshold=0.95 , min_sup=10)
    # output_file_path = "../../data/keywords_segphrase_w_unigram.txt"
    # segphraseOutput.save_candidate_phrase(output_file_path)


    ### Step 3: lower case seged output
    cnt = 0
    input_file_path = "/shared/data/jiaming/semantic_scholar/cs/parsed_semantic_scholar_docs.txt"
    output_file_path = "/shared/data/jiaming/semantic_scholar/cs/papers.txt"
    with open(input_file_path, "r") as fin, open(output_file_path, "w") as fout:
        for line in fin:
            cnt += 1
            if cnt % 10000 == 0:
                print(cnt)
            line = line.strip()
            line = line.lower()
            fout.write(rmTag_concat_segphrase(line, no_hypen=True, remove_noise=True))
            fout.write("\n")


    # output_file_path = "../../data/phrase_chunk_info.txt"
    # autophraseOutput.save_phrase_to_pos_sequence(output_file_path)

    # print(len(autophraseOutput.phrase_to_pos_sequence))
    # for k in autophraseOutput.phrase_to_pos_sequence:
    #     print(k, autophraseOutput.phrase_to_pos_sequence[k])

    ## Additional steps (deal with hypen)
    # intput_keyword_path = "/shared/data/jiaming/semantic_scholar/cs/salient.csv"
    # output_keyword_path = "/shared/data/jiaming/semantic_scholar/cs/keywords.txt"
    # keyword2score = {}
    # with open(intput_keyword_path, "r") as fin:
    #     for line in fin:
    #         line = line.strip()
    #         segs = line.split(",")
    #         phrase = re.sub(r"-","_", segs[0])
    #         score = float(segs[1])
    #         if score >= 0.75:
    #           keyword2score[phrase] = score
    #         else:
    #           break
    # print("Number of deduplicated keywords = ", len(keyword2score))
    # with open(output_keyword_path, "w") as fout:
    #     for ele in sorted(keyword2score.items(), key = lambda x:-x[1]):
    #         fout.write(ele[0])
    #         fout.write("\t")
    #         fout.write(str(ele[1]))
    #         fout.write("\n")






if __name__ == '__main__':
    main()

