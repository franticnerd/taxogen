from heapq import heappush, heappop, heappushpop, nsmallest, nlargest
import codecs
import math
import ast
import argparse
import copy


class CaseSlim:

	def bm25_df_paper(self, df, max_df, tf, dl, avgdl, k=1.2, b=0.5, multiplier=3):
		score = tf * (k + 1) / (tf + k * (1 - b + b * (dl / avgdl)))
		df_factor = math.log(1 + df, 2) / math.log(1 + max_df, 2)
		score *= df_factor
		score *= multiplier
		return score


	def softmax_paper(self, score_list):
		# normalization of exp
		exp_sum = 1
		for score in score_list:
			exp_sum += math.exp(score)

		exp_list = []
		for score in score_list:
			normal_value = math.exp(score) / exp_sum
			exp_list.append(normal_value)
		return exp_list


	def compute(self, score_type='ALL'):
		'''
		-- score_type --
			ALL: all three factors
			POP: only popularity
			DIS: only distinctive
			INT: only integrity
			NOPOP: no populairty
			NODIS: no distinctive
			NOINT: no integrity
		'''
		scores = {}
		multiplier = 1

		
		sum_self = self.sum_cnt
		num_context_cells = len(self.sum_cnt_context) + 1
		total_sum = sum(self.sum_cnt_context.values()) + sum_self
		avgdl = total_sum / float(num_context_cells)

		# method 1
		for phrase in self.phrase_cnt:
			lower_phrase = phrase.lower()
			score = 1
			nor_phrase = self.normalize(lower_phrase)
			self_cnt = self.phrase_cnt[phrase]
			self_df = self.phrase_df[phrase]
			
			group = [(self_df, self.max_df, self_cnt, sum_self)]

			self.context_groups[phrase] = []
			for phrase_group, phrase_values in self.phrase_cnt_context.items():
				context_df = self.phrase_df_context[phrase_group].get(phrase, 0)
				sum_context = self.sum_cnt_context[phrase_group]
				context_cnt = phrase_values.get(phrase, 0)
				maxdf_context = self.max_df_context[phrase_group]

				if (context_cnt > 0):
					group.append((context_df, maxdf_context, context_cnt, sum_context))
					self.context_groups[phrase].append((context_df, maxdf_context, context_cnt, sum_context))
				
			score_list = []
			for record in group:
				score_list.append(self.bm25_df_paper(record[0], record[1], record[2], record[3], avgdl))
			distinct = self.softmax_paper(score_list)[0]
			
			# score_list = map(prettyfloat, score_list)
			# log_str = lower_phrase.encode('utf-8') + ':' + str(prettyfloat(score)) + '\t' +  str(group) +  '\t' + str(score_list) + '\n'
			# log_strs[lower_phrase] = log_str
			# log_scores[lower_phrase] = score
			# distinct = score
			popularity = math.log(1 + self_df, 2)
			try:
				integrity = float(self.global_scores[nor_phrase])
			except:
				integrity = 0.8

			if score_type == 'ALL':
				score = distinct * popularity * integrity
			elif score_type == 'POP':
				score = popularity
			elif score_type == 'DIS':
				score = distinct
			elif score_type == 'INT':
				score = integrity
			elif score_type == 'NOPOP':
				score = distinct * integrity
			elif score_type == 'NODIS':
				score = popularity * integrity
			elif score_type == 'NOINT':
				score = popularity * distinct
			else:
				score = 0

			scores[phrase] = score

		ranked_list = [(phrase, scores[phrase]) for phrase in sorted(scores, key=scores.get, reverse=True)]
		
		# print 'OLAPORP DONE'
		return ranked_list


	def agg_phrase_cnt_df(self, freq_data, selected_docs = None):
		phrase_cnt = {}
		phrase_df = {}

		if selected_docs == None:
			for doc_index in freq_data:
				for phrase in freq_data[doc_index]:
					if phrase not in phrase_cnt:
						phrase_cnt[phrase] = 0
					phrase_cnt[phrase] += freq_data[doc_index][phrase]
		else:
			for doc_index in selected_docs:
				for phrase in freq_data.get(doc_index, {}):
					if phrase not in phrase_cnt:
						phrase_cnt[phrase] = 0
					if phrase not in phrase_df:
						phrase_df[phrase] = 0
					phrase_cnt[phrase] += freq_data[doc_index][phrase]
					phrase_df[phrase] += 1

		return phrase_cnt, phrase_df


	def normalize(self, word):
		word = word.lower()
		result = []
		for i in xrange(len(word)):
			if word[i].isalpha() or word[i] == '\'':
				result.append(word[i])
			else:
				result.append(' ')
		word = ''.join(result);
		return ' '.join(word.split())


	def __init__(self, freq_data, selected_docs, context_doc_groups, global_scores=None):
		# print 'handle slim version'
		self.phrase_cnt, self.phrase_df = self.agg_phrase_cnt_df(freq_data, selected_docs)
		self.phrase_cnt_context = {}
		self.phrase_df_context = {}
		if len(self.phrase_df) > 0:
			self.max_df = max(self.phrase_df.values())
		else:
			self.max_df = 0
		self.max_df_context = {}
		self.dc_context = {}
		self.self_dc = len(selected_docs)
		self.sum_cnt = sum(self.phrase_cnt.values())
		self.sum_cnt_context = {}
		self.global_scores = global_scores
		for group, docs in context_doc_groups.items():
			self.phrase_cnt_context[group], self.phrase_df_context[group] = self.agg_phrase_cnt_df(freq_data, docs)
			if len(self.phrase_df_context[group]) > 0:
				self.max_df_context[group] = max(self.phrase_df_context[group].values())
			else:
				self.max_df_context[group] = 0
			self.dc_context[group] = len(docs)
			self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())

		# added for exploration
		self.context_groups = {}
		self.ranked_list = []


