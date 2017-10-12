from paras import la_pos_tweets, la_keywords
from datetime import datetime

class KeywordGenerator:

    def __init__(self, f_in, f_out):
        self.input = f_in
        self.output = f_out
        self.keywords = set()
        self.noun_tag = set(['NN', 'NNS', 'NNP', 'NNPS'])

    def parse_pos_tweet(self, pos_tweet):

        pos_tweet = pos_tweet.split(' ')

        for segment in pos_tweet:
            segment = segment.strip().split('/')

            if segment[2] in self.noun_tag:
                self.keywords.add(segment[0]+"\n")

    def build_keyword(self):

        with open(self.input, 'r') as f:
            data = f.readlines()

            for pos_tweet in data:
                self.parse_pos_tweet(pos_tweet)

        with open(self.output, 'w+') as f:
            f.writelines(self.keywords)

if __name__ == '__main__':
    start = datetime.utcnow()
    gen = KeywordGenerator(la_pos_tweets, la_keywords)
    gen.build_keyword()
    finish = datetime.utcnow()
    exec_time = finish-start
    print exec_time.seconds
    print exec_time.microseconds



