import numpy as np
from os import listdir
from os.path import isfile, join
import operator
import utils


def get_candidates(folder, o_file):

	files = ['%s%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f))]
	quality_phrases = set()

	for file in files:
		with open(file) as f:
			for line in f:
				phrase = line.split(' ')[0]
				quality_phrases.add(phrase)

	print 'Quality phrase count: ' + str(len(quality_phrases))

	with open(o_file, 'w+') as g:
		for phrase in quality_phrases:
			g.write('%s\n' % phrase)

def read_caseolap_result(case_file):
	phrase_map = {}

	cell_cnt = 0
	with open(case_file) as f:
		for line in f:
			cell_cnt += 1
			segments = line.strip('\r\n ').split('\t')
			cell_id, phs_str = segments[0], segments[1][1:-1]
			segments = phs_str.split(', ')
			for ph_score in segments:
				parts = ph_score.split('|')
				ph, score = parts[0], float(parts[1])
				if ph not in phrase_map:
					phrase_map[ph] = {}
				phrase_map[ph][cell_id] = score

	return phrase_map, cell_cnt


def rank_phrase(case_file, o_file):

	ph_dist_map = {}

	phrase_map, cell_cnt = read_caseolap_result(case_file)

	unif = [1.0 / cell_cnt] * cell_cnt

	for ph in phrase_map:
		ph_vec = [x[1] for x in phrase_map[ph].iteritems()]
		if len(ph_vec) < cell_cnt:
			ph_vec += [0] * (cell_cnt - len(ph_vec))
		ph_vec = utils.l1_normalize(ph_vec)
		ph_dist_map[ph] = utils.kl_divergence(ph_vec, unif)

	ranked_list = sorted(ph_dist_map.items(), key=operator.itemgetter(1), reverse=True)
	with open(o_file, 'w+') as g:
		for ph in ranked_list:
			g.write('%s\t%f\n' % (ph[0], ph[1]))


# folder = '../data/leef/query_relevant/'
# o_file = '../data/candidates.txt'

# get_candidates(folder, o_file)

case_file = '../data/cluster/caseolap.txt'
o_file = '../data/cluster/ph_dist_ranking.txt'
rank_phrase(case_file, o_file)