def read_data(label_f, link_f):

	cells = {}
	freq_data = {}
	docs = set()
	phrases = set()

	with open(label_f, 'r+') as f:
		for line in f:
			segments = line.strip('\n\r').split('\t')
			cell = segments[1]
			doc_id = segments[0]
			if cell not in cells:
				cells[cell] = []
			cells[cell].append(doc_id)
			docs.add(doc_id)

	print 'Read label file done.'

	with open(link_f, 'r+') as f:
		for line in f:
			# print 'sss' + line
			segments = line.strip('\n\r ').split('\t')
			doc_id = segments[0]
			if doc_id not in docs:
				continue
			if doc_id not in freq_data:
				freq_data[doc_id] = {}

			for i in range(1, len(segments), 2):
				phrase, w = segments[i], int(segments[i+1])
				phrases.add(phrase)
				freq_data[doc_id][phrase] = w

	print 'Read link file done.'

	return cells, freq_data, phrases


def read_target_tokens(token_f):

	tokens = set()
	with open(token_f, 'r+') as f:
		for line in f:
			segments = line.strip('\r\n ').split('\t')
			tokens.add(segments[1])

	print 'Read target token file done.'
	return tokens


def run_caseolap(cells, freq_data, target_phs, o_file, verbose=3, top_k=200):
	of = open(o_file, 'w+')

	for cell in cells:
		print 'Running CaseOLAP for cell: %s' % cell

		selected_docs = cells[cell]
		context_doc_groups = copy.copy(cells)
		context_doc_groups.pop(cell, None)
		caseslim = CaseSlim(freq_data, selected_docs, context_doc_groups)

		top_phrases = caseslim.compute()
		of.write('%s\t' % cell)

		phr_str = ', '.join([ph[0] + '|' + str(ph[1]) for ph in top_phrases if ph[0] in target_phs])
		of.write('[%s]\n' % phr_str)


if __name__ == "__main__":
	# Traditional CaseOLAP Setting
	# parser = argparse.ArgumentParser(prog='caseslim.py', \
	# 		description='CaseOLAP slim version without cube structure.')
	# parser.add_argument('-label', required=True, \
	# 		help='The file with labeled docs.') 
	# parser.add_argument('-link', required=True, \
	# 		help='The file with doc phrase relationships.') 
	# parser.add_argument('-output', required=True, \
	# 		help='The output result file')
	# args = parser.parse_args()

	# cells, freq_data, phrases = read_data(args.label, args.link)

	# run_caseolap(cells, freq_data, args.output)

	# Taxonomy Special case
	parser = argparse.ArgumentParser(prog='caseslim.py', \
			description='CaseOLAP slim version without cube structure.')
	parser.add_argument('-folder', required=True, \
			help='The files used.')
	parser.add_argument('-iter', required=True, \
			help='Iteration index.')
	args = parser.parse_args()

	link_f = '%s/keyword_cnt.txt' % args.folder
	cell_f = '%s/paper_cluster-%s.txt' % (args.folder, args.iter)
	token_f = '%s/cluster_keyword-%s.txt' % (args.folder, args.iter)
	output_f = '%s/caseolap-%s.txt' % (args.folder, args.iter)


	cells, freq_data, phrases = read_data(cell_f, link_f)
	target_phs = read_target_tokens(token_f)
	# print target_phs

	run_caseolap(cells, freq_data, target_phs, output_f)


# python caseslim.py -folder ../data/cluster -iter 0
# python case_ranker.py -folder ../data/cluster -iter 0 -thres 0.15


