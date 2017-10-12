import subprocess, os
from paras import la_pure_tweets, la_pos_tweets, la_keywords
from datetime import datetime

class KeywordGenerator:

    def __init__(self, pure_tweets, pos_tweets, f_out):
        self.pure_tweets = pure_tweets
        self.pos_tweets = pos_tweets
        self.output = f_out
        self.keywords = set()
        self.noun_tag = {'NN', 'NNS', 'NNP', 'NNPS'}

    def parse_pos_tweet(self, pos_tweet):

        pos_tweet = pos_tweet.split(' ')

        for segment in pos_tweet:
            segment = segment.strip().split('/')

            if segment[2] in self.noun_tag:
                self.keywords.add(segment[0]+"\n")

    def build_keyword(self):

        with open(self.pos_tweets, 'r') as f:
            data = f.readlines()

            for pos_tweet in data:
                self.parse_pos_tweet(pos_tweet)

        with open(self.output, 'w+') as f:
            f.writelines(self.keywords)

    def build_pos_tag_tweets(self):

        if os.path.exists(self.pos_tweets):
            return

        subprocess.call("cd ../../../twitter_nlp", shell=True)
        subprocess.call(['export TWITTER_NLP=./'], shell=True)
        subprocess.call(['python python/ner/extractEntities.py %s -o %s' % (self.pure_tweets, self.pos_tweets)], shell=True)
        subprocess.call("cd ../local-embedding/code/tweet_preprocessing/", shell=True)


if __name__ == '__main__':
    start = datetime.utcnow()
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords)
    gen.build_keyword()
    finish = datetime.utcnow()
    exec_time = finish-start
    print exec_time.seconds
    print exec_time.microseconds



