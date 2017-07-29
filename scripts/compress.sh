# python ./compress.py -root ../data/dblp/cluster -output ../data/dblp/taxonomies/cluster.txt

python ../code/compress.py -root ../data/dblp/ablation-no-caseolap-l3 -output ../data/dblp/taxonomies/l3-ablation-no-caseolap.txt
python ../code/compress.py -root ../data/dblp/ablation-no-caseolap-l4 -output ../data/dblp/taxonomies/l4-ablation-no-caseolap.txt

python ../code/compress.py -root ../data/dblp/our-l3-0.15 -output ../data/dblp/taxonomies/l3-our-0.15.txt
python ../code/compress.py -root ../data/dblp/our-l4-0.25 -output ../data/dblp/taxonomies/l4-our-0.25.txt

python ../code/compress.py -root ../data/dblp/ablation-no-local-embedding-l3-0.15 -output ../data/dblp/taxonomies/l3-ablation-no-local-embedding-0.15.txt
python ../code/compress.py -root ../data/dblp/ablation-no-local-embedding-l4-0.15 -output ../data/dblp/taxonomies/l4-ablation-no-local-embedding-0.15.txt
python ../code/compress.py -root ../data/dblp/ablation-no-local-embedding-l4-0.25 -output ../data/dblp/taxonomies/l4-ablation-no-local-embedding-0.25.txt

python ../code/compress.py -root ../data/dblp/hc-l3 -output ../data/dblp/taxonomies/l3-hc.txt
python ../code/compress.py -root ../data/dblp/hc-l4 -output ../data/dblp/taxonomies/l4-hc.txt
