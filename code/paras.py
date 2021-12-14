import yaml
from collections import defaultdict

class yaml_loader:
    def load(self, para_file):
        yaml.add_constructor('!join', self._concat)
        fin = open(para_file, 'r')
        # using default dict: if the key is not specified, the values is None
        return defaultdict(lambda: None, yaml.load(fin))
    def _concat(self, loader, node):
        seq = loader.construct_sequence(node)
        return ''.join([str(i) for i in seq])

def load_params(para_file):
    if para_file is None:
        para = set_default_params()
    else:
        para = yaml_loader().load(para_file)
    return para

def set_default_params():
    pd = dict()
    pd['data_dir'] = '../data/toy/'
    pd['raw_doc_file'] = pd['data_dir'] + 'raw/papers.txt'
    pd['raw_keyword_file'] = pd['data_dir'] + 'raw/keywords.txt'
    pd['doc_file'] = pd['data_dir'] + 'input/papers.txt'
    # pd['embedding_file'] = pd['data_dir'] + 'input/embeddings.txt'
    pd['doc_keyword_cnt_file'] = pd['data_dir'] + 'input/paper_keyword_cnt.txt'
    # pd['keyword_file'] = pd['data_dir'] + 'input/keywords.txt'
    # output
    pd['input_dir'] = pd['data_dir'] + 'input/'
    pd['root_node_dir'] = pd['data_dir'] + 'cluster/'
    pd['n_cluster'] = 2
    pd['filter_thre'] = 0.15
    pd['n_expand'] = 100

    # pd['filtered_keyword_file'] = pd['data_dir'] + 'output/keywords-'
    # pd['hierarchy_file'] = pd['data_dir'] + 'output/hierarchy-'
    # pd['doc_membership_file'] = pd['data_dir'] + 'output/paper_cluster-'
    # pd['cluster_keyword_file'] = pd['data_dir'] + 'output/cluster_keyword-'
    return pd


# change the parameters based on iteration
def change_params(pd, iter):
    if iter == 0:
        pd['filtered_keyword_file'] = pd['keyword_file']
    else:
        pd['filtered_keyword_file'] += str(iter - 1) + '.txt'
    pd['hierarchy_file'] += str(iter) + '.txt'
    pd['doc_membership_file'] += str(iter) + '.txt'
    pd['cluster_keyword_file'] += str(iter) + '.txt'



def load_toy_params():
    pd = dict()
    # pd['data_dir'] = '/Users/chao/data/projects/local-embedding/toy/'
    pd['data_dir'] = '/shared/data/jiaming/local-embedding/sp'
    pd['doc_file'] = pd['data_dir'] + 'input/papers.txt'
    pd['doc_keyword_cnt_file'] = pd['data_dir'] + 'input/keyword_cnt.txt'
    pd['input_dir'] = pd['data_dir'] + 'input/'
    pd['root_node_dir'] = pd['data_dir'] + 'cluster/'
    pd['n_cluster'] = 2
    pd['filter_thre'] = 0.15
    pd['n_expand'] = 100
    pd['n_cluster_iter'] = 2
    return pd


def load_dblp_params():
    pd = dict()
    pd['data_dir'] = '/shared/data/czhang82/projects/local-embedding/dblp/'
    pd['doc_file'] = pd['data_dir'] + 'input/papers.txt'
    pd['doc_keyword_cnt_file'] = pd['data_dir'] + 'input/keyword_cnt.txt'
    pd['input_dir'] = pd['data_dir'] + 'input/'
    pd['root_node_dir'] = pd['data_dir'] + 'cluster/'
    pd['n_cluster'] = 5
    pd['filter_thre'] = 0.25
    pd['n_expand'] = 100
    pd['n_cluster_iter'] = 5
    return pd


def load_sp_params():
    pd = dict()
    # pd['data_dir'] = '/shared/data/czhang82/projects/local-embedding/sp/'
    pd['data_dir'] = '/shared/data/jiaming/local-embedding/sp/'
    pd['doc_file'] = pd['data_dir'] + 'input/papers.txt'
    pd['doc_keyword_cnt_file'] = pd['data_dir'] + 'input/keyword_cnt.txt'
    pd['input_dir'] = pd['data_dir'] + 'input/'
    pd['root_node_dir'] = pd['data_dir'] + 'cluster/'
    pd['n_cluster'] = 5
    pd['filter_thre'] = 0.15
    pd['n_expand'] = 200
    pd['n_cluster_iter'] = 5
    return pd


def load_dblp_params_method():
    pd = dict()
    pd['data_dir'] = '/home/sasce/PycharmProjects/taxogen/data/dblp/'
    pd['doc_file'] = pd['data_dir'] + 'input/papers.txt'
    pd['doc_keyword_cnt_file'] = pd['data_dir'] + 'input/keyword_cnt.txt'
    pd['input_dir'] = pd['data_dir'] + 'input/'
    pd['root_node_dir'] = pd['data_dir'] + 'cluster/'
    pd['n_cluster'] = 5
    pd['filter_thre'] = 0.15
    pd['n_expand'] = 200
    pd['n_cluster_iter'] = 5
    return pd

