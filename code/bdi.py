import numpy as np
from os import listdir
from collections import defaultdict
import utils
import Queue
import argparse
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists


def get_clus_keywords(clus_kws_f):
    clus_map = {}
    with open(clus_kws_f) as f:
        for line in f:
            clus_id, ph = line.strip('\r\n').split('\t')
            clus_id = int(clus_id)
            if clus_id not in clus_map:
                clus_map[clus_id] = set()
            clus_map[clus_id].add(ph)
    return clus_map


def compute_dbi(embs, clus_map, center_map):

    n_clus = len(center_map)

    c_centers = {}
    for c_center in center_map:
        cid = center_map[c_center]
        c_centers[int(cid)] = embs[c_center]

    M = [[0 for x in range(n_clus)] for y in range(n_clus)]
    R = [[0 for x in range(n_clus)] for y in range(n_clus)]
    S = [0 for x in range(n_clus)]
    D = [0 for x in range(n_clus)]

    for i in range(n_clus):
        c_embs = [embs[x] for x in clus_map[i]]
        S[i] = utils.euclidean_cluster(c_embs, c_centers[i])

    for i in range(n_clus):
        for j in range(n_clus):
            if i != j:
                M[i][j] = utils.euclidean_distance(c_centers[i], c_centers[j])
                R[i][j] = (S[i] + S[j]) / M[i][j]

    for i in range(n_clus):
        for j in range(n_clus):
            if i != j and R[i][j] > D[i]:
                D[i] = R[i][j]

    return sum(D) / len(D)


def output_dbi(dbi_scores):

    dbi_by_lvl = {}
    all_dbi = [x[0] for x in dbi_scores.values()]

    print 'Average DBI for all is: %f' % (sum(all_dbi) / len(all_dbi))

    for x in dbi_scores.values():
        if x[1] not in dbi_by_lvl:
            dbi_by_lvl[x[1]] = []
        dbi_by_lvl[x[1]].append(x[0])

    for lvl in dbi_by_lvl:
        dbis = dbi_by_lvl[lvl]
        print 'Average DBI for level %d is: %f' % (lvl, sum(dbis) / len(dbis))


def recursion(root, lvl):

    q = Queue.Queue()
    q.put((root, -1, 1, '*'))

    dbi_scores = {}

    while not q.empty():

        (c_folder, c_id, level, c_name) = q.get()

        if level >= lvl:
            continue
        
        hier_f = '%s/hierarchy.txt' % c_folder
        clus_kws_f = '%s/cluster_keywords.txt' % c_folder
        emb_f = '%s/embeddings.txt' % c_folder
        if not exists(hier_f):
            continue

        hier_map = utils.load_hier_f(hier_f)
        clus_map = get_clus_keywords(clus_kws_f)
        embs = utils.load_embeddings(emb_f)

        for cluster in hier_map:
            cc_id = hier_map[cluster]
            cluster_folder = '%s/%s' % (c_folder, cluster)
            cluster_namespace = '%s/%s' % (c_name, cluster)
            q.put((cluster_folder, cc_id, level+1, cluster_namespace))

        
        # handle current
        dbi = compute_dbi(embs, clus_map, hier_map)
        print 'Computing DBI for %s: %f' % (c_name, dbi)
        dbi_scores[c_name] = (dbi, level)
    output_dbi(dbi_scores)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='redundancy_bdi.py', \
            description='')
    parser.add_argument('-root', required=True, \
            help='root of data files.')
    parser.add_argument('-lvl', required=True, \
            help='')
    args = parser.parse_args()

    recursion(args.root, args.lvl)
