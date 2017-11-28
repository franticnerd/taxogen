import subprocess, os

import sys
from sklearn.feature_extraction.text import CountVectorizer
import time
import json
from ..tweet_preprocessing.tweet_handler import preprocess_tweet
from ..tweet_preprocessing.tweet_handler import Logger
from ..tweet_preprocessing.paras import load_la_tweets_paras


class LINE:
    def __init__(self, paras):
        self.input = paras['graph_embedding_tweets']
        self.train_edges = paras['train_edges']
        self.output = paras['embeddings']
        self.size = paras['line_paras']['size']
        self.order = paras['line_paras']['order']
        self.negative = paras['line_paras']['negative']
        self.samples = paras['line_paras']['samples']
        self.rho = paras['line_paras']['rho']
        self.threads = paras['line_paras']['thread']
        self.logger = Logger.get_logger("MAIN LOG")
        self.min_count = paras['line_paras']['min_count']
        self.co_occurrence_tweets = paras['co_occurrence_tweets']

    def build_train_file(self, input_file=None, train_file=None):

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__,
                                                  'Start building training file'))

        if input_file == None:
            input_file = self.input
        if train_file == None:
            train_file = self.train_edges

        self.word_word_co_occurrence(input_file, train_file, self.logger, self.min_count)
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__,
                                                  'Finish building training file'))

    @staticmethod
    def word_word_co_occurrence(input_file, train_file, logger, min_count):
        t1 = time.time()
        with open(input_file, 'r') as f:
            data = f.readlines()

        count_vec = CountVectorizer(decode_error='ignore', analyzer='word')
        x = count_vec.fit_transform(data)
        features = count_vec.get_feature_names()
        xc = x.T * x
        xc.setdiag(0)
        xc = xc.tocoo()
        result = []
        for i, j, v in zip(xc.row, xc.col, xc.data):
            if v >= min_count:
                result.append('{}\t{}\t{}'.format(features[i], features[j], v))
        with open(train_file, 'w') as outf:
            outf.write('\n'.join(result))
        t2 = time.time()

        logger.info("word_word_co_occurrence_2 takes {}".format(t2-t1))



    def run(self, train_file=None, output_file=None):
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run.__name__,
                                                  'Start graph embedding training'))

        if train_file == None:
            train_file = self.train_edges
        if output_file == None:
            output_file = self.output

        if not os.path.exists('line'):
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run.__name__,
                                                      'Please download LINE package and put the executable under the current path.'))
        else:
            subprocess.call(
                ['./line', '-train', train_file, '-output', output_file, '-size', self.size, '-order', self.order,
                 '-negative', self.negative, '-samples', self.samples, '-rho', self.rho, '-threads', self.threads])

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run.__name__,
                                                  'Finish graph embedding training'))

    @staticmethod
    def build_co_occurrence_dic(fin, fout):
        with open(fin, 'r') as f:
            data = f.readlines()

        co_occurrence_dic = {}
        curr_word = None
        for line in data:
            line = line.split('\t')
            if curr_word == None or curr_word != line[1]:
                curr_word = line[1]
                co_occurrence_dic[curr_word] = 0

            co_occurrence_dic[curr_word] += 1

        # co_occurrence_dic = sorted(co_occurrence_dic.items(), key=lambda t: t[1], reverse=True)
        with open(fout, 'w') as f:
            json.dump(co_occurrence_dic, f)

if __name__ == '__main__':
    #git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].strip('\n')

    #paras = load_la_tweets_paras(dir=git_version)
    #line = LINE(paras)
    #line.build_train_file()

    #line.run()
    #logger = Logger('log.txt')
    #LINE.word_word_co_occurrence_1("pure_tweets.txt", 'train_edges.txt', logger, 10)

    if(len(sys.argv) < 3):
        print "python -m code.graph_embedding.graph_embedding fin fout"

    fin = sys.argv[1]
    fout = sys.argv[2]

    print fin
    print fout

    LINE.build_co_occurrence_dic(fin, fout)