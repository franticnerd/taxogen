import subprocess, os
from paras import la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG
from datetime import datetime
from util.logger import Logger


class KeywordGenerator:
    def __init__(self, pure_tweets, pos_tweets, f_out, logger_name):
        self.pure_tweets = pure_tweets
        self.pos_tweets = pos_tweets
        self.output = f_out
        self.keywords = set()
        self.noun_tag = {'NN', 'NNS', 'NNP', 'NNPS'}
        self.logger = Logger.get_logger(MAIN_LOG)

    def parse_pos_tweet(self, pos_tweet):

        pos_tweet = pos_tweet.split(' ')

        for segment in pos_tweet:
            segment = segment.strip().split('/')

            if segment[2] in self.noun_tag:
                self.keywords.add(segment[0] + "\n")

    def build_keyword(self):

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Start building keywords'))

        with open(self.pos_tweets, 'r') as f:
            data = f.readlines()
            count = 0
            for pos_tweet in data:
                self.parse_pos_tweet(pos_tweet)
                count += 1

                if count % 10000 == 0:
                    self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__,
                                                              '%s pos tag tweets processed' % count))

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Write keywords to file'))

        with open(self.output, 'w+') as f:
            f.writelines(self.keywords)

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Finish building keywords'))

    def build_pos_tag_tweets(self):

        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_pos_tag_tweets.__name__,
                                                  'Start building pos tag tweets'))

        subprocess.Popen('python python/ner/extractEntities.py %s -o %s' % (self.pure_tweets, self.pos_tweets), shell=True)


        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_pos_tag_tweets.__name__,
                                                  'Finish building pos tag tweets'))


if __name__ == '__main__':
    start = datetime.utcnow()
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG)
    gen.build_pos_tag_tweets()
    gen.build_keyword()
    finish = datetime.utcnow()
    exec_time = finish - start
    print exec_time.seconds
    print exec_time.microseconds
