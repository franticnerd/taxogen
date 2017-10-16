import json
import preprocessor as p
import os
import subprocess
from paras import la_tweets, la_input, lexnorm, MAIN_LOG
from util.logger import Logger
import re

class TweetHandler:
    def __init__(self, file_in, file_out, logger_name, lexnorm):
        self.input = file_in
        self.output = file_out
        self.lexnorm = lexnorm
        self.lexnorm_dic = self.output + 'lexnorm.txt'
        self.pure_tweets = self.output + 'pure_tweets.txt'
        self.embeddings = self.output + 'embeddings.txt'
        p.set_options(p.OPT.EMOJI, p.OPT.URL, p.OPT.MENTION)
        self.logger = Logger.get_logger(logger_name)
        self.pattern = re.compile("[^a-z0-9\#\s]+")

    def build_lexnorm_dict(self, file_in):
        res = {}
        with open(file_in, 'r') as f:
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_lexnorm_dict.__name__,
                                                      'Reading emnlp_dict.txt'))
            data = f.readlines()
            for line in data:
                line = preprocess_tweet(line)
                line = line.split('\t')
                res[line[0].strip()] = line[1].strip()
            self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_lexnorm_dict.__name__,
                                                      'Finish building lexnorm.txt, write to file'))
        with open(self.lexnorm_dic, 'w+') as f:
            json.dump(res, f)

    def run_word2vec(self):
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.run_word2vec.__name__,
                                                  'Run word2vec on pure_tweets.txt'))
        if not os.path.exists('word2vec'):
            subprocess.call(['gcc ../word2vec.c -o word2vec -lm -pthread -O2 -Wall -funroll-loops -Wno-unused-result'],
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

                count = 0
                for line in f:
                    count += 1
                    tweet_content = line.split('\x01')
                    raw_tweet = tweet_content[7]
                    raw_tweet = preprocess_tweet(raw_tweet)

                    # clean tweet - remove emoji, mention and url
                    clean_tweet = p.clean(raw_tweet)
                    clean_tweet = self.remove_non_alphanumeric(clean_tweet)
                    clean_tweet = clean_tweet

                    tweet_words = clean_tweet.split(' ')
                    for i in range(len(tweet_words)):
                        if tweet_words[i] in self.lexnorm:
                            tweet_words[i] = self.lexnorm[tweet_words[i]]

                    clean_tweet = ' '.join(tweet_words)
                    clean_tweet = clean_tweet.strip(' ')
                    if clean_tweet == '':
                        continue
                    outf.write(clean_tweet + '\n')

                    if count%100000 == 0:
                        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.preprocess.__name__, '%s tweets processed')%count)

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.preprocess.__name__,
                                                  'Embedding tweets'))
        self.run_word2vec()

    def remove_non_alphanumeric(self, tweet):
        """ Only keeps letter, digit and # in tweets, remove all other chars
            :param tweet: a tweet to be cleaned
            :return: cleaned tweet
        """
        return re.sub(self.pattern, '', tweet)


def preprocess_tweet(tweet, lower=True):
    if lower:
        return tweet.replace('\n', '').strip().lower()
    else:
        return tweet.replace('\n', '').strip()


if __name__ == '__main__':
    test = TweetHandler(la_tweets, la_input, MAIN_LOG, lexnorm)
    test.preprocess()
