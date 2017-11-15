import os, datetime
from util.logger import Logger
# logger name
MAIN_LOG = "MAIN LOG"
# normalization dictionary
lexnorm = './../../lib/emnlp2012-lexnorm/emnlp_dict.txt'


def load_la_tweets_paras(dir, phrases=False, create_log=True):
    ret = {}
    ret['raw'] = '/shared/data/lunanli3/local-embedding/raw/tweets/la/'
    ret['input'] = '/shared/data/lunanli3/local-embedding/input/tweets/la/'
    ret['output'] = '/shared/data/lunanli3/local-embedding/output/tweets/la/'

    # raw tweet data
    ret['tweets'] = ret['raw'] + 'tweets.txt'
    ret['category'] = '/shared/data/lunanli3/local-embedding/raw/category/category.txt'

    # preprocess data
    ret['lexnorm_dic'] = ret['raw'] + 'lexnorm.txt'
    ret['train_edges'] = ret['raw'] + 'train_edges.txt'

    if phrases:
        ret['pure_tweets'] = ret['raw'] + 'segmented_pure_tweets.txt'
        ret['embeddings'] = ret['raw'] + 'segmented_embeddings.txt'
    else:
        ret['pure_tweets'] = ret['raw'] + 'pure_tweets.txt'
        ret['embeddings'] = ret['raw'] + 'embeddings.txt'

    ret['graph_embedding_tweets'] = ret['raw'] + 'graph_embedding_tweets.txt'
    ret['pos_tweets'] = ret['raw'] + 'pos_tag_tweets.txt'
    ret['keywords'] = ret['raw'] + 'keywords.txt'
    ret['category_keywords'] = ret['raw'] + 'category_keywords.txt'
    ret['seed_keywords_dic'] = ret['raw'] + 'seed_keywords_dic.txt'
    ret['seed_keywords'] = ret['raw'] + 'seed_keywords.txt'
    ret['hashtags'] = ret['raw'] + 'hashtags.txt'
    ret['phrases'] = ret['raw'] + 'phrases.csv'
    ret['line_paras'] = load_line_paras()
    ret['co_occurrence_tweets'] = ret['raw'] + 'co_word/'

    # log
    ret['log'] = ret['output'] + 'log/' + dir

    if create_log:
        if not os.path.exists(ret['log']):
            os.makedirs(ret['log'])
        ret['log'] = ret['log'] + '/{}.txt'.format(datetime.datetime.now().strftime("%I:%M:%S_%B_%d_%Y"))
        print 'log: {}'.format(ret['log'])
        logger = Logger(ret['log'])
    return ret


def load_line_paras():
    paras = {'size': '100', 'order': '1', 'negative': '5', 'samples': '100', 'rho': '0.025', 'thread': '20', 'min_count': 5}
    return paras
