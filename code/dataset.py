import numpy as np
from collections import defaultdict
from math import log

class DataSet:

    def __init__(self, embedding_file, document_file, candidate_file):
        self.word_to_vec = self.load_embeddings(embedding_file)
        self.keywords = self.load_keywords(candidate_file)
        self.keyword_set = set(self.keywords)
        self.keyword_to_id = self.gen_keyword_id()
        self.documents = self.load_documents(document_file)
        self.documents_trimmed = self.get_trimmed_documents()
        self.keyword_idf = self.build_keyword_idf()

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
        documents = []
        with open(document_file, 'r') as fin:
            for line in fin:
                keywords = line.strip().split()
                documents.append(keywords)
        return documents

    def get_trimmed_documents(self):
        trimmed_documents = []
        for d in self.documents:
            trimmed_doc = [e for e in d if e in self.keyword_set]
            trimmed_documents.append(trimmed_doc)
        return trimmed_documents

    def load_keywords(self, seed_word_file):
        seed_words = []
        with open(seed_word_file, 'r') as fin:
            for line in fin:
                seed_words.append(line.strip())
        return seed_words

    def gen_keyword_id(self):
        keyword_to_id = {}
        for idx, keyword in enumerate(self.keywords):
            keyword_to_id[keyword] = idx
        return keyword_to_id

    def get_candidate_embeddings(self):
        ret = []
        for word in self.keywords:
            vec = self.word_to_vec[word]
            ret.append(vec)
        return np.array(ret)

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

if __name__ == '__main__':
    data_dir = '/Users/chao/data/projects/local-embedding/toy/'
    document_file = data_dir + 'input/papers.txt'
    keyword_file = data_dir + 'input/candidates.txt'
    embedding_file = data_dir + 'input/embeddings.txt'
    dataset = DataSet(embedding_file, document_file, keyword_file)
    print len(dataset.get_candidate_embeddings())
    print dataset.get_candidate_embeddings()
