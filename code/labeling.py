import argparse
import utils
import operator
import Queue
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename
from case_ranker import read_caseolap_result, rank_phrase

def label(folder):
	# print folder
	par_folder = dirname(folder)
	cur_label = basename(folder)
	p_case_f = '%s/caseolap.txt' % par_folder
	c_case_f = '%s/caseolap.txt' % folder

	
	phrase_map_p, cell_map_p, tmp = read_caseolap_result(p_case_f)
	ranked_phrases = rank_phrase(p_case_c)
	desc_ps = {ph:dist for (ph, dist) in ranked_phrases}
	min_score = 0.15
	label_cands = {}

	for (ph, score) in cell_map_p[cur_label]:
		spread_factor = 0
		if ph not in desc_ps:
			spread_factor = 1.0 / min_score
		else:
			spread_factor = 1.0 / desc_ps[ph]

		label_cands[ph] = score * spread_factor

	ranked_list = sorted(label_cands.items(), key=operator.itemgetter(1), reverse=True)

	return ranked_list[0][0]


def recursion(root):

	q = Queue.Queue()
	q.put(root)

	while not q.empty():
		c_folder = q.get()
		# expand children
		children_fs = ['%s/%s' % (c_folder, f) for f in listdir(c_folder) if isdir(join(c_folder, f))]
		for child in children_fs:
			q.put(child)

		# handle current
		if c_folder != root:
			l = label(c_folder)
			print 'label for %s is: %s' % (c_folder, l)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='labeling.py', \
			description='')
	parser.add_argument('-root', required=True, \
			help='root of data files.')
	args = parser.parse_args()

	recursion(args.root)
