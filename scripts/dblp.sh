config='dblp.yaml'
# python ../code/cluster-preprocess.py $config

for i in {0..4}
do
  python ../code/main.py $config $i
  python ../code/caseslim.py -folder ../data/dblp/cluster -iter $i
  python ../code/case_ranker.py -folder ../data/dblp/cluster -iter $i -thres 0.15
done
