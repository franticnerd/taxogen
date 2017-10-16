import subprocess, os
from util.logger import Logger
from tweet_handler import TweetHandler
from paras import la_log, la_tweets, la_raw, la_pos_tweets, la_keywords, la_pure_tweets, lexnorm, MAIN_LOG, la_category_keywords, la_category, la_embeddings
from seed_term_generator import KeywordGenerator

if __name__ == '__main__':
    git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0]
    dir = la_log + git_version.strip('\n')
    if not os.path.exists(dir):
        os.mkdir(dir)

    logger = Logger(dir + "/log.txt")

    # generate lexnorm.txt, pure_tweets.txt, embeddings.txt
    tweet_handler = TweetHandler(la_tweets, la_raw, MAIN_LOG, lexnorm)
    tweet_handler.preprocess()

    # generate pos_tag_tweets.txt and keywords.txt
    gen = KeywordGenerator(la_pure_tweets, la_pos_tweets, la_keywords, MAIN_LOG, la_category, la_category_keywords, la_embeddings)
    gen.build_pos_tag_tweets()
    gen.build_keyword()
