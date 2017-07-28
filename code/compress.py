import argparse
import utils
import operator
import Queue
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from case_ranker import read_caseolap_result, rank_phrase

def get_rep(folder, c_id, N):
	print 'Start get representative phrases for %s, %s ========================' % (folder, c_id)
	# print folder
	par_folder = dirname(folder)
	cur_label = basename(folder)

	result_phrases = [cur_label]

	ph_f = '%s/caseolap.txt' % par_folder
	if exists(ph_f):
		phrase_map_p, cell_map_p, tmp = read_caseolap_result(ph_f)
		parent_dist_ranking = cell_map_p[c_id]

		for (ph, score) in parent_dist_ranking:
			if ph not in result_phrases:
				result_phrases.append(ph)
			if len(result_phrases) >= N:
				break

	else:
		print 'looking at embeddings for %s' % folder

		ph_f = '%s/embeddings.txt' % par_folder
		kw_f = '%s/keywords.txt' % par_folder
		keywords = set()
		with open(kw_f) as f:
			for line in f:
				keywords.add(line.strip('\r\n'))

		embs = utils.load_embeddings(ph_f)
		tmp_embs = {}
		for k in keywords:
			if k in embs:
				tmp_embs[k] = embs[k]
		embs = tmp_embs

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
		
		for ph in bestp[:N]:
			if ph not in result_phrases:
				result_phrases.append(ph)
	
	#print result_phrases
	return result_phrases

def recursion(root, o_file, N):

	q = Queue.Queue()
	q.put((root, -1, '*'))

	g = open(o_file, 'w+')

	while not q.empty():
		(c_folder, c_id, c_name) = q.get()
		
		hier_f = '%s/hierarchy.txt' % c_folder
		if not exists(hier_f):
			continue

		hier_map = utils.load_hier_f(hier_f)

		for cluster in hier_map:
			cc_id = hier_map[cluster]
			cluster_folder = '%s/%s' % (c_folder, cluster)
			cluster_namespace = '%s/%s' % (c_name, cluster)
			q.put((cluster_folder, cc_id, cluster_namespace))

		# handle current
		if c_folder != root:
			phs = get_rep(c_folder, str(c_id), N)
			phs_str = ','.join(phs)
			g.write('%s\t%s\n' % (c_name, phs_str))

	g.close()


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='compress.py', \
			description='')
	parser.add_argument('-root', required=True, \
			help='root of data files.')
	parser.add_argument('-output', required=True, \
			help='output file name.')
	parser.add_argument('-N', required=False, \
			help='number of phrases included.')
	args = parser.parse_args()

	N = 10
	if args.N is not None:
		N = int(args.N)

	recursion(args.root, args.output, N)
