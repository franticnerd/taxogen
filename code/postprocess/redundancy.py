import numpy as np
from os import listdir
from os.path import isfile, join
from collections import defaultdict

def load_inverted_index(reidx):
    pd_map = defaultdict(set)
    with open(reidx) as f:
        for line in f:
            segments = line.strip('\r\n').split('\t')
            doc_ids = segments[1].split(',')
            if len(doc_ids) > 0 and doc_ids[0] == '':
                continue
                # print line
            pd_map[segments[0]] = set([int(x) for x in doc_ids])
    return pd_map

def get_tax_filenames(dir):
    return [join(dir, f) for f in listdir(dir) if isfile(join(dir, f))]


def load_taxonomy(tax_file):
    taxonomy = {}
    with open(tax_file) as f:
        for line in f:
            segments = line.strip('\r\n').split('\t')
            node_name = segments[0]
            keywords = segments[1].split(',')
            taxonomy[node_name] = keywords[:10]
    return taxonomy

def compute_pmi(inverted_index, tax):
    values = []
    for node, keywords in tax.items():
        pairs = set(frozenset([i, j]) for i in keywords for j in keywords if i != j)
        for p in pairs:
            pair = list(p)
            sim = compute_pair_pmi(inverted_index, pair[0], pair[1])
            if sim is not None:
                values.append(sim)
    return np.mean(values)


def compute_pair_pmi(index, w_a, w_b):
    set_a = index[w_a]
    set_b = index[w_b]
    if len(set_a) == 0 or len(set_b) == 0:
        return None
    else:
        return float(len(set_a.intersection(set_b))) / float(len(set_a.union(set_b)))


def main(idx_file, taxonomy_dir, output_file):
    inverted_index = load_inverted_index(idx_file)
    # print len(inverted_index)
    taxonomy_files = get_tax_filenames(taxonomy_dir)
    print taxonomy_files
    with open(output_file, 'a') as fout:
        for tax_file in taxonomy_files:
            tax = load_taxonomy(tax_file)
            pmi = compute_pmi(inverted_index, tax)
            fout.write(str(pmi) + '\t' + tax_file + '\n')


# idx_file = '/shared/data/czhang82/projects/local-embedding/dblp/reidx.txt'
# tax_dir = '/shared/data/czhang82/projects/local-embedding/dblp/taxonomies/'
# eval_dir = '/shared/data/czhang82/projects/local-embedding/dblp/results/'

idx_file = '/Users/chao/data/projects/local-embedding/dblp/input/index.txt'
tax_dir = '/Users/chao/data/projects/local-embedding/dblp/taxonomies/'
eval_dir = '/Users/chao/data/projects/local-embedding/dblp/results/'

output_file = eval_dir + 'jaccard.txt'
main(idx_file, tax_dir, output_file)
