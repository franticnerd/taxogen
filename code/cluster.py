'''
__author__: Chao Zhang
__description__: A wrapper for spherecluster, implement the term clustering component.
__latest_updates__: 09/25/2017
'''
from collections import defaultdict

from scipy.spatial.distance import cosine
from spherecluster import SphericalKMeans
from dataset import SubDataSet
from tweet_preprocessing.util.logger import Logger


class Clusterer:

    def __init__(self, data, n_cluster):
        self.data = data
        self.n_cluster = n_cluster
        self.clus = SphericalKMeans(n_cluster)
        self.clusters = defaultdict(list)  # cluster id -> members
        self.membership = None  # a list contain the membership of the data points
        self.center_ids = None  # a list contain the ids of the cluster centers
        self.inertia_scores = None
        self.label_cosine = {}
        self.similarity_rank = {}

    def fit(self):
        self.clus.fit(self.data)
        labels = self.clus.labels_
        for idx, label in enumerate(labels):
            self.clusters[label].append(idx)
        self.membership = labels
        self.center_ids = self.gen_center_idx()
        self.inertia_scores = self.clus.inertia_
        logger = Logger.get_logger("MAIN LOG")
        logger.info('Clustering concentration score: %s'%self.inertia_scores)

    # find the idx of each cluster center
    def gen_center_idx(self):
        ret = []
        for cluster_id in range(self.n_cluster):
            center_idx = self.find_center_idx_for_one_cluster(cluster_id)
            ret.append((cluster_id, center_idx))
        return ret

    def find_center_idx_for_one_cluster(self, cluster_id):
        query_vec = self.clus.cluster_centers_[cluster_id]
        members = self.clusters[cluster_id]
        self.similarity_rank[cluster_id] = {}
        self.label_cosine[cluster_id] = {}
        best_similarity, ret = -1, -1
        for member_idx in members:
            member_vec = self.data[member_idx]
            cosine_sim = self.calc_cosine(query_vec, member_vec)
            self.label_cosine[cluster_id][member_idx] = member_vec
            self.similarity_rank[cluster_id][member_idx] = cosine_sim
            if cosine_sim > best_similarity:
                best_similarity = cosine_sim
                ret = member_idx
        return ret

    def calc_cosine(self, vec_a, vec_b):
        return 1 - cosine(vec_a, vec_b)


def run_clustering(full_data, doc_id_file, filter_keyword_file, n_cluster, parent_direcotry, parent_description,\
                   cluster_keyword_file, hierarchy_file, doc_membership_file, simi_rank, label_cosine):
    """

    :param full_data: Dataset object
    :param doc_id_file: doc_ids.txt doc_id1
    :param filter_keyword_file: keywords.txt keyword1
    :param n_cluster: number of minimum clusters
    :param parent_direcotry:
    :param parent_description: parent keyword
    :param cluster_keyword_file: cluster_keywords.txt cluster_id \t keyword
    :param hierarchy_file: hierarchy.txt cluster_center_word parent_word
    :param doc_membership_file: paper_cluster.txt doc_id cluster_id
    :return:
    """
    # TODO: Need to use WordNet to decide parent
    logger = Logger.get_logger("MAIN LOG")
    dataset = SubDataSet(full_data, doc_id_file, filter_keyword_file)
    logger.info('\n')
    logger.info('Start clustering for %s keywords under parent: %s' % (len(dataset.keywords), parent_description))
    ## TODO: change later here for n_cluster selection from a range
    clus = Clusterer(dataset.embeddings, n_cluster)
    clus.fit()
    logger.info('\n')
    logger.info('Done clustering for %s keywords under parent: %s'%(len(dataset.keywords), parent_description))
    dataset.write_cluster_members(clus, cluster_keyword_file, parent_direcotry)
    center_names = dataset.write_cluster_centers(clus, parent_description, hierarchy_file)
    dataset.write_document_membership(clus, doc_membership_file, parent_direcotry)
    dataset.write_cluster_info(clus.similarity_rank, clus.label_cosine, simi_rank, label_cosine)
    logger.info('\n')
    logger.info('Done saving cluster results for %s keywords under parent: %s'%(len(dataset.keywords), parent_description))
    logger.info('\n')
    return center_names
