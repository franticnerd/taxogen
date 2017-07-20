# learn embedding for each papers

ROOT=/shared/data/expert_finding/old-leef
GRAPH=/shared/data/expert_finding/full

TEXT_INPUT=/shared/data/tensor_embedding/data/dblp/raw/paper_phrases.txt.frequent.hardcode
WORD_EMBEDDING=$ROOT/word_embedding/word2vec.txt
QUERY_DATA=/shared/data/expert_finding/full/query.set
HIERARCHY=/shared/data/expert_finding/full/query.hierarchy

# search for semantically related terms
make
mkdir $ROOT/query_relevant
echo "./query_search -context $WORD_EMBEDDING -input $QUERY_DATA -output $ROOT/query_relevant" 
# -----
./query_search -context $WORD_EMBEDDING -input $QUERY_DATA -output $ROOT/query_relevant

exit

# retrain word2vec.txt based on the local queries
TOP=30
THRESHOLD=0

# query rewrite 
mkdir $ROOT/local_embeddings
# -----
python fetch_papers_relevant.py -input $GRAPH -relevant $ROOT/query_relevant -text $TEXT_INPUT \
   -output $ROOT/local_embeddings -query $QUERY_DATA -threshold $THRESHOLD -N $TOP

# retrain the embedding
# -----
python local_embedding_training.py -input $ROOT/local_embeddings -query $QUERY_DATA
