#!/usr/bin/env
'''
__author__: Chao Zhang
__description__: Run local embedding using word2vec
__latest_updates__: 09/26/2017
'''
import argparse
import subprocess
import utils
import os
from tweet_preprocessing.util.logger import Logger
from graph_embedding.graph_embedding import LINE
from tweet_preprocessing.paras import load_la_tweets_paras

def read_files(folder, parent):
    """

    :param folder: current folder
    :param parent: parent keyword
    :return: embs - keyowrds embedding keywords - keywords cates - cluster dictionary
    """
    logger = Logger.get_logger("MAIN LOG")
    logger.info("[Local-embedding] Reading file: %s"%parent)
    logger.info("[Local-embedding] Folder: {}".format(folder))
    emb_file = '%s/embeddings.txt' % folder
    hier_file = '%s/hierarchy.txt' % folder
    keyword_file = '%s/keywords.txt' % folder ## here only consider those remaining keywords


    embs = utils.load_embeddings(emb_file)
    logger.info("[Local-embedding] Embedding is: {}".format(embs))
    keywords = set()
    cates = {}

    with open(keyword_file) as f:
        for line in f:
            keywords.add(line.strip('\r\n'))

    # select keywords that have embeddings
    tmp_embs = {}
    for k in keywords:
        if k in embs:
            tmp_embs[k] = embs[k]
    embs = tmp_embs

    with open(hier_file) as f:
        for line in f:
            segs = line.strip('\r\n').split(' ')
            if segs[1] == parent:
                cates[segs[0]] = set()

    logger.info('[Local-embedding] Finish reading embedding, hierarchy and keywords files.')

    return embs, keywords, cates

def relevant_phs(embs, cates, N):
    """
    Find the closest N phrases for each cluster
    :param embs: keywords embeddings
    :param cates: clusters
    :param N: n_expand
    :return:
    """
    logger = Logger.get_logger("MAIN LOG")
    for cate in cates:
        worst = -100
        bestw = [-100] * (N + 1)
        bestp = [''] * (N + 1)
        # cate_ph = cate[2:]
        cate_ph = cate

        for ph in embs:
            cate_emb = embs[cate_ph]
            ph_embd = embs[ph]
            sim = utils.cossim(cate_emb, ph_embd)
            if sim > worst:
                for i in range(N):
                    if sim >= bestw[i]:
                        for j in range(N - 1, i - 1, -1):
                            bestw[j+1] = bestw[j]
                            bestp[j+1] = bestp[j]
                        bestw[i] = sim
                        bestp[i] = ph
                        worst = bestw[N-1]
                        break

        # print bestw
        # print bestp

        for ph in bestp[:N]:
            cates[cate].add(ph)

    logger.info('Top similar phrases found.')

    return cates

def revevant_docs(text, reidx, cates):
    logger = Logger.get_logger("MAIN LOG")
    docs = {}
    idx = 0
    pd_map = {}
    for cate in cates:
        for ph in cates[cate]:
            pd_map[ph] = set()

    with open(text) as f:
        for line in f:
            docs[idx] = line
            idx += 1

    with open(reidx) as f:
        for line in f:
            segments = line.strip('\r\n').split('\t')
            doc_ids = segments[1].split(',')
            if len(doc_ids) > 0 and doc_ids[0] == '':
                continue
                # print line
            pd_map[segments[0]] = set([int(x) for x in doc_ids])

    logger.info('Relevant docs found.')

    return pd_map, docs


def run_word2vec(pd_map, docs, cates, folder):
    logger = Logger.get_logger("MAIN LOG")
    for cate in cates:

        c_docs = set()
        for ph in cates[cate]:
            c_docs = c_docs.union(pd_map[ph])

        logger.info('Starting cell %s with %d docs.' % (cate, len(c_docs)))
        
        # save file
        # sub_folder = '%s/%s' % (folder, cate)
        # input_f = '%s/text' % sub_folder
        # output_f = '%s/embeddings.txt' % sub_folder
        sub_folder = folder + cate + '/'
        input_f = sub_folder + 'text'
        output_f = sub_folder + 'embeddings.txt'
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        with open(input_f, 'w+') as g:
            for d in c_docs:
                g.write(docs[d])

        logger.info('[Local-embedding] starting calling word2vec')
        # print(input_f)
        # print(output_f)
        # embed_proc = subprocess.Popen(["./word2vec", "-threads", "20", "-train", input_f, "-output", output_f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # embed_proc.wait()
        subprocess.call(["./word2vec", "-threads", "20", "-train", input_f, "-output", output_f])
        logger.info('[Local-embedding] done training word2vec')


def run_line(pd_map, docs, cates, folder):
    logger = Logger.get_logger("MAIN LOG")
    for cate in cates:

        c_docs = set()
        for ph in cates[cate]:
            c_docs = c_docs.union(pd_map[ph])

        logger.info('Starting cell %s with %d docs.' % (cate, len(c_docs)))

        # save file
        # sub_folder = '%s/%s' % (folder, cate)
        # input_f = '%s/text' % sub_folder
        # output_f = '%s/embeddings.txt' % sub_folder
        sub_folder = folder + cate + '/'
        input_f = sub_folder + 'text'
        output_f = sub_folder + 'embeddings.txt'
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        with open(input_f, 'w+') as g:
            for d in c_docs:
                g.write(docs[d])
        train_file = sub_folder + "train_edges.txt"
        git_version = subprocess.Popen('git rev-parse --short HEAD', shell=True, stdout=subprocess.PIPE).communicate()[0].strip('\n')
        paras = load_la_tweets_paras(dir=git_version, create_log=False)
        line = LINE(paras)
        logger.info('[Local-embedding] starting generating input for line')
        line.build_train_file(input_file=input_f, train_file=train_file)
        logger.info('[Local-embedding] line starts generating embedding')
        line.run(train_file=train_file, output_file=output_f)
        logger.info('[Local-embedding] done training line')
        word_co_occurrence = sub_folder + "keyword_co_occurrence.txt"
        line.build_co_occurrence_dic(train_file, word_co_occurrence)
        logger.info('[Local-embedding] done generating keyword co-occurrences')

def main_local_embedding(folder, doc_file, reidx, parent, N):
    """

    :param word_co_occurrence:
    :param folder: current folder
    :param doc_file: papers.txt tweet1 \n tweet2 \n tweet3 ...
    :param reidx: index.txt word doc_num1 doc_num2 ...
    :param parent: parent keyword
    :param N: n_expand
    :return:
    """
    embs, keywords, cates = read_files(folder, parent)
    cates = relevant_phs(embs, cates, int(N))
    pd_map, docs = revevant_docs(doc_file, reidx, cates)
    run_line(pd_map, docs, cates, folder)
    #run_word2vec(pd_map, docs, cates, folder)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='local_embedding_training.py', \
            description='Train Embeddings for each query.')
    parser.add_argument('-folder', required=True, \
            help='The folder of previous level.')
    parser.add_argument('-text', required=True, \
            help='The raw text file.')
    parser.add_argument('-reidx', required=True, \
            help='The reversed index file.')
    parser.add_argument('-parent', required=True, \
            help='the target expanded phrase')
    parser.add_argument('-N', required=True, \
            help='The number of neighbor used to extract documents')
    args = parser.parse_args()
    main_local_embedding(args.folder, args.text, args.reidx, args.parent, args.N)


# python local_embedding_training.py -folder ../data/cluster -text ../data/paper_phrases.txt.frequent.hardcode -reidx ../data/reidx.txt -parent \* -N 100

