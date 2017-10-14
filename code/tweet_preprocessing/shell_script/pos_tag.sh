cd ./../../../twitter_nlp
export TWITTER_NLP=./
python python/ner/extractEntities.py $1 -o $2 --classify --pos
cd ./../local-embedding/code/tweet_preprocessing/
