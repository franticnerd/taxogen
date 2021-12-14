import os
import math
import operator

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

def kl_divergence(p, q):
	if len(p) != len(q):
		print('KL divergence error: p, q have different length')
	c_entropy = 0
	for i in range(len(p)):
		if p[i] > 0:
			c_entropy += p[i] * math.log(float(p[i]) / q[i])
	return c_entropy

def avg_weighted_colors(color_list, c_size):
	# print color_list
	# given a weighted color list, return the result
	result_color = [0] * c_size
	for (color, weight) in color_list:
		w_color = [x * weight for x in color]
		# print w_color
		result_color = list(map(operator.add, result_color, w_color))
		# print result_color
	return l1_normalize(result_color)


def l1_normalize(p):
	sum_p = sum(p)
	if sum_p <= 0:
		print('Normalizing invalid distribution')
	return [x/sum_p for x in p]

def cossim(p, q):
	if len(p) != len(q):
		print('KL divergence error: p, q have different length')
	
	p_len = q_len = mix_len = 0

	for i in range(len(p)):
		mix_len += p[i] * q[i]
		p_len += p[i] * p[i]
		q_len += q[i] * q[i]

	return mix_len / (math.sqrt(p_len) * math.sqrt(q_len))

def euclidean_distance(p, q):
	if len(p) != len(q):
		print('Euclidean distance error: p, q have different length')
	
	distance = 0

	for i in range(len(p)):
		distance += math.pow(p[i] - q[i], 2)

	return math.sqrt(distance)


def euclidean_cluster(ps, c):
	if len(ps) == 0 or c == None:
		print('Cluster is empty')

	distance = 0

	for p in ps:
		for i in range(len(p)):
			distance += math.pow(p[i] - c[i], 2)
	distance /= len(ps)

	return math.sqrt(distance)


def dot_product(p, q):
	if len(p) != len(q):
		print('KL divergence error: p, q have different length')
	
	p_len = q_len = mix_len = 0

	for i in range(len(p)):
		mix_len += p[i] * q[i]

	return mix_len

def softmax(score_list):
	# normalization of exp
	exp_sum = 0
	for score in score_list:
		exp_sum += math.exp(score)

	exp_list = []
	for score in score_list:
		normal_value = math.exp(score) / exp_sum
		exp_list.append(normal_value)
	return exp_list


def softmax_for_map(t_map):
	exp_sum = 0
	for key in t_map:
		score = t_map[key]
		exp_sum += math.exp(score)

	for key in t_map:
		score = t_map[key]
		normal_value = math.exp(score) / exp_sum
		t_map[key] = normal_value


def avg_emb_with_distinct(ele_map, embs_from, dist_map, vec_size):

	avg_emb = [0] * vec_size
	t_weight = 0

	for key, value in ele_map.items():
		t_emb = embs_from[key]
		w = value * dist_map[key]
		for i in range(vec_size):
			avg_emb[i] += w * t_emb[i]
		t_weight += w

	for i in range(vec_size):
		avg_emb[i] /= t_weight

	return avg_emb


def avg_emb(ele_map, embs_from, vec_size):
	
	avg_emb = [0] * vec_size
	t_weight = 0

	for key, value in ele_map.items():
		t_emb = embs_from[key]
		w = value
		for i in range(vec_size):
			avg_emb[i] += w * t_emb[i]
		t_weight += w

	for i in range(vec_size):
		avg_emb[i] /= t_weight

	return avg_emb

def load_hier_f(hier_f):
	hier_map = {}

	with open(hier_f) as f:
		idx = 0
		for line in f:
			topic = line.split()[0]
			hier_map[topic] = idx
			idx += 1

	return hier_map






# ensure the path for the output file exist
def ensure_directory_exist(file_name):
	directory = os.path.dirname(file_name)
	if not os.path.exists(directory):
		os.makedirs(directory)
