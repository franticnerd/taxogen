config='dblp.yaml'
# python ../code/cluster-preprocess.py $config

for i in {0..1}
do
  python ../code/main.py $config $i
  python ../code/caseslim.py -folder ../data/dblp/cluster -iter $i
  python ../code/case_ranker.py -folder ../data/dblp/cluster -iter $i -thres 0.15
  python ../code/local_embedding_training.py -folder ../data/dblp/cluster -text ../data/dblp/input/papers.txt -reidx ../data/dblp/reidx.txt -parent \* -N 100
done

