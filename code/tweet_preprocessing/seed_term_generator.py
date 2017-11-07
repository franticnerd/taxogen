import subprocess, os
import paras
from datetime import datetime
from util.logger import Logger
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
from tweet_handler import preprocess_tweet
from collections import OrderedDict
import re


class SeedTermGenerator:
    def __init__(self, paras, logger_name):
        self.pure_tweets = paras['pure_tweets']
        self.pos_tweets = paras['pos_tweets']
        self.output = paras['keywords']
        self.keywords = set()
        self.noun_tag = {'NN', 'NNS', 'NNP', 'NNPS'}
        self.logger = Logger.get_logger(logger_name)
        self.category = paras['category']
        self.category_keywords = paras['category_keywords']
        self.embeddings = paras['embeddings']
        self.seed_keywords_dic = paras['seed_keywords_dic']
        self.seed_keywords = paras['seed_keywords']
        self.hashtags = paras['hashtags']
        self.phrases = paras['phrases']
        self.graph_embedding_tweets = paras['graph_embedding_tweets']
        self.pattern = re.compile("[^a-zA-Z0-9\s]+")

    def parse_pos_tweet(self, pos_tweet):
        pos_tweet = preprocess_tweet(pos_tweet, lower=False)
        pos_tweet = pos_tweet.split(' ')
        new_tweet = []
        for segment in pos_tweet:
            segment = segment.strip().split('/')

            if segment[2] in self.noun_tag:
                self.keywords.add(segment[0] + "\n")
                new_tweet.append(segment[0])

        return ' '.join(new_tweet)


    def build_keyword(self, graph_embedding=False):

        self.logger.info(
            Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__, 'Start building keywords'))

        graph_embedding_tweets = set()

        with open(self.pos_tweets, 'r') as f:
            data = f.readlines()
            count = 0
            for pos_tweet in data:
                noun_tweet = preprocess_tweet(self.parse_pos_tweet(pos_tweet))

                if len(noun_tweet) > 0:
                    graph_embedding_tweets.append(noun_tweet)
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

        if graph_embedding:
            with open(self.graph_embedding_tweets, 'w') as f:
                f.write('\n'.join(graph_embedding_tweets))
            self.logger.info(
                Logger.build_log_message(self.__class__.__name__, self.build_keyword.__name__,
                                         'Finish building graph embedding tweets'))

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

    def build_seed_keywords(self):

        with open(self.embeddings, 'r') as f:
            embedding_data = f.readlines()
        with open(self.category_keywords, 'r') as f:
            category_keywords = preprocess_tweet(f.read()).split(' ')
        with open(self.output, 'r') as f:
            keywords = f.readlines()
        with open(self.phrases, 'r') as f:
            phrases = f.readlines()

        # build embedding dictionary
        embed_dic = {}
        for line in embedding_data[1:]:
            line = preprocess_tweet(line, lower=False)
            line = line.split(' ')
            embed_dic[line[0].strip()] = [float(i) for i in line[1:]]

        # build category dictionary
        category_keywords_embed = OrderedDict()
        for word in category_keywords:
            word = word.lower()
            if word in embed_dic:
                category_keywords_embed[word] = embed_dic[word]

        # build keywords dictionary
        count = 0
        keywords_embed = OrderedDict()
        for word in keywords:
            word = preprocess_tweet(word)
            count += 1
            if word in embed_dic and not word.startswith('#'):
                keywords_embed[word] = embed_dic[word]

            if count % 10000 == 0:
                self.logger.info(
                    Logger.build_log_message(self.__class__.__name__, self.build_seed_keywords.__name__,
                                             "%s keywords processed" % count))

        # build phrases dictionary
        # phrases_embed = OrderedDict()
        # for phrase in phrases:
        #     phrase = preprocess_tweet(phrase)
        #     phrase = phrase.split(',')
        #     score = float(phrase[1])
        #     phrase = phrase[0]
        #
        #     if score < 0.7:
        #         break
        #
        #     if phrase in embed_dic:
        #         phrases_embed[phrase] = embed_dic[phrase]

        keywords_embed_array = np.asarray(keywords_embed.values())
        # phrases_embed_array = np.asarray(phrases_embed.values())
        category_keywords_array = np.asarray(category_keywords_embed.values())
        keywords_result = cosine_similarity(category_keywords_array, keywords_embed_array)
        # phrases_result = cosine_similarity(category_keywords_array, phrases_embed_array)

        keywords_embed_keys = keywords_embed.keys()
        # phrases_embed_keys = phrases_embed.keys()
        category_keywords_embed_keys = category_keywords_embed.keys()

        cosine_cate = {}
        for i in range(len(keywords_result)):
            cosine_cate[category_keywords_embed_keys[i]] = {}
            for j in range(len(keywords_result[i])):
                if keywords_result[i][j] >= 0.7:
                    cosine_cate[category_keywords_embed_keys[i]][keywords_embed_keys[j]] = keywords_result[i][j]
            # for j in range(len(phrases_result[i])):
            #     if phrases_result[i][j] >= 0.4:
            #         cosine_cate[category_keywords_embed_keys[i]][phrases_embed_keys[j]] = phrases_result[i][j]
        keywords_result = []
        for key in cosine_cate:
            cosine_cate[key] = OrderedDict(sorted(cosine_cate[key].items(), key=lambda t: t[1], reverse=True))
            keywords_result.extend(cosine_cate[key].keys())

        with open(self.seed_keywords_dic, 'w+') as fout:
            json.dump(cosine_cate, fout, indent=4)

        with open(self.seed_keywords, 'w+') as fout:
            fout.write('\n'.join(keywords_result))

    def build_phrases(self):
        return


if __name__ == '__main__':
    start = datetime.utcnow()
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].strip('\n')
    la_paras = paras.load_la_tweets_paras(dir=git_version)
    gen = SeedTermGenerator(la_paras, paras.MAIN_LOG)
    # gen.build_pos_tag_tweets()
    gen.build_keyword(graph_embedding=True)
    # gen.build_category_keywords()
    # gen.build_seed_keywords()
