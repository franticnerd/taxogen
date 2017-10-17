import subprocess, os
from paras import la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG, la_category, la_category_keywords, la_embeddings, la_seed_keywords_dic, la_seed_keywords
from datetime import datetime
from util.logger import Logger
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from tweet_handler import preprocess_tweet
from collections import OrderedDict
import re


class KeywordGenerator:
    def __init__(self, pure_tweets, pos_tweets, f_out, logger_name, category, category_keywords, embeddings, seed_keywords_dic, seed_keywords):
        self.pure_tweets = pure_tweets
        self.pos_tweets = pos_tweets
        self.output = f_out
        self.keywords = set()
        self.noun_tag = {'NN', 'NNS', 'NNP', 'NNPS'}
        self.logger = Logger.get_logger(logger_name)
        self.category = category
        self.category_keywords = category_keywords
        self.embeddings = embeddings
        self.seed_keywords_dic = seed_keywords_dic
        self.seed_keywords = seed_keywords
        self.pattern = re.compile("[^a-zA-Z0-9\s]+")

    def parse_pos_tweet(self, pos_tweet):
        pos_tweet = preprocess_tweet(pos_tweet, lower=False)
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
        p = subprocess.Popen('shell_script/pos_tag.sh %s %s' % (self.pure_tweets, self.pos_tweets), shell=True)
        p.communicate()
        self.logger.info(Logger.build_log_message(self.__class__.__name__, self.build_pos_tag_tweets.__name__,
                                                  'Finish building pos tag tweets'))

    def build_category_keywords(self):
        with open(self.category, 'r') as f:
            data = f.read()
        category_dict = json.loads(data)
        category_dict = category_dict['categories']
        category_keywords = set(self.recursive_build_category_keywords(category_dict))
        with open(self.category_keywords, 'w+') as fout:
            fout.write(' '.join(category_keywords))

    def recursive_build_category_keywords(self, category_dict):
        if len(category_dict) == 0:
            return []

        keywords = []
        for category in category_dict:
            name = preprocess_tweet(category['name']).encode('ascii', 'ignore')
            re.sub(self.pattern, '', name).encode('utf8', 'ignore')
            words = name.split(' ')
            words = [word for word in words if len(word) > 1]
            keywords.extend(words)
            child_keywords = self.recursive_build_category_keywords(category['categories'])
            keywords.extend(child_keywords)
        return keywords

    def match_category_keyword(self):

        with open(self.embeddings, 'r') as f:
            embedding_data = f.readlines()
        with open(self.category_keywords, 'r') as f:
            category_keywords = preprocess_tweet(f.read()).split(' ')
        with open(self.output, 'r') as f:
            keywords = f.readlines()

        embed_dic = {}
        for line in embedding_data[1:]:
            line = preprocess_tweet(line, lower=False)
            line = line.split(' ')
            embed_dic[line[0].strip()] = [float(i) for i in line[1:]]

        category_keywords_embed = OrderedDict()
        for word in category_keywords:
            word = word.lower()
            if word in embed_dic:
                category_keywords_embed[word] = embed_dic[word]

        count = 0
        keywords_embed = OrderedDict()
        for word in keywords:
            word = preprocess_tweet(word)
            count += 1
            if word in embed_dic:
                keywords_embed[word] = embed_dic[word]

            if count % 10000 == 0:
                print "%s keywords processed" % count

        keywords_embed_array = np.asarray(keywords_embed.values())
        category_keywords_array = np.asarray(category_keywords_embed.values())
        result = cosine_similarity(category_keywords_array, keywords_embed_array)

        keywords_embed_keys = keywords_embed.keys()
        category_keywords_embed_keys = category_keywords_embed.keys()

        cosine_cate = {}
        for i in range(len(result)):
            cosine_cate[category_keywords_embed_keys[i]] = {}
            for j in range(len(result[i])):
                if result[i][j] >= 0.55:
                    cosine_cate[category_keywords_embed_keys[i]][keywords_embed_keys[j]] = result[i][j]

        result = []
        for key in cosine_cate:
            cosine_cate[key] = OrderedDict(sorted(cosine_cate[key].items(), key=lambda t: t[1], reverse=True))
            result.extend(cosine_cate[key].keys())
        with open(self.seed_keywords_dic, 'w+') as fout:
            json.dump(cosine_cate, fout, indent=4)

        with open(self.seed_keywords, 'w+') as fout:
            fout.write('\n'.join(result))




if __name__ == '__main__':
    start = datetime.utcnow()
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG, la_category, la_category_keywords, la_embeddings, la_seed_keywords_dic, la_seed_keywords)
    # gen.build_pos_tag_tweets()
    # gen.build_keyword()
    gen.build_category_keywords()
    #gen.match_category_keyword()
    finish = datetime.utcnow()
    exec_time = finish - start
    print exec_time.seconds
    print exec_time.microseconds
