import numpy as np
from spherecluster import SphericalKMeans
from collections import defaultdict
from scipy.spatial.distance import cosine

class Clusterer:
    def __init__(self, data, n_cluster):
        self.data = data
        self.n_cluster = n_cluster
        self.clus = SphericalKMeans(n_cluster)
        self.membership = defaultdict(list)

    def fit(self):
        self.clus.fit(self.data)
        labels = self.clus.labels_
        for idx, label in enumerate(labels):
            self.membership[label].append(idx)

    # find the idx of each cluster center
    def gen_center_idx(self):
        ret = []
        for cluster_id in xrange(self.n_cluster):
            center_idx = self.find_center_idx_for_one_cluster(cluster_id)
            ret.append((cluster_id, center_idx))
        return ret


    def find_center_idx_for_one_cluster(self, cluster_id):
        query_vec = self.clus.cluster_centers_[cluster_id]
        members = self.membership[cluster_id]
        best_similarity, ret = -1, -1
        for member_idx in members:
            member_vec = self.data[member_idx]
            cosine_sim = self.calc_cosine(query_vec, member_vec)
            if cosine_sim > best_similarity:
                best_similarity = cosine_sim
                ret = member_idx
        print best_similarity
        return ret

    def calc_cosine(self, vec_a, vec_b):
        return 1 - cosine(vec_a, vec_b)

    # the descriptions should have the same size as data
    def print_cluster(self, descriptions):
        for label in xrange(self.n_cluster):
            idx_list = self.membership[label]
            members = [descriptions[idx] for idx in idx_list]
            print members


class DataSet:
    def __init__(self, data_file):
        self.word_to_vec = {}
        with open(data_file, 'r') as fin:
            header = fin.readline()
            print 'loading data file: ', header
            for line in fin:
                items = line.strip().split()
                word = items[0]
                vec = [float(v) for v in items[1:]]
                self.word_to_vec[word] = vec


    def gen_np_array(self, word_list):
        ret = []
        for word in word_list:
            vec = self.word_to_vec[word]
            ret.append(vec)
        return np.array(ret)

def load_seed_words(seed_word_file):
    seed_words = []
    with open(seed_word_file, 'r') as fin:
        for line in fin:
            seed_words.append(line.strip())
    return seed_words


def write_hierarchy(clus_centers, descriptions, parent_description, output_file):
    with open(output_file, 'w') as fout:
        for cluster_id, center_idx in clus_centers:
            description = descriptions[center_idx]
            fout.write(description + ' ' + parent_description + '\n')



def main():
    # datafile = '/shared/data/expert_finding/leef/word_embedding/word2vec.txt'
    data_file = '/Users/chao/data/projects/local-embedding/word2vec.txt'
    seed_file = '/Users/chao/data/projects/local-embedding/keywords.txt'
    dataset = DataSet(data_file)
    seed_words = load_seed_words(seed_file)
    vectors = dataset.gen_np_array(seed_words)

    # hierarchy_file = '/shared/data/expert_finding/full/query.hierarchy'
    hierarchy_file = '/Users/chao/data/projects/local-embedding/hierarchy.txt'

    clus = Clusterer(vectors, 5)
    clus.fit()
    clus.print_cluster(seed_words)
    clus_centers = clus.gen_center_idx()
    write_hierarchy(clus_centers, seed_words, '*', hierarchy_file)

if __name__ == '__main__':
    main()

