import json
import heapq
import preprocessor as p
from paras import la_tweets, la_output, lexnorm, lexnorm_dic
from util.dateutil import DateUtil
class TweetHandler:
    def __init__(self, file_in, file_out):
        self.input = file_in
        self.output = file_out
        # self.build_lexnorm_dict(lexnorm, self.output)
        with open(lexnorm_dic) as json_data:
            self.lexnorm = json.load(json_data)
        p.set_options(p.OPT.EMOJI, p.OPT.URL, p.OPT.MENTION)


    def build_lexnorm_dict(self, file_in, file_out):
        res = {}
        with open(file_in, 'r') as f:
            data = f.readlines()
            for line in data:
                line = line.strip().split('\t')
                res[line[0]]=line[1]
        with open(file_out+"/lexnorm.txt", 'w+') as f:
            json.dump(res, f)


    def preprocess(self):
        # key is user id and value is all possible tweets from this user
        with open (self.output+"/pure_tweets.txt", "w+") as outf:
            with open(self.input, 'r') as f:
                for line in f:
                    tweet_content = line.split('\x01')
                    raw_tweet = tweet_content[7]

                    # clean tweet - remove emoji, mention and url
                    clean_tweet = p.clean(raw_tweet)
                    tweet_words = clean_tweet.encode("ascii", "ignore").split(' ')
                    for i in range(len(tweet_words)):
                        if tweet_words[i] in self.lexnorm:
                            tweet_words[i] = self.lexnorm[tweet_words[i]]

                    clean_tweet = " ".join(tweet_words)
                    outf.write(clean_tweet+"\n")

if __name__ == '__main__':
    test = TweetHandler(la_tweets, la_output)
    test.preprocess()

