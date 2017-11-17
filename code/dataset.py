'''
__author__: Chao Zhang
__description__: Construct Full dataset and sub dataset objects.
  Currently, the document hard clustering is written in the file
__latest_updates__: 09/25/2017
'''
import numpy as np
from collections import defaultdict
from math import log
from utils import ensure_directory_exist
from tweet_preprocessing.util.logger import Logger
import json
import operator

# the complete data set
class DataSet:

    def __init__(self, embedding_file, document_file):
        self.documents = self.load_documents(document_file)
        self.embeddings = self.load_embeddings(embedding_file)
        # the initial complete set of keywords
        # self.keywords = self.load_keywords(candidate_file)
        # self.keyword_set = set(self.keywords)
        # self.documents_trimmed = self.get_trimmed_documents(self.documents, self.keyword_set)
        # assert len(self.documents) == len(self.documents_trimmed)

    def load_embeddings(self, embedding_file):
        if embedding_file is None:
            return {}
        word_to_vec = {}
        with open(embedding_file, 'r') as fin:
            header = fin.readline()
            for line in fin:
                items = line.strip().split()
                word = items[0]
                vec = [float(v) for v in items[1:]]
                word_to_vec[word] = vec
        return word_to_vec

    def load_documents(self, document_file):
        '''
        :param document_file: papers.txt tweet
        :return: list of documents
        '''
        documents = []
        with open(document_file, 'r') as fin:
            for line in fin:
                keywords = line.strip().split()
                documents.append(keywords)
        return documents

    # # trim the keywords that do not appear in the keyword set
    # def get_trimmed_documents(self, documents, keyword_set):
    #     trimmed_documents = []
    #     for d in documents:
    #         trimmed_doc = [e for e in d if e in keyword_set]
    #         trimmed_documents.append(trimmed_doc)
    #     return trimmed_documents

    # def load_keywords(self, seed_word_file):
    #     seed_words = []
    #     with open(seed_word_file, 'r') as fin:
    #         for line in fin:
    #             seed_words.append(line.strip())
    #     return seed_words

