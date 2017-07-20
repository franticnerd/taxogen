import argparse
import utils
import operator


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


def rank_phrase(case_file, o_file, thres):

	ph_dist_map = {}
	smoothing_factor = 0.0

	phrase_map, cell_cnt = read_caseolap_result(case_file)

	unif = [1.0 / cell_cnt] * cell_cnt

	for ph in phrase_map:
		ph_vec = [x[1] for x in phrase_map[ph].iteritems()]
		if len(ph_vec) < cell_cnt:
			ph_vec += [0] * (cell_cnt - len(ph_vec))
		# smoothing
		ph_vec = [x + smoothing_factor for x in ph_vec]
		ph_vec = utils.l1_normalize(ph_vec)
		ph_dist_map[ph] = utils.kl_divergence(ph_vec, unif)

	ranked_list = sorted(ph_dist_map.items(), key=operator.itemgetter(1), reverse=True)
	with open(o_file, 'w+') as g:
		for ph in ranked_list:
			if ph[1] > thres:
				g.write('%s\n' % (ph[0]))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='case_ranker.py', \
			description='Ranks the distinctiveness score using caseolap result.')
	parser.add_argument('-input', required=True, \
			help='The files used.')
	parser.add_argument('-thres', required=True, \
			help='The files used.')
	parser.add_argument('-output', required=True, \
			help='The output result file')
	args = parser.parse_args()

	rank_phrase(args.input, args.output, float(args.thres))
