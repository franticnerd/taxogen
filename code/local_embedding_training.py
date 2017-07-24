#!/usr/bin/env
import argparse
import subprocess
import utils
import os


def read_files(folder, parent):
    print parent
    emb_file = '%s/embeddings.txt' % folder
    hier_file = '%s/hierarchy.txt' % folder
    keyword_file = '%s/keywords.txt' % folder

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
        # cate_ph = cate[2:]
        cate_ph = cate

        for ph in embs:
            sim = utils.cossim(embs[cate_ph], embs[ph])
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

def revevant_docs(text, reidx, cates):
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
        output_f = '%s/embeddings.txt' % sub_folder
        if not os.path.exists(sub_folder):
            os.makedirs(sub_folder)
        with open(input_f, 'w+') as g:
            for d in c_docs:
                g.write(docs[d])

        print 'starting calling word2vec'
        print input_f
        print output_f
        embed_proc = subprocess.Popen(["./word2vec", "-threads", "20", "-train", input_f, "-output", output_f], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        embed_proc.wait()
        print 'done training word2vec'
        # subprocess.call(["./word2vec", "-threads", "10", "-train", input_f, "-output", output_f], stdout=subprocess.PIPE)


def main_local_embedding(folder, doc_file, reidx, parent, N):
    embs, keywords, cates = read_files(folder, parent)
    cates = relevant_phs(embs, cates, int(N))
    pd_map, docs = revevant_docs(doc_file, reidx, cates)
    run_word2vec(pd_map, docs, cates, folder)


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

