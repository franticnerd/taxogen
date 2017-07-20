from collections import Counter
import sys
from paras import load_params


def trim_document_set(raw_doc_file, doc_file, keyword_file):
    keyword_set = load_keywords(keyword_file)
    with open(raw_doc_file, 'r') as fin, open(doc_file, 'w') as fout:
        for line in fin:
            doc = line.strip().split()
            if check_doc_contain_keyword(doc, keyword_set):
                fout.write(' '.join(doc) + '\n')


def load_keywords(seed_word_file):
    seed_words = []
    with open(seed_word_file, 'r') as fin:
        for line in fin:
            seed_words.append(line.strip())
    return set(seed_words)


# check whether a document contains one or more keywords
def check_doc_contain_keyword(doc, keyword_set):
    for word in doc:
        if word in keyword_set:
            return True
    return False


def gen_doc_keyword_cnt_file(doc_file, keyword_cnt_file):
    documents = []
    with open(doc_file, 'r') as fin:
        for line in fin:
            keywords = line.strip().split()
            documents.append(keywords)
    doc_word_counts = []
    for d in documents:
        c = Counter(d)
        doc_word_counts.append(c)
    with open(keyword_cnt_file, 'w') as fout:
        for i, counter in enumerate(doc_word_counts):
            counter_string = counter_to_string(counter)
            fout.write(str(i) + '\t' + counter_string + '\n')


def counter_to_string(counter):
    elements = []
    for k, v in counter.items():
        elements.append(k)
        elements.append(v)
    return '\t'.join([str(e) for e in elements])


def main(opt):
    raw_doc_file = opt['raw_doc_file']
    doc_file = opt['doc_file']
    keyword_file = opt['keyword_file']
    doc_keyword_cnt_file = opt['doc_keyword_cnt_file']
    trim_document_set(raw_doc_file, doc_file, keyword_file)
    gen_doc_keyword_cnt_file(doc_file, doc_keyword_cnt_file)

if __name__ == '__main__':
    para_file = None if len(sys.argv) <= 1 else sys.argv[1]
    opt = load_params(para_file)  # load parameters as a dict
    main(opt)
