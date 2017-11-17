import subprocess, os
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

        self.word_word_co_occurrence_2(input_file, train_file, self.logger, self.min_count)
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__,
                                                  'Finish building training file'))

    @staticmethod
    def word_word_co_occurrence_1(input_file, train_file, logger, min_count):
        t1 = time.time()
        with open(input_file, 'r') as f:
            data = f.readlines()
        word_co_occurrence = {}
        # word_co_occurrence_tweets = {}
        count = 0
        for tweet in data:
            tweet = preprocess_tweet(tweet, lower=True)
            stweet = tweet.split(' ')

            for i in range(len(stweet)):
                for j in range(i + 1, len(stweet)):
                    co_w1 = '{}\t{}'.format(stweet[i], stweet[j])
                    co_w2 = '{}\t{}'.format(stweet[j], stweet[i])
                    # co_w = '{}_{}'.format(stweet[i], stweet[j])
                    if co_w1 not in word_co_occurrence:
                        word_co_occurrence[co_w1] = 0
                    if co_w2 not in word_co_occurrence:
                        word_co_occurrence[co_w2] = 0
                    # if co_w not in word_co_occurrence_tweets:
                    #     word_co_occurrence_tweets[co_w] = []

                    word_co_occurrence[co_w1] += 1
                    word_co_occurrence[co_w2] += 1
                    # word_co_occurrence_tweets[co_w].append(tweet)

            count += 1

            if count % 10000 == 0:
                logger.info(Logger.build_log_message("LINE", "word_word_co_occurrence_1",
                                                          '{} lines processed'.format(count)))
        word_co_occurrence = {k: v for k, v in word_co_occurrence.iteritems() if v >= min_count}
        res_list = []
        word_set = set()
        for key, val in word_co_occurrence.iteritems():
            res_list.append('{}\t{}'.format(key, float(val)))
            # res_list.append('{}\t{}\t{}'.format(key, val, 'e'))
            for word in key.split('\t'):
                word_set.add(word)
        with open(train_file, 'w') as outf:
            outf.write('\n'.join(res_list))

            # with open(self.train_nodes, 'wb') as outf:
            #     outf.write('\n'.join(list(word_set)))

            # count = 0
            # for co_word in word_co_occurrence_tweets:
            #     if len(word_co_occurrence_tweets[co_word]) >= self.min_count:
            #         with open(self.co_occurrence_tweets+co_word+".txt", 'w') as outf:
            #             outf.write('\n'.join(word_co_occurrence_tweets[co_word]))
            #         count += 1
            #         if count % 10000 == 0:
            #             self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_train_file.__name__, '{} co_occurrence_words processed'.format(count)))
        t2 = time.time()
        logger.info("word_word_co_occurrence_1 takes {}".format(t2-t1))

    @staticmethod
    def word_word_co_occurrence_2(input_file, train_file, logger, min_count):
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

        with open(fout, 'w') as f:
            json.dump(co_occurrence_dic, f)

if __name__ == '__main__':
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].strip('\n')

    paras = load_la_tweets_paras(dir=git_version)
    line = LINE(paras)
    line.build_train_file()
    line.run()
    #logger = Logger('log.txt')
    #LINE.word_word_co_occurrence_1("pure_tweets.txt", 'train_edges.txt', logger, 10)