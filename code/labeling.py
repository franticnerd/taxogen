import argparse
import utils
import operator
import Queue
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename
from case_ranker import read_caseolap_result, rank_phrase

def label(folder, c_id):
	print 'Start labeling for %s, %s ========================' % (folder, c_id)
	# print folder
	par_folder = dirname(folder)
	cur_label = basename(folder)
	p_case_f = '%s/caseolap.txt' % par_folder
	c_case_f = '%s/caseolap.txt' % folder
	emb_f = '%s/embeddings.txt' % par_folder

	# generate word2vec phrases
	embs = utils.load_embeddings(emb_f)
	if cur_label not in embs:
		print 'Error!!!'
		exit(1)
	N = 30
	worst = -100
	bestw = [-100] * (N + 1)
	bestp = [''] * (N + 1)

	for ph in embs:
		sim = utils.cossim(embs[cur_label], embs[ph])
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
	cands = {x:bestw[idx] for idx, x in enumerate(bestp)}

	phrase_map_p, cell_map_p, tmp = read_caseolap_result(p_case_f)
	parent_dist_ranking = cell_map_p[c_id]
	parent_dist_map = {ph:float(dist) for (ph, dist) in parent_dist_ranking}
	child_kl_ranking = rank_phrase(c_case_f)
	child_kl_map = {ph:dist for (ph, dist) in child_kl_ranking}
	min_score = 0.12
	label_cands = {}

	# for (ph, score) in parent_dist_ranking:
	for (ph, score) in cands.items():
		if ph not in parent_dist_map:
			continue

		spread_factor = 0
		if ph not in child_kl_map:
			spread_factor = 1.0 / min_score
		else:
			spread_factor = 1.0 / child_kl_map[ph]
			# spread_factor = 0.01

		label_cands[ph] = score * spread_factor * parent_dist_map[ph]
		# label_cands[ph] = score * parent_dist_map[ph]

	ranked_list = sorted(label_cands.items(), key=operator.itemgetter(1), reverse=True)
	print ranked_list

	return ranked_list[0][0]


def recursion(root):

	q = Queue.Queue()
	q.put((root, -1))

	label_map = {}

	try:
		while not q.empty():
			(c_folder, c_id) = q.get()
			hier_map = utils.load_hier_f('%s/hierarchy.txt' % c_folder)

			for cluster in hier_map:
				cc_id = hier_map[cluster]
				cluster_folder = '%s/%s' % (c_folder, cluster)
				q.put((cluster_folder, cc_id))

			# handle current
			if c_folder != root:
				l = label(c_folder, str(c_id))
				cur_label = basename(c_folder)
				label_map[cur_label] = l
				print 'label for %s is: %s\n' % (c_folder, l)
	except:
		for (o_l, l) in label_map.items():
			print '%s ==> %s' % (o_l, l)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='labeling.py', \
			description='')
	parser.add_argument('-root', required=True, \
			help='root of data files.')
	args = parser.parse_args()

	recursion(args.root)
