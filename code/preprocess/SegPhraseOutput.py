'''
__author__: Jiaming Shen
__description__: Parse SegPhrase output
'''
import re
import itertools
from collections import deque
# from pattern.en import parse

class SegPhraseOutput(object):
    def __init__(self, input_path=None):
        self.input_path = input_path
        self.phrase_to_pos_sequence = {} # key: lower case phrase, value: a dict of {"pos_sequence": count}
        self.pos_sequence_to_score = {} # key: a pos sequence, value: a score in [0,0, 1.0]
        self.candidate_phrase = []

    def parse_one_doc(self, doc):
        ''' Parse each doc and update the phrase_to_pos_sequence

        :param doc:
        :return:
        '''
        ## replace non-ascii character
        doc = re.sub(r'[^\x00-\x7F]+', ' ', doc)
        ## add space before and after <phrase> tags
        doc = re.sub(r"\[", " <phrase> ", doc)
        doc = re.sub(r"\]", " </phrase> ", doc)
        ## add space before and after special characters
        doc = re.sub(r"([.,!:?()])", r" \1 ", doc)
        ## replace multiple continuous whitespace with a single one
        doc = re.sub(r"\s{2,}", " ", doc)

        tmp = parse(doc, relations=False, lemmata=False).split()
        token_info = itertools.chain(*tmp)

        IN_PHRASE_FLAG = False
        q = deque()
        for token in token_info:
            word = str(token[0])
            tag = str(token[1])
            chunk = str(token[2])
            if word == "<phrase>": # the start of a phrase
                IN_PHRASE_FLAG = True
            elif word == "</phrase>": # the end of a phrase
                ## obtain the information of current phrase
                current_phrase_list = []
                while (len(q) != 0):
                    current_phrase_list.append(q.popleft())
                phrase = " ".join([ele[0] for ele in current_phrase_list])
                phrase = phrase.lower() # convert to lower case
                chunk_sequence = " ".join([ele[2] for ele in current_phrase_list])

                ## update phrase information
                if phrase not in self.phrase_to_pos_sequence:
                    self.phrase_to_pos_sequence[phrase] = {}

                if chunk_sequence not in self.phrase_to_pos_sequence[phrase]:
                    self.phrase_to_pos_sequence[phrase][chunk_sequence] = 1
                else:
                    self.phrase_to_pos_sequence[phrase][chunk_sequence] += 1

                IN_PHRASE_FLAG = False
            else:
                if IN_PHRASE_FLAG: # in phrase, push the (word, tag, chunk) triplet
                    q.append((word, tag, chunk))

        # sanity checking
        if (len(q) != 0):
            print("[ERROR]: mismatched </phrase> in document: %s" % doc)

    def save_phrase_to_pos_sequence(self, output_path=""):
        with open(output_path, "w") as fout:
            for phrase in self.phrase_to_pos_sequence:
                fout.write(phrase)
                fout.write("\t")
                fout.write(str(self.phrase_to_pos_sequence[phrase]))
                fout.write("\n")

    def load_phrase_to_pos_sequence(self, input_path=""):
        with open(input_path, "r") as fin:
            for line in fin:
                line = line.strip()
                seg = line.split("\t")
                phrase = seg[0]
                pos_sequence = eval(seg[1])
                self.phrase_to_pos_sequence[phrase] = pos_sequence
        print("[INFO] Number of phrases before NP pruning = ", len(self.phrase_to_pos_sequence))

    def obtain_pos_sequence_to_score(self):
        pos_sequence_2_score = {}
        for v in self.phrase_to_pos_sequence.values():
            for pos_sequence in v:
                if pos_sequence not in pos_sequence_2_score:
                    pos_sequence_list = pos_sequence.split()
                    ## Rule 1: if "O" is in the NP Chunk sequence, this sequence has score 0
                    if "O" in pos_sequence_list:
                        pos_sequence_2_score[pos_sequence] = 0.0
                    else:
                        ## Rule 2: the score of a pos tag sequence is the portion of NP in sequence
                        phrase_tags = [ele.split("-")[1] for ele in pos_sequence_list]
                        score = float(phrase_tags.count("NP")) / len(phrase_tags)
                        pos_sequence_2_score[pos_sequence] = score
        self.pos_sequence_to_score = pos_sequence_2_score


        print(len(self.pos_sequence_to_score))
        print(self.pos_sequence_to_score)

    def obtain_candidate_phrase(self, threshold = 0.8, min_sup = 5):
        candidate_phrase = []
        for phrase in self.phrase_to_pos_sequence:
            phrase_score = 0
            freq = sum(self.phrase_to_pos_sequence[phrase].values())
            if freq < min_sup:
                continue
            for pos_sequence in self.phrase_to_pos_sequence[phrase].keys():
                pos_sequence_weight = float(self.phrase_to_pos_sequence[phrase][pos_sequence]) / freq
                pos_sequence_score = self.pos_sequence_to_score[pos_sequence]
                phrase_score += (pos_sequence_weight * pos_sequence_score)
            if phrase_score >= threshold:
                # print(phrase, phrase_score)
                candidate_phrase.append(phrase)
        print(len(candidate_phrase))
        print(candidate_phrase[0:10])
        self.candidate_phrase = candidate_phrase

    def save_candidate_phrase(self, output_path=""):
        with open(output_path, "w") as fout:
            for phrase in self.candidate_phrase:
                fout.write("_".join(phrase.split()))
                fout.write("\n")

    def obtain_candidate_phrase_wiki(self, inputFile, outputFile):
        with open(inputFile, "r") as fin, open(outputFile, "w") as fout:
            for line in fin:
              line = line.strip()
              segs = line.split("\t")
              phrase = "_".join(segs[0].split())
              try:
                score = int(segs[1])
              except:
                print(line)
              if score != 0:
                fout.write(phrase+"\n")