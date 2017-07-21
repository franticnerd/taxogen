#!/usr/bin/env
import argparse
import subprocess
import utils
import os


def read_files(folder, parent):
    print parent
    emb_file = '%s/embedding.txt' % folder
    hier_file = '%s/hierarchy-final.txt' % folder
    keyword_file = '%s/keywords-final.txt' % folder

    embs = utils.load_embeddings(emb_file)
    keywords = set()
    cates = {}

    with open(keyword_file) as f:
        for line in f:
            keywords.add(line.strip('\r\n'))

    tmp_embs = {}
    for k in keywords:
        tmp_embs[k] = embs[k]
    embs = tmp_embs

    with open(hier_file) as f:
        for line in f:
            segs = line.strip('\r\n').split(' ')
            if segs[1] == parent:
                cates[segs[0]] = set()

    print 'Embedding, hierarchy and keywords read done.'

    return embs, keywords, cates

def relevant_phs(embs, cates, N):

    for cate in cates:
        worst = -100
        bestw = [-100] * (N + 1)
        bestp = [''] * (N + 1)

        for ph in embs:
            sim = utils.cossim(embs[cate], embs[ph])
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

    print 'Top similar phrases found.'

    return cates

def revevant_docs(text, cates):
    docs = {}
    idx = 0
    pd_map = {}
    for cate in cates:
        for ph in cates[cate]:
            pd_map[ph] = set()

    with open(text) as f:
        for line in f:
            docs[idx] = line
            for ph in pd_map:
                if ph in line:
                    pd_map[ph].add(idx)
            idx += 1

    print 'Relevant docs found.'

    return pd_map, docs


def run_word2vec(pd_map, docs, cates, folder):

    for cate in cates:

        c_docs = set()
        for ph in cates[cate]:
            c_docs = c_docs.union(pd_map[ph])

        print 'Starting cell %s with %d docs.' % (cate, len(c_docs))
        
        # save file
        sub_folder = '%s/%s' % (folder, cate)
        input_f = '%s/text' % sub_folder
        output_f = '%s/embedding.txt' % sub_folder
        os.makedirs(sub_folder)
        with open(input_f, 'w+') as g:
            for d in c_docs:
                g.write(docs[d])

        subprocess.Popen(["./word2vec", "-train", input_f, "-output", output_f], stdout=subprocess.PIPE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='local_embedding_training.py', \
            description='Train Embeddings for each query.')
    parser.add_argument('-folder', required=True, \
            help='The folder of previous level.')
    parser.add_argument('-text', required=True, \
            help='The raw text file.')
    parser.add_argument('-parent', required=True, \
            help='the target expanded phrase')
    parser.add_argument('-N', required=True, \
            help='The number of neighbor used to extract documents')
    args = parser.parse_args()
     
    embs, keywords, cates = read_files(args.folder, args.parent)
    cates = relevant_phs(embs, cates, int(args.N))
    pd_map, docs = revevant_docs(args.text, cates)
    run_word2vec(pd_map, docs, cates, args.folder)

# python local_embedding_training.py -folder ../data/cluster -text ../data/paper_phrases.txt.frequent.hardcode -parent * -N 100

