import sys

from dataset import DataSet
from cluster import run_clustering
from paras import *
from caseslim import main_caseolap
from case_ranker import rank_phrase
from local_embedding_training import main_local_embedding


class DataFiles:
    def __init__(self, input_dir, node_dir):
        self.doc_file = input_dir + 'papers.txt'
        self.link_file = input_dir + 'keyword_cnt.txt'
        self.index_file = input_dir + 'index.txt'

        self.embedding_file = node_dir + 'embeddings.txt'
        self.seed_keyword_file = node_dir + 'seed_keywords.txt'
        self.doc_id_file = node_dir + 'doc_ids.txt'

        self.doc_membership_file = node_dir + 'paper_cluster.txt'
        self.hierarchy_file = node_dir + 'hierarchy.txt'
        self.cluster_keyword_file = node_dir + 'cluster_keywords.txt'

        self.caseolap_keyword_file = node_dir + 'caseolap.txt'
        self.filtered_keyword_file = node_dir + 'keywords.txt'


'''
input_dir: the directory for storing the input files that do not change
node_dir: the directory for the current node in the hierarchy
n_cluster: the number of clusters
filter_thre: the threshold for filtering general keywords in the caseolap phase
parent: the name of the parent node
n_expand: the number of phrases to expand from the center
level: the current level in the recursion
'''


def recur(input_dir, node_dir, n_cluster, parent, n_cluster_iter, filter_thre, n_expand, level):
    if level >= 2:
        return
    print '============================= Running level ', level, ' and node ', parent, '============================='
    df = DataFiles(input_dir, node_dir)
    full_data = DataSet(df.embedding_file, df.doc_file)
    print 'Done reading the full data.'
    print node_dir

    for iter in xrange(n_cluster_iter):
        if iter > 0:
            df.seed_keyword_file = df.filtered_keyword_file

        children = run_clustering(full_data, df.doc_id_file, df.seed_keyword_file, n_cluster, node_dir, parent,\
                       df.cluster_keyword_file, df.hierarchy_file, df.doc_membership_file)

        main_caseolap(df.link_file, df.doc_membership_file, df.cluster_keyword_file, df.caseolap_keyword_file)

        rank_phrase(df.caseolap_keyword_file, df.filtered_keyword_file, filter_thre)

    main_local_embedding(node_dir, df.doc_file, df.index_file, parent, n_expand)

    for child in children:
        recur(input_dir, node_dir + child + '/', n_cluster, child, n_cluster_iter, filter_thre, n_expand, level + 1)


def main(opt):
    input_dir = opt['input_dir']
    node_dir = opt['root_node_dir']
    n_cluster = opt['n_cluster']
    filter_thre = opt['filter_thre']
    n_expand = opt['n_expand']
    n_cluster_iter = opt['n_cluster_iter']
    level = 0
    recur(input_dir, node_dir, n_cluster, '*', n_cluster_iter, filter_thre, n_expand, level)

if __name__ == '__main__':
    # para_file = None if len(sys.argv) <= 1 else sys.argv[1]
    # iter = 0 if len(sys.argv) <= 1 else int(sys.argv[2])
    # opt = load_params(para_file)  # load parameters as a dict
    # change_params(opt, iter)
    # opt = load_toy_params()
    opt = load_dblp_params()
    main(opt)
