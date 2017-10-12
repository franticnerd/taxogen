import json
import preprocessor as p
import os
import subprocess
from paras import la_tweets, la_input, lexnorm, la_log
from util.logger import Logger
class TweetHandler:
    def __init__(self, file_in, file_out, logging_file, lexnorm):
        self.input = file_in
        self.output = file_out
        self.lexnorm = lexnorm
        self.lexnorm_dic = self.output + 'lexnorm.txt'
        self.pure_tweets = self.output + 'pure_tweets.txt'
        self.embeddings = self.output + 'embeddings.txt'
        p.set_options(p.OPT.EMOJI, p.OPT.URL, p.OPT.MENTION)
        self.logging_file = logging_file
        self.logger = Logger(self.logging_file).get_logger()

    def build_lexnorm_dict(self, file_in):
        res = {}
        with open(file_in, 'r') as f:
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_lexnorm_dict.__name__,
                                                      'Reading emnlp_dict.txt'))
            data = f.readlines()
            for line in data:
                line = line.strip().split('\t')
                res[line[0]] = line[1]
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_lexnorm_dict.__name__,
                                                      'Finish building lexnorm.txt, write to file'))
        with open(self.lexnorm_dic, 'w+') as f:
            json.dump(res, f)

    def run_word2vec(self):
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run_word2vec.__name__,
                                                  'Run word2vec on pure_tweets.txt'))
        if not os.path.exists('word2vec'):
            subprocess.call(['gcc word2vec.c -o word2vec -lm -pthread -O2 -Wall -funroll-loops -Wno-unused-result'],
                            shell=True)

        subprocess.call(["./word2vec", "-threads", "20", "-train", self.pure_tweets, "-output", self.embeddings])
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run_word2vec.__name__,
                                                  'Finish word2vec, embeddings.txt generated'))
    def preprocess(self):

        if not os.path.exists(self.lexnorm_dic):
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.preprocess.__name__,
                                                  'Start building lexnorm'))
            self.build_lexnorm_dict(self.lexnorm)

        with open(self.lexnorm_dic) as json_data:
            self.lexnorm = json.load(json_data)

        # key is user id and value is all possible tweets from this user
        with open(self.pure_tweets, 'w+') as outf:
            with open(self.input, 'r') as f:
                self.logger.info(Logger.build_log_message(self.__class__.__name__, self.preprocess.__name__,
                                                          'Preprocess tweets'))
                for line in f:
                    tweet_content = line.split('\x01')
                    raw_tweet = tweet_content[7]

                    # clean tweet - remove emoji, mention and url
                    clean_tweet = p.clean(raw_tweet)
                    tweet_words = clean_tweet.encode('ascii', 'ignore').split(' ')
                    for i in range(len(tweet_words)):
                        if tweet_words[i] in self.lexnorm:
                            tweet_words[i] = self.lexnorm[tweet_words[i]]

                    clean_tweet = ' '.join(tweet_words)
                    outf.write(clean_tweet + '\n')
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.preprocess.__name__,
                                                  'Embedding tweets'))
        self.run_word2vec()

if __name__ == '__main__':
    test = TweetHandler(la_tweets, la_input, la_log, lexnorm)
    test.preprocess()
