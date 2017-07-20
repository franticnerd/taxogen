from collections import defaultdict

from scipy.spatial.distance import cosine
from spherecluster import SphericalKMeans

class Clusterer:

    def __init__(self, data, n_cluster):
        self.data = data
        self.n_cluster = n_cluster
        self.clus = SphericalKMeans(n_cluster)
        self.clusters = defaultdict(list)  # cluster id -> members
        self.membership = None  # a list contain the membership of the data points

    def fit(self):
        self.clus.fit(self.data)
        labels = self.clus.labels_
        for idx, label in enumerate(labels):
            self.clusters[label].append(idx)
        self.membership = labels

    # find the idx of each cluster center
    def gen_center_idx(self):
        ret = []
        for cluster_id in xrange(self.n_cluster):
            center_idx = self.find_center_idx_for_one_cluster(cluster_id)
            ret.append((cluster_id, center_idx))
        return ret

    def find_center_idx_for_one_cluster(self, cluster_id):
        query_vec = self.clus.cluster_centers_[cluster_id]
        members = self.clusters[cluster_id]
        best_similarity, ret = -1, -1
        for member_idx in members:
            member_vec = self.data[member_idx]
            cosine_sim = self.calc_cosine(query_vec, member_vec)
            if cosine_sim > best_similarity:
                best_similarity = cosine_sim
                ret = member_idx
        return ret

    def calc_cosine(self, vec_a, vec_b):
        return 1 - cosine(vec_a, vec_b)

    # the descriptions should have the same size as data
    def write_cluster_keyword(self, keywords, output_file):
        with open(output_file, 'w') as fout:
            for clus_id in xrange(self.n_cluster):
                members = self.clusters[clus_id]
                for keyword_id in members:
                    keyword = keywords[keyword_id]
                    fout.write(str(clus_id) + '\t' + keyword + '\n')

    def write_hierarchy(self, clus_centers, keywords, parent_keyword, output_file):
        with open(output_file, 'w') as fout:
            for cluster_id, center_idx in clus_centers:
                keyword = keywords[center_idx]
                fout.write(keyword + ' ' + parent_keyword + '\n')

    # the descriptions should have the same size as data
    def write_document_membership(self, documents, keyword_to_id, keyword_idf, output_file):
        with open(output_file, 'w') as fout:
            for idx, doc in enumerate(documents):
                doc_membership = self.get_doc_membership(doc, keyword_to_id, keyword_idf)
                cluster_id = self.assign_document(doc_membership)
                fout.write(str(idx) + '\t' + str(cluster_id) + '\n')

    def get_doc_membership(self, document, keyword_to_id, keyword_idf):
        ret = [0.0] * self.n_cluster
        for keyword in document:
            keyword_id = keyword_to_id[keyword]
            cluster_id = self.membership[keyword_id]
            idf = keyword_idf[keyword]
            ret[cluster_id] += idf
        return ret

    def assign_document(self, doc_membership):
        best_idx, max_score = -1, 0
        for idx, score in enumerate(doc_membership):
            if score > max_score:
                best_idx, max_score = idx, score
        return best_idx
