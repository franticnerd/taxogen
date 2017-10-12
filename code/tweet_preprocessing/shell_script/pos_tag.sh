cd ./../../../twitter_nlp
export TWITTER_NLP=./
python python/ner/extractEntities.py $1 -o $2
cd ./../local-embedding/code/tweet_preprocessing/