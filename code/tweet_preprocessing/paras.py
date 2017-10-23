# logger name
MAIN_LOG = "MAIN LOG"
# normalization dictionary
lexnorm = './../../lib/emnlp2012-lexnorm/emnlp_dict.txt'

def load_la_tweets_paras():
    ret = {}
    ret['raw'] = '/shared/data/lunanli3/local-embedding/raw/tweets/la/'
    ret['input'] = '/shared/data/lunanli3/local-embedding/input/tweets/la/'
    ret['output'] = '/shared/data/lunanli3/local-embedding/output/tweets/la/'

    # raw tweet data
    ret['tweets'] = ret['raw'] + 'tweets.txt'
    ret['category'] = '/shared/data/lunanli3/local-embedding/raw/category/category.txt'

    # preprocess data
    ret['lexnorm_dic'] = ret['raw'] + 'lexnorm.txt'
    ret['pure_tweets'] = ret['raw'] + 'pure_tweets.txt'
    ret['segmented_pure_tweets'] = ret['raw'] + 'segmented_pure_tweets.txt'
    ret['pos_tweets'] = ret['raw'] + 'pos_tag_tweets.txt'
    ret['keywords'] = ret['raw'] + 'keywords.txt'
    ret['category_keywords'] = ret['raw'] + 'category_keywords.txt'
    ret['embeddings'] = ret['raw'] + 'embeddings.txt'
    ret['seed_keywords_dic'] = ret['raw'] + 'seed_keywords_dic.txt'
    ret['seed_keywords'] = ret['raw'] + 'seed_keywords.txt'
    ret['hashtags'] = ret['raw'] + 'hashtags.txt'
    ret['phrases'] = ret['raw'] + 'phrases.csv'

    # log
    ret['log'] = ret['output'] + 'log/'

    return ret