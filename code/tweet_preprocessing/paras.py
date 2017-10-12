la_input = '/shared/data/lunanli3/local-embedding/input/tweets/la/'
la_output = '/shared/data/lunanli3/local-embedding/output/tweets/la/'

# normalization dictionary
lexnorm = './../../lib/emnlp2012-lexnorm/emnlp_dict.txt'

#raw tweet data
la_tweets = la_input + 'tweets.txt'

#preprocess data
lexnorm_dic = la_input + 'lexnorm.txt'
la_pure_tweets = la_input + 'pure_tweets.txt'
la_pos_tweets = la_input + 'tweets_pos_tag.txt'
la_keywords = la_input + 'keywords.txt'

#log
# la_log = la_output + 'log.txt'
la_log = './log.txt'