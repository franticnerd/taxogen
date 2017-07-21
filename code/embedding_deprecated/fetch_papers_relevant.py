#-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
# File Name : fetch_papers_relevant.py
#
# Purpose : Fetch papers that are relevant to the queries
#
# Creation Date : 17-03-2017
#
# Last Modified : Sat 18 Mar 2017 09:37:49 PM CDT
#
# Created By : Huan Gui (huangui2@illinois.edu) 
#
#_._._._._._._._._._._._._._._._._._._._._.

import argparse
import os
import copy 

from numpy import linalg as LA
import numpy as np

def fetch_paper(thread, N, term, relevant_dict, tp_map):
    targets, target_set = [term], set([term])
    for i in xrange(N):
        q, s = relevant_dict[term][i][0], relevant_dict[term][i][1]
        if s > thread and q not in target_set:
            targets.append(q)
            target_set.add(q)
    paper_set = set()
    print "Query :", term, len(targets), "---"
    for t in targets:
        if t not in tp_map:
            print "(%s)" % t,
            continue
        paper_set = paper_set | tp_map[t]
        print "(%s, %d) " % (t, len(paper_set)), 
    return paper_set
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='fetch_papers_relevant.py', \
            description='Find papers relevant to the query.')
    parser.add_argument('-input', required=True, \
            help='The input folder.') 
    parser.add_argument('-relevant', required=True, \
            help='The folder for relevant queries.') 
    parser.add_argument('-output', required=True, \
            help='The output folder.') 
    parser.add_argument('-text', required=True, \
            help='The text data.') 
    parser.add_argument('-query', required=True, \
            help='The input query file') 
    parser.add_argument('-threshold', required=True, \
            help='The minimal score to be relevant') 
    parser.add_argument('-N', required=True, \
            help='The number of relevant queries') 
    args = parser.parse_args()
    
    threshold = float(args.threshold)
    N = int(args.N)
    
    query_terms = []
    data = open(args.query)
    for line in data:
        queries = line.strip().split("#")
        for term in queries:
            query_terms.append(term)
        
    relevant_dict = dict()
    all_terms = set(query_terms)
    
    for term in query_terms:
        relevant_dict[term] = []
        print "%s/%s" % (args.relevant, term)
        data = open("%s/%s" % (args.relevant, term))
        print term 
        for line in data:
            values = line.strip().split()
            relevant_dict[term].append((values[0], float(values[1])))
            print values[0],  
            all_terms.add(values[0])
        print "\n" 
        
    # read paper-term 
    term_paper_map = dict()
    data = open("%s/paper_term.net" % args.input)
    #data = open("./paper_term.net")
    for line in data:
        value = line.split()
        term, paper = value[1], int(value[0])
        if term not in all_terms:
            continue
        if term not in term_paper_map:
            term_paper_map[term] = set()
        term_paper_map[term].add(paper)
    print "Finish reading paper_term.net"

    data = open(args.query)
    for line in data:
        queries = line.strip().split("#")
        paper_set = None 
        for i in xrange(len(queries)):
            if i == 0:
                paper_set = fetch_paper(threshold, N,
                        queries[i], relevant_dict, term_paper_map)
            else:
                paper_set = paper_set | fetch_paper(threshold, N, 
                        queries[i], relevant_dict, term_paper_map)
            
            print "For query :", queries[i],
            print "Before :", len(term_paper_map[queries[i]]),        
            print "After :", len(paper_set)
        
        
        path = "%s/%s" % (args.output, "_".join(queries))
        if not os.path.isdir(path):
            os.system("mkdir %s/%s" % (args.output, "_".join(queries)))
        fout = open("%s/%s/text" % (args.output, "_".join(queries)), "w")
        fout_2 = open("%s/%s/pid_text" % (args.output, "_".join(queries)), "w")
        data = open(args.text)
        index = 0
        for line in data:
            if index in paper_set:
                fout.write(line)
                fout_2.write("%d\t%s\n" % (index, line))
            index += 1
        fout.close()
        fout_2.close()
