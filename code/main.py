import sys

from dataset import SubDataSet, load_dataset
from cluster import run_clustering
from paras import load_params, change_params


def main(opt):
    full_data = load_dataset(opt)

    filter_keyword_file = opt['filtered_keyword_file']
    dataset = SubDataSet(full_data, filter_keyword_file)

    n_cluster = opt['n_cluster']
    clus = run_clustering(dataset.embeddings, n_cluster)

    cluster_keyword_file = opt['cluster_keyword_file']
    dataset.write_cluster_keywords(clus, cluster_keyword_file)

    hierarchy_file = opt['hierarchy_file']
    dataset.write_cluster_centers(clus, '*', hierarchy_file)

    doc_membership_file = opt['doc_membership_file']
    dataset.write_document_membership(clus, doc_membership_file)


if __name__ == '__main__':
    para_file = None if len(sys.argv) <= 1 else sys.argv[1]
    iter = 0 if len(sys.argv) <= 1 else int(sys.argv[2])
    opt = load_params(para_file)  # load parameters as a dict
    change_params(opt, iter)
    main(opt)
