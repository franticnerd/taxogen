'''
__author__: Jiaming Shen
__description__: Based on AutoPhrase output, generate 1) papers.txt, 2) keywords.txt
__latest_update__: Auguest 2, 2017
'''
from config import *
from AutoPhraseOutput import AutoPhraseOutput
from SegPhraseOutput import SegPhraseOutput
import re
from pattern.en import parsetree
from pattern.en import parse
from pattern.search import search
from pattern.en import pprint
from textblob import TextBlob
from collections import deque
import time
from collections import Counter
from itertools import groupby
import itertools

def rmTag_concat(line):
    def concat(matched):
        phrase = matched.group()
        phrase = re.sub('<phrase>', '', phrase)
        phrase = re.sub('</phrase>', '', phrase)
        return '_'.join(phrase.split())

    res = re.sub("<phrase>(.*?)</phrase>", concat, line)
    return res

def rmTag_concat_segphrase(line):
    line = re.sub(r"\[", "<phrase>", line)
    line = re.sub(r"\]", "</phrase>", line)
    def concat(matched):
        phrase = matched.group()
        phrase = re.sub('<phrase>', '', phrase)
        phrase = re.sub('</phrase>', '', phrase)
        return '_'.join(phrase.split())

    res = re.sub("<phrase>(.*?)</phrase>", concat, line)
    return res


def main():
    ### Step 1: obtain phrase_to_pos_sequence files
    # segphraseOutput = SegPhraseOutput()
    # cnt = 0
    # with open(RAW_SEGMENTATION, "r") as fin:
    #     for line in fin:
    #         cnt += 1
    #         # if cnt == 100:
    #         #     break
    #         if cnt % 1000 == 0:
    #             print(cnt)
    #         line = line.strip()
    #         segphraseOutput.parse_one_doc(line)

    # print(len(segphraseOutput.phrase_to_pos_sequence))
    # for k in segphraseOutput.phrase_to_pos_sequence:
    #     print(k, segphraseOutput.phrase_to_pos_sequence[k])

    # output_file_path = "../../data/phrase_chunk_info_segphrase.txt"
    # segphraseOutput.save_phrase_to_pos_sequence(output_file_path)


    ### Step 2: Heuristically select NP
    # segphraseOutput = SegPhraseOutput()
    # input_file_path = "../../data/phrase_chunk_info_segphrase.txt"
    # segphraseOutput.load_phrase_to_pos_sequence(input_file_path)
    # segphraseOutput.obtain_pos_sequence_to_score()
    # segphraseOutput.obtain_candidate_phrase(threshold=0.95 , min_sup=10)
    # output_file_path = "../../data/keywords_segphrase.txt"
    # segphraseOutput.save_candidate_phrase(output_file_path)



    cnt = 0
    output_file_path = "../../data/papers_segphrase.txt"
    with open(RAW_SEGMENTATION, "r") as fin, open(output_file_path, "w") as fout:
        for line in fin:
            cnt += 1
            if cnt % 1000 == 0:
                print(cnt)
            line = line.strip()
            line = line.lower()
            fout.write(rmTag_concat_segphrase(line))
            fout.write("\n")

    # output_file_path = "../../data/phrase_chunk_info.txt"
    # autophraseOutput.save_phrase_to_pos_sequence(output_file_path)

    # print(len(autophraseOutput.phrase_to_pos_sequence))
    # for k in autophraseOutput.phrase_to_pos_sequence:
    #     print(k, autophraseOutput.phrase_to_pos_sequence[k])




if __name__ == '__main__':
    main()


