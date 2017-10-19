import json
import preprocessor as p
import os
import subprocess
import paras
from util.logger import Logger
import re

class TweetHandler:
    def __init__(self, paras, logger_name, lexnorm):
        self.input = paras['tweets']
        self.output = paras['raw']
        self.lexnorm = lexnorm
        self.lexnorm_dic = paras['lexnorm_dic']
        self.pure_tweets = paras['pure_tweets']
        self.embeddings = paras['embeddings']
        self.hashtags = paras['hashtags']
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
                    outf.write('{0}\n'.format(clean_tweet))

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

    def build_hashtags(self):
        with open(self.pure_tweets, 'r') as f:
            data = f.readlines()
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_hashtags.__name__,
                                                      'Build hashtags'))
        hashtag_dic = {}
        for line in data:
            line = preprocess_tweet(line, lower=False)
            line = line.split(' ')
            for word in line:
                if word.startswith('#'):
                    if word.count('#') == 1:
                        self.add_hashtag_to_dic(hashtag_dic, word)
                    else:
                        tags = word[1:].split('#')
                        for tag in tags:
                            self.add_hashtag_to_dic(hashtag_dic, '#'+tag)

        with open(self.hashtags, 'w') as outf:
            for key in hashtag_dic:
                if hashtag_dic[key] >= 10:
                    outf.write('{0}\n'.format(key))

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_hashtags.__name__,
                                                  'Finish building hashtags'))

    def add_hashtag_to_dic(self, dic, hastag):
        if hastag not in dic:
            dic[hastag] = 0
        dic[hastag] += 1

def preprocess_tweet(tweet, lower=True):
    if lower:
        return tweet.replace('\n', '').strip().lower()
    else:
        return tweet.replace('\n', '').strip()


if __name__ == '__main__':
    la_paras = paras.load_la_tweets_paras()
    test = TweetHandler(la_paras, paras.MAIN_LOG, paras.lexnorm)
    #test.preprocess()
    test.build_hashtags()