# sub data set for each cluster
class SubDataSet:

    def __init__(self, full_data, doc_id_file, keyword_file):
        """

        :param full_data: Dataset object
        :param doc_id_file: doc_ids.txt doc_id1
        :param keyword_file: keywords.txt keyword1
        """
        self.keywords = self.load_keywords(keyword_file, full_data)
        self.keyword_to_id = self.gen_keyword_id()
        self.keyword_set = set(self.keywords)
        self.embeddings, self.labels = self.load_embeddings(full_data)
        self.documents, self.original_doc_ids = self.load_documents(full_data, doc_id_file)
        self.keyword_idf = self.build_keyword_idf()

    def load_keywords(self, keyword_file, full_data):
        """
        load keywords that have embeddings
        :param keyword_file: keywords.txt keyword1
        :param full_data: Dataset object
        :return: [keyword1, keyword2, ...]
        """
        keywords = []
        logger = Logger.get_logger("MAIN LOG")
        with open(keyword_file, 'r') as fin:
            for line in fin:
                # TODO: filter nouns if use graph embedding
                keyword = line.strip()
                if keyword in full_data.embeddings:
                    keywords.append(keyword)
                else:
                    logger.info('%s not in the embedding file'%keyword)
        return keywords

    def gen_keyword_id(self):
        """
        build a dictionary of keyword and index
        :return: {keyword: idx}
        """
        keyword_to_id = {}
        for idx, keyword in enumerate(self.keywords):
            keyword_to_id[keyword] = idx
        return keyword_to_id

    def load_embeddings(self, full_data):
        """
        select embeddings for keywords, in the same order
        :param full_data:
        :return: array([embedding1, embedding2, ...])
        """
        embeddings = full_data.embeddings
        ret = []
        labels = []
        for word in self.keywords:
            labels.append(word)
            vec = embeddings[word]
            ret.append(vec)
        return np.array(ret), labels

    def load_documents(self, full_data, doc_id_file):
        """
        remove docs that don't contain keywords at current sub-topic
        :param full_data: Dataset object
        :param doc_id_file: doc_ids.txt doc_id1
        :return: trimmed documents along with its corresponding ids
        """
        doc_ids = self.load_doc_ids(doc_id_file)
        trimmed_doc_ids, trimmed_docs = [], []
        for doc_id in doc_ids:
            doc = full_data.documents[doc_id]
            trimmed_doc = [e for e in doc if e in self.keyword_set]
            if len(trimmed_doc) > 0:
                trimmed_doc_ids.append(doc_id)
                trimmed_docs.append(trimmed_doc)
        return trimmed_docs, trimmed_doc_ids

    def load_doc_ids(self, doc_id_file):

        doc_ids = []
        with open(doc_id_file, 'r') as fin:
            for line in fin:
                doc_id = int(line.strip())
                doc_ids.append(doc_id)
        return doc_ids

    def build_keyword_idf(self):
        keyword_idf = defaultdict(float)
        for doc in self.documents:
            word_set = set(doc)
            for word in word_set:
                if word in self.keyword_set:
                    keyword_idf[word] += 1.0
        N = len(self.documents)
        for w in keyword_idf:
            keyword_idf[w] = log(1.0 + N / keyword_idf[w])
        return keyword_idf

    # output_file: one integrated file;
    def write_cluster_members(self, clus, cluster_file, parent_dir):
        """
        write keywords and clusters to file
        :param clus:
        :param cluster_file: cluster_keywords.txt cluster_id \t keyword
        :param parent_dir:
        :return:
        """
        n_cluster = clus.n_cluster
        clusters = clus.clusters  # a dict: cluster id -> keywords
        with open(cluster_file, 'w') as fout:
            for clus_id in range(n_cluster):
                members = clusters[clus_id]
                for keyword_id in members:
                    keyword = self.keywords[keyword_id]
                    fout.write(str(clus_id) + '\t' + keyword + '\n')
        # write the cluster for each sub-folder
        clus_centers = clus.center_ids
        for clus_id, center_keyword_id in clus_centers:
            center_keyword = self.keywords[center_keyword_id]
            output_file = parent_dir + center_keyword + '/seed_keywords.txt'
            ensure_directory_exist(output_file)
            members = clusters[clus_id]
            with open(output_file, 'w') as fout:
                for keyword_id in members:
                    keyword = self.keywords[keyword_id]
                    fout.write(keyword + '\n')

    def write_cluster_centers(self, clus, parent_description, output_file):
        """
        Get center keyword of each cluster
        :param clus:
        :param parent_description:
        :param output_file: hierarchy.txt current label parent label
        :return:
        """
        clus_centers = clus.center_ids
        center_names = []
        with open(output_file, 'w') as fout:
            for cluster_id, keyword_idx in clus_centers:
                keyword = self.keywords[keyword_idx]
                center_names.append(keyword)
                fout.write(keyword + ' ' + parent_description + '\n')
        return center_names


    def write_document_membership(self, clus, output_file, parent_dir):
        """

        :param clus:
        :param output_file: paper_cluster.txt doc_id cluster_id
        :param parent_dir:
        :return:
        """
        n_cluster = clus.n_cluster
        keyword_membership = clus.membership  # an array containing the membership of the keywords
        cluster_document_map = defaultdict(list)  # key: cluster id, value: document list
        with open(output_file, 'w') as fout:
            for idx, doc in zip(self.original_doc_ids, self.documents):
                doc_membership = self.get_doc_membership(n_cluster, doc, keyword_membership)
                cluster_id = self.assign_document(doc_membership)
                cluster_document_map[cluster_id].append(idx)
                fout.write(str(idx) + '\t' + str(cluster_id) + '\n')
        # write the document ids for each sub-folder
        clus_centers = clus.center_ids
        for clus_id, center_keyword_id in clus_centers:
            center_keyword = self.keywords[center_keyword_id]
            output_file = parent_dir + center_keyword + '/doc_ids.txt'
            ensure_directory_exist(output_file)
            doc_ids = cluster_document_map[clus_id]
            with open(output_file, 'w') as fout:
                for doc_id in doc_ids:
                    fout.write(str(doc_id) + '\n')


    def get_doc_membership(self, n_cluster, document, keyword_membership):
        ret = [0.0] * n_cluster
        ## Strength of each document on each cluster is the tf-idf score. The tf part is considered during the
        ## enumeration of document tokens.
        for keyword in document:
            keyword_id = self.keyword_to_id[keyword]
            cluster_id = keyword_membership[keyword_id]
            idf = self.keyword_idf[keyword]
            ret[cluster_id] += idf
        return ret

    def assign_document(self, doc_membership):
        ## Currently document cluster is a hard partition.
        best_idx, max_score = -1, 0
        for idx, score in enumerate(doc_membership):
            if score > max_score:
                best_idx, max_score = idx, score
        return best_idx

    def write_cluster_info(self, similarity_rank, label_cosine, simi_rank_prefix, label_cosine_prefix):

        for cluster_id in similarity_rank:
            simi_file = '{}_{}.txt'.format(simi_rank_prefix, cluster_id)
            label_cosine_file = '{}_{}.txt'.format(label_cosine_prefix, cluster_id)

            simi = {}
            cosine = {}

            for member_idx in similarity_rank[cluster_id]:
                simi[self.labels[member_idx]] = similarity_rank[cluster_id][member_idx]
                cosine[self.labels[member_idx]] = label_cosine[cluster_id][member_idx].tolist()

            simi = sorted(simi.items(), key=operator.itemgetter(1), reverse=True)

            with open(simi_file, 'w') as f:
                json.dump(simi, f)

            with open(label_cosine_file, 'w') as f:
                json.dump(cosine, f)

        return
if __name__ == '__main__':
    data_dir = '/Users/chao/data/projects/local-embedding/toy/'
    document_file = data_dir + 'input/papers.txt'
    keyword_file = data_dir + 'input/candidates.txt'
    embedding_file = data_dir + 'input/embeddings.txt'
    dataset = DataSet(embedding_file, document_file, keyword_file)
    print(len(dataset.get_candidate_embeddings()))
