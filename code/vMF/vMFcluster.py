'''
__author__: Jiaming Shen (adapted from Chao Zhang's previous cluster.py)
__description__: Experiment on using movMF to do spherecial clustering with rejection option
__latest_updates__: 10/21/2017
'''
from collections import defaultdict
from scipy.spatial.distance import cosine
from spherecluster import SphericalKMeans, VonMisesFisherMixture
from sklearn.preprocessing import normalize
import utils
import time


class Clusterer:

    def __init__(self, data, n_cluster, method="soft-movMF", init="random-class", n_init=10, n_jobs=1):
        self.data = data
        self.n_cluster = n_cluster
        self.method = method

        if method == "spk":
          self.clus = SphericalKMeans(n_clusters=n_cluster)
        elif method == "hard-movMF":
          self.clus = VonMisesFisherMixture(n_clusters=n_cluster, posterior_type='hard',
                                            init = init, n_init = n_init, n_jobs = n_jobs)
        elif method == "soft-movMF":
          self.clus = VonMisesFisherMixture(n_clusters=n_cluster, posterior_type='soft',
                                            init = init, n_init = n_init, n_jobs = n_jobs)

        self.clusters = {}  # cluster id -> dict(element_id: distance to center)
        self.clusters_phrase = {} # cluster id -> representative words
        self.membership = None  # a list contain the membership of the data points
        self.center_ids = None  # a list contain the ids of the cluster centers
        self.inertia_scores = None


    def fit(self, debug=False):
        start = time.time()
        self.clus.fit(self.data)
        end = time.time()
        print("Finish fitting data of size %s using %s seconds" % (self.data.shape, (end-start)))
        self.inertia_scores = self.clus.inertia_
        print('Clustering inertia score (smaller is better):', self.inertia_scores)

        labels = self.clus.labels_
        self.membership = labels

        if debug:
            print("Labels:", labels)
          # print("cluster_centers_:", self.clus.cluster_centers_)
            if self.method != "spk":
                print("concentrations_:", self.clus.concentrations_)
                print("weights_:", self.clus.weights_)
                print("posterior_:", self.clus.posterior_)

        for idx, label in enumerate(labels):
            cluster_center = self.clus.cluster_centers_[int(label)]
            consine_sim =  self.calc_cosine(self.data[idx], cluster_center)
            if label not in self.clusters:
                self.clusters[label] = {}
                self.clusters[label][idx] = consine_sim
            else:
                self.clusters[label][idx] = consine_sim

        for cluster_id in range(self.n_cluster):
            self.clusters_phrase[cluster_id] = sorted(self.clusters[cluster_id].items(), key = lambda x:-x[1])


        # self.center_ids = self.gen_center_idx()


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

    def find_phrase_rank(self, phrase, cluster_id):
        for idx, ele in enumerate(self.clusters_phrase[cluster_id]):
            if ele[0] == phrase:
                return (idx+1)
        return -1

    def senity_check(self):
        for phrase_id in range(self.data.shape[0]):
            cluster_member = self.membership[phrase_id]
            result = []
            for cluster_id in range(self.n_cluster):
                cluster_rank = self.find_phrase_rank(phrase_id, cluster_id)
                sim = self.calc_cosine(self.data[phrase_id], self.clus.cluster_centers_[cluster_id])
                if sim < 0:
                    print(phrase_id, sim)
                    return
                # result.append((cluster_id, cluster_rank, sim))
            # print("Put in cluster: %s" % cluster_member)
            # print("Rank information in all clusters: %s" % str(result))


    def explore(self, keyword2id=None, id2keyword=None, iteractive=False):
        for cluster_id in range(self.n_cluster):
            print("Cluster %s top keywords" % cluster_id)
            for rank, keyword_id in enumerate(self.clusters_phrase[cluster_id][0:10]):
                print("Rank:%s keywords:%s (score=%s)" % (rank+1, id2keyword[keyword_id[0]], keyword_id[1]))
            print("="*80)

        if iteractive:
            while(True):
                phrase = input('Input keyword (use "_" to concat tokens for phrase): ')
                if len(phrase) == 0:
                    break

                if phrase not in keyword2id:
                    print("Out of vocabulary keyword, please try again")
                    continue
                else:
                    phrase_id = keyword2id[phrase]
                    cluster_member = self.membership[phrase_id]
                    result = []
                    for cluster_id in range(self.n_cluster):
                        cluster_rank = self.find_phrase_rank(phrase_id, cluster_id)
                        sim = self.calc_cosine(self.data[phrase_id], self.clus.cluster_centers_[cluster_id])
                        result.append((cluster_id, cluster_rank, sim))
                    print("Put in cluster: %s" % cluster_member )
                    print("Rank information in all clusters: %s" % str(result))



def run_clustering(full_data, doc_id_file, filter_keyword_file, n_cluster, parent_direcotry, parent_description,\
                   cluster_keyword_file, hierarchy_file, doc_membership_file):
    dataset = SubDataSet(full_data, doc_id_file, filter_keyword_file)
    print('Start clustering for ', len(dataset.keywords), ' keywords under parent:', parent_description)
    ## TODO: change later here for n_cluster selection from a range
    clus = Clusterer(dataset.embeddings, n_cluster)
    clus.fit()
    print('Done clustering for ', len(dataset.keywords), ' keywords under parent:', parent_description)
    dataset.write_cluster_members(clus, cluster_keyword_file, parent_direcotry)
    center_names = dataset.write_cluster_centers(clus, parent_description, hierarchy_file)
    dataset.write_document_membership(clus, doc_membership_file, parent_direcotry)
    print('Done saving cluster results for ', len(dataset.keywords), ' keywords under parent:', parent_description)
    return center_names

if __name__ == '__main__':
    f_embeddings = "../../data/eecs/keyword_embeddings.txt"
    keyword2id, id2keyword, embeddings = utils.load_keyword_embeddings(f_embeddings)

    ## L2-normalization
    # embeddings = normalize(embeddings)
    ## Fitting cluster
    clus = Clusterer(embeddings, n_cluster=8, method='spk', n_init=4, n_jobs=4)
    clus.fit(debug=True)
    clus.explore(keyword2id=keyword2id, id2keyword=id2keyword, iteractive=True)
    # clus.senity_check()
    print('Done clustering for ', len(keyword2id), ' keywords')
