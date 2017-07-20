#-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.
#
# File Name : local_embedding_training.py
#
# Purpose : Train local embeddings based on the relevant queries 
#
# Creation Date : 17-03-2017
#
# Last Modified : Fri 17 Mar 2017 08:03:32 PM CDT
#
# Created By : Huan Gui (huangui2@illinois.edu) 
#
#_._._._._._._._._._._._._._._._._._._._._.

import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='local_embedding_training.py', \
            description='Train Embeddings for each query.')
    parser.add_argument('-input', required=True, \
            help='The folder of input text folder.') 
    parser.add_argument('-query', required=True, \
            help='The input query file') 
    args = parser.parse_args()
     
    data = open(args.query)
    for line in data:
        query = line.split("\n")[0].replace("#", "_")
        text = "%s/%s/text" % (args.input, query)
        output = "%s/%s/term.embeddings" %  (args.input, query)
        subprocess.Popen(["./word2vec", "-train", text, "-output", output], stdout=subprocess.PIPE) 


