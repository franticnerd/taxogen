import argparse
import utils
import operator
import Queue
import math
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from case_ranker import read_caseolap_result, rank_phrase

ph_idf = None
doc_to_ph = None

def parse_reidx(reidx_f):
	global ph_idf
	global doc_to_ph
	ph_idf = {}
	pd_map = {}
	doc_to_ph = {}

	with open(reidx_f) as f:
		for line in f:
			segments = line.strip('\r\n').split('\t')
			doc_ids = segments[1].split(',')
			if len(doc_ids) > 0 and doc_ids[0] == '':
				pd_map[segments[0]] = set()
				continue
				# print line
			pd_map[segments[0]] = set([int(x) for x in doc_ids])
			ph_idf[segments[0]] = 0
			for x in doc_ids:
				if x not in doc_to_ph:
					doc_to_ph[x] = []
				doc_to_ph[x].append(segments[0])

	d_cnt = len(doc_to_ph)
	for ph in pd_map:
		if len(pd_map[ph]) > 0:
			ph_idf[ph] = math.log(float(d_cnt) / len(pd_map[ph]))

	print 'Inverted Index file read.'



def get_rep(folder, c_id, N):
	print('Start get representative phrases for %s, %s ========================' % (folder, c_id))
	# print folder
	par_folder = dirname(folder)
	cur_label = basename(folder)

	result_phrases = [cur_label]	

	ph_f = '%s/caseolap.txt' % par_folder
	if exists(ph_f):
		kw_clus_f = '%s/cluster_keywords.txt' % par_folder
		kws = set()
		with open(kw_clus_f) as f:
			for line in f:
				clus_id, ph = line.strip('\r\n').split('\t')
				if clus_id == c_id:
					kws.add(ph)
		emb_f = '%s/embeddings.txt' % par_folder
		embs = utils.load_embeddings(emb_f)

		# print len(kws)
		phrase_map_p, cell_map_p, tmp = read_caseolap_result(ph_f)
		parent_dist_ranking = cell_map_p[c_id]

		ph_scores = {} 
		for (ph, score) in parent_dist_ranking:
			if ph not in kws:
				continue
			emb_dist = utils.cossim(embs[ph], embs[cur_label])
			ph_scores[ph] = score * emb_dist

		ph_scores = sorted(ph_scores.items(), key=operator.itemgetter(1), reverse=True)

		for (ph, score) in ph_scores:
			if ph not in result_phrases and ph in kws:
				result_phrases.append(ph)
			if len(result_phrases) >= N:
				break
		
	elif ph_idf == None:
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
	else:
		# Using TF-IDF to generate
		print 'looking at tf-idf for %s' % folder
		d_clus_f = '%s/paper_cluster.txt' % par_folder
		kw_clus_f = '%s/cluster_keywords.txt' % par_folder
		docs = []
		kws = set()
		with open(d_clus_f) as f:
			for line in f:
				doc_id, clus_id = line.strip('\r\n').split('\t')
				if clus_id == c_id:
					docs.append(doc_id)
		with open(kw_clus_f) as f:
			for line in f:
				clus_id, ph = line.strip('\r\n').split('\t')
				if clus_id == c_id:
					kws.add(ph)
		ph_scores = {x:0 for x in ph_idf}
		for d in docs:
			if d in doc_to_ph:
				for ph in doc_to_ph[d]:
					ph_scores[ph] += 1
		
		for ph in ph_scores:
			if ph_scores[ph] == 0:
				continue
			if ph not in kws:
				ph_scores[ph] = 0
				continue
			ph_scores[ph] = 1 + math.log(ph_scores[ph])
			ph_scores[ph] *= ph_idf[ph]
		ph_scores = sorted(ph_scores.items(), key=operator.itemgetter(1), reverse=True)

		for (ph, score) in ph_scores:
			if ph not in result_phrases:
				result_phrases.append(ph)
			if len(result_phrases) > N:
				break
	
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
  # python compress.py -root ../data/dblp/our-l3-0.15 -output ../data/dblp/taxonomies/l3-our-0.15.txt
	parser = argparse.ArgumentParser(prog='compress.py', \
			description='')
	parser.add_argument('-root', required=True, \
			help='root of data files.')
	parser.add_argument('-output', required=True, \
			help='output file name.')
	parser.add_argument('-reidx', required=False, \
			help='reindex_file.')
	parser.add_argument('-N', required=False, \
			help='number of phrases included.')
	args = parser.parse_args()


	N = 10
	if args.N is not None:
		N = int(args.N)

	if args.reidx is not None:
		parse_reidx(args.reidx)

	recursion(args.root, args.output, N)


