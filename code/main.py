import sys

from dataset import DataSet
from cluster import Clusterer
from paras import load_params

def main(opt):
    document_file = opt['doc_file']
    keyword_file = opt['keyword_file']
    embedding_file = opt['embedding_file']
    dataset = DataSet(embedding_file, document_file, keyword_file)
    keyword_embeddings = dataset.get_candidate_embeddings()
    n_cluster = opt['n_cluster']
    hierarchy_file = opt['hierarchy_file']
    cluster_keyword_file = opt['cluster_keyword_file']
    doc_membership_file = opt['doc_membership_file']

    keywords = dataset.keywords
    documents = dataset.documents_trimmed

    clus = Clusterer(keyword_embeddings, n_cluster)
    clus.fit()

    clus.write_cluster_keyword(keywords, cluster_keyword_file)

    clus_centers = clus.gen_center_idx()
    clus.write_hierarchy(clus_centers, keywords, '*', hierarchy_file)

    keyword_to_id = dataset.keyword_to_id
    keyword_idf = dataset.keyword_idf
    clus.write_document_membership(documents, keyword_to_id, keyword_idf, doc_membership_file)

if __name__ == '__main__':
    para_file = None if len(sys.argv) <= 1 else sys.argv[1]
    opt = load_params(para_file)  # load parameters as a dict
    main(opt)
