# About

This repo is an implementation of the following paper for constructing topic taxonomy from text corpora.

"TaxoGen: Unsupervised Topic Taxonomy Construction by Adaptive Term Embedding and Clustering",
Chao Zhang, Fangbo Tao, Xiusi Chen, Jiaming Shen, Meng Jiang, Brian Sadler, Michelle Vanni, Jiawei Han,
ACM SIGKDD Conference on Knowledge Discovery and Pattern Mining (KDD), 2018.


# Input

The input consists of three files:

1. papers.txt
  - This data file contains all the documents (e.g., paper titles). 
  - Every line is a sequence of processed keywords (either uni-grams or phrases). 
  - The keywords are separated by blank spaces (words in a phrase are concatenated by '_').
2. keywords.txt
  - This data file contains all keywords extracted from the document collection (e.g., entities, noun phrases). 
  - Every line is a keyword.
3. embeddings.txt
  - This data file contains the embeddings of all the keywords. 
  - Every line is the embedding of a keyword.



The DBLP dataset used in the paper is available here:

https://drive.google.com/file/d/1GbxKrxrmFrKt5vgDHP1xe1Qr_rfvR1jh/view?usp=sharing


# How to run?

You can use "python main.py" to run TaxoGen.

A full pipeline is included in run.sh, including how we preprocess the corpus, run TaxoGen, and postproces the results for visualization.

