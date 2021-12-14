#-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
# File Name : metrics.py
#
# Purpose : Given a query and a rank list, return the following metrics 
#           1) P@5, P@10, P@20
#           2) Mean Average Precision (MAP)
#           3) bpref
#           4) Mean Reciprocal Rank (MRR)
#
# Creation Date : 12-01-2017
#
# Last Modified : Wed 19 Apr 2017 01:52:34 PM CDT
#
# Created By : Huan Gui (huangui2@illinois.edu) 
#
#_._._._._._._._._._._._._._._._._._._._._.

import argparse 
import numpy as np
from math import log

# candidates as (ordered) lists
# ground_truth as (unordered) set
# calculates precision @ 5, 10, 20
def precision(candidates, ground_truth):
    R = len(ground_truth)
    C = len(ground_truth)

    p_5, p_10, p_20 = 0, 0, 0
    true_positive = 0
    for i in range(5):
        if i < len(candidates) and candidates[i] in ground_truth:
            true_positive += 1
    p_5 = float(true_positive) / 5.0

    for i in range(5, 10):
        if i < len(candidates) and candidates[i] in ground_truth:
            true_positive += 1
    p_10 = float(true_positive) / 10.0

    for i in range(10, 20):
        if i < len(candidates) and candidates[i] in ground_truth:
            true_positive += 1
    p_20 = float(true_positive) / 20.0

    true_positive = 0
    for i in range(min(R, C)):
        if i < len(candidates) and candidates[i] in ground_truth:
            true_positive += 1
            
    p_R = float(true_positive) / float(R) 

    return p_5, p_10, p_20, p_R

# set N = R when calculating MAP
def MAP(candidates, ground_truth):
    C = len(candidates)
    R = len(ground_truth)
    true_positive, precision, total_precision = 0, 0, 0
    for n in range(1, min(C, R) + 1):
        if candidates[n - 1] in ground_truth:
            true_positive += 1
            precision = float(true_positive) / float(n)
            total_precision += precision
    return float(total_precision) / float(R)

def RR(candidates, ground_truth):
    result = 0
    nCandidates = len(candidates)
    for n in range(nCandidates):
        if candidates[n] in ground_truth:
            result = n + 1
            break 
    return 0 if result == 0 else 1.0 / float(result)

def NDCG(candidates, ground_truth, K = 20):
    DCG, IDCG = 0, 0
    ndcg_5, ndcg_10, ndcg_20 = 0, 0, 0
    for i in range(K):
        x = 1.0 / log(i + 2, 2)
        IDCG += x
        if i < len(candidates) and candidates[i] in ground_truth:
            DCG += x
        if i == 4:
            ndcg_5 = DCG / IDCG
        elif i == 9:
            ndcg_10 = DCG / IDCG
        elif i == 19:
            ndcg_20 = DCG / IDCG
    return ndcg_5, ndcg_10, ndcg_20

def bpref(candidates, ground_truth):
    R = len(candidates)
    false_positive, bpref, k = 0, 0, 0
    for n in range(R):
        if candidates[n] not in ground_truth:
            false_positive += 1
        else:
            bpref += 1 - float(false_positive) / R
            k += 1
            if k == 200:
                break
    return bpref / float(k)

def printResults(name, result):
    print(name, end=' ')
    print("%.4f" % (np.mean(result)), end=' ')
    for res in result:
        print("%.4f" % res, end=' ')
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='metrics.py', \
            description='Calculate the metrics.')
    parser.add_argument('-input', '--input', required=True, \
            help='Input folder of retrieved experts for all queries.') 
    parser.add_argument('-query', '--query', required=True, \
            help='The label of experts.') 
    parser.add_argument('-label', '--label', required=True, \
            help='The label of experts.') 
    args = vars(parser.parse_args())

    ground_truth_folder = args['label']
    
    input_folder = args['input']

    queries = []
    query_file = args['query']
    query_data = open(query_file) 
    for line in query_data:
        query = line.split("\n")[0].replace(" ", "_")
        queries.append(query)
    print("measure overall", " ".join(queries))
    
    Precision_5, Precision_10, Precision_20, Precision_R, l_MAP, l_MRR, l_bpref = \
            list([[] for i in range(7)])
    NDCG_5, NDCG_10, NDCG_20 = list([[] for i in range(3)])

    for query in queries:
        candidate_file = input_folder + "/" + query + "/author.weights"
        
        scores = dict() 
        data = open(candidate_file) 
        for line in data:
            value = line.split("\n")[0].split()
            scores[value[0]] = float(value[1])
        scores = sorted(list(scores.items()), key=lambda x:x[1], reverse=True)

        candidates = [x[0] for x in scores]
        
        expert_file = ground_truth_folder + "/" + query + ".experts"
        experts = set() 
        
        data = open(expert_file)
        for line in data:
            value = line.split("\n")[0]
            experts.add(value)
            
        p_5, p_10, p_20, p_R = precision(candidates, experts)
        ndcg_5, ndcg_10, ndcg_20 = NDCG(candidates, experts)
        r_map = MAP(candidates, experts) 
        r_rr = RR(candidates, experts)
        r_bpref = bpref(candidates, experts)

        Precision_5.append(p_5)
        Precision_10.append(p_10)
        Precision_20.append(p_20)
        Precision_R.append(p_R)
        l_MAP.append(r_map)
        l_MRR.append(r_rr)
        l_bpref.append(r_bpref)
        NDCG_5.append(ndcg_5)
        NDCG_10.append(ndcg_10)
        NDCG_20.append(ndcg_20)
        
    printResults("Precision@5", Precision_5)
    printResults("Precision@10", Precision_10)
    printResults("Precision@20", Precision_20)
    printResults("NDCG@5", NDCG_5)
    printResults("NDCG@10", NDCG_10)
    printResults("NDCG@20", NDCG_20)
    printResults("MAP", l_MAP)
    printResults("MRR", l_MRR)
    printResults("bpref", l_bpref)
