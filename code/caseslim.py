# from utils.utils import agg_phrase_cnt
# from utils.utils import agg_phrase_df
# from utils.utils import normalize
from heapq import heappush, heappop, heappushpop, nsmallest, nlargest
import codecs
import math
import ast
import ipdb


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




	# def __init__(self, freq_data, selected_docs, context_doc_groups, global_scores):
	# 	print 'start query'
	# 	self.selected_docs = selected_docs
	# 	self.phrase_cnt = self.agg_phrase_cnt(freq_data, selected_docs)
	# 	self.phrase_df = self.agg_phrase_df(freq_data, selected_docs)
	# 	self.phrase_cnt_context = {}
	# 	self.phrase_df_context = {}
	# 	if len(self.phrase_df) > 0:
	# 		self.max_df = max(self.phrase_df.values())
	# 	else:
	# 		self.max_df = 0
	# 	self.max_df_context = {}
	# 	self.dc_context = {}
	# 	self.self_dc = len(selected_docs)
	# 	self.sum_cnt = sum(self.phrase_cnt.values())
	# 	self.sum_cnt_context = {}
	# 	self.global_scores = global_scores
	# 	for group, docs in context_doc_groups.items():
	# 		self.phrase_cnt_context[group] = agg_phrase_cnt(freq_data, docs)
	# 		self.phrase_df_context[group] = agg_phrase_df(freq_data, docs)
	# 		if len(self.phrase_df_context[group]) > 0:
	# 			self.max_df_context[group] = max(self.phrase_df_context[group].values())
	# 		else:
	# 			self.max_df_context[group] = 0
	# 		self.dc_context[group] = len(docs)
	# 		self.sum_cnt_context[group] = sum(self.phrase_cnt_context[group].values())

	# 	# added for exploration
	# 	self.context_groups = {}
	# 	self.ranked_list = []




# def point_query(freq_data, selected_docs, context_doc_groups, global_scores, score_type):
# 	algorithm = OLAPORP(freq_data, selected_docs, context_doc_groups, global_scores)
# 	if score_type == 'TFIDF':
# 		return algorithm.compute_tfidf()
# 	else:
# 		return algorithm.compute(score_type), algorithm
	
