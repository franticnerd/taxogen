la_raw = '/shared/data/lunanli3/local-embedding/raw/tweets/la/'
la_input = '/shared/data/lunanli3/local-embedding/input/tweets/la/'
la_output = '/shared/data/lunanli3/local-embedding/output/tweets/la/'

# normalization dictionary
lexnorm = './../../lib/emnlp2012-lexnorm/emnlp_dict.txt'

# raw tweet data
la_tweets = la_raw + 'tweets.txt'
la_category = '/shared/data/lunanli3/local-embedding/raw/category/category.txt'

# preprocess data
lexnorm_dic = la_raw + 'lexnorm.txt'
la_pure_tweets = la_raw + 'pure_tweets.txt'
la_pos_tweets = la_raw + 'pos_tag_tweets.txt'
la_keywords = la_raw + 'keywords.txt'
la_category_keywords = la_raw + 'category_keywords.txt'
la_embeddings = la_raw + 'embeddings.txt'
la_seed_keywords_dic = la_raw + 'seed_keywords_dic.txt'
la_seed_keywords = la_raw + 'seed_keywords.txt'

# logger name
MAIN_LOG = "MAIN LOG"

# log
la_log = la_output + 'log/'
