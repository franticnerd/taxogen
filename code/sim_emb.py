import argparse
import utils
import operator
import Queue
import math
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from case_ranker import read_caseolap_result, rank_phrase


def load_embeddings(embedding_file):
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

def compare(a_f, b_f):

	emb_f = 'embeddings.txt'
	a_emb_f = '%s/%s' % (a_f, emb_f)
	b_emb_f = '%s/%s' % (b_f, emb_f)

	if not exists(a_emb_f) or not exists(b_emb_f):
		print 'Embedding file not found'
		exit(1)

	embs_a = load_embeddings(a_emb_f)
	embs_b = load_embeddings(b_emb_f)

	embs_groups = [embs_a, embs_b]

	while 1:
		n_name = raw_input("Enter your node: ")
		if n_name not in embs_a or n_name not in embs_b:
			print '%s not found' % n_name

		for embs in embs_groups:
			t_emb = embs[n_name]
			sim_map = {}
			for key in embs:
				sim_map[key] = utils.cossim(t_emb, embs[key])
			
			sim_map = sorted(sim_map.items(), key=operator.itemgetter(1), reverse=True)
			print sim_map[:10]
			print 'group finished\n'



if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='sim_emb.py', \
			description='')
	parser.add_argument('-a', required=True, \
			help='root of data files.')
	parser.add_argument('-b', required=True, \
			help='root of data files.')
	args = parser.parse_args()

	compare(args.a, args.b)