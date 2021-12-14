# generate the evaluation pairs of different taxonomies
import argparse
import utils
import operator
import random
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from taxonomy import Taxonomy, TNode


def gen_intrusion_pairs(tax, N, case_N):
	# generate the sibling intrusion set
	cnt = 0

	pairs = {}

	# exp_file = open('%s_exp' % intru_f, 'w+')
	# gold_file = open('%s_gold' % intru_f, 'w+')

	while cnt < case_N:
		node = tax.sample_a_node()

		if node.parent == None:
			continue
		sibs = node.get_siblings()
		if len(sibs) == 0:
			continue
		s_node = random.choice(sibs)

		shuf_phs = node.ph_list[:N]
		cand_phs = s_node.ph_list
		while True:
			n_ph = random.choice(cand_phs)
			if n_ph not in shuf_phs:
				shuf_phs.append(n_ph)
				random.shuffle(shuf_phs)
				exp_line = ','.join(shuf_phs)
				intr_idx = shuf_phs.index(n_ph)
				pairs[exp_line] = intr_idx
				cnt += 1
				break

	return pairs


def gen_isa_pairs(tax, isa_N, case_N):
	cnt = 0
	pairs = {}

	while cnt < case_N:
		node = tax.sample_a_node()
		rmd_node = tax.sample_a_node()
		if node.parent == None or node.parent == rmd_node or node.parent.name == '*' \
			or rmd_node.name == '*':
			continue
		p_node = node.parent

		n_phs = '|'.join(node.ph_list[:isa_N])
		p_phs = '|'.join(p_node.ph_list[:isa_N])
		rmd_phs = '|'.join(rmd_node.ph_list[:isa_N])
		if len(p_phs) == 0 or len(rmd_phs) == 0:
			print(tax)
			print(n_phs)
			print(node.name)
			print(p_node.name)
			print(rmd_node.name)
			exit(1)
		order = random.choice([0, 1])
		p_id = 0
		if order == 0:
			exp_line = '%s,%s,%s' % (n_phs, p_phs, rmd_phs)
		else:
			exp_line = '%s,%s,%s' % (n_phs, rmd_phs, p_phs)
			p_id = 1
		pairs[exp_line] = p_id

		cnt += 1
	
	return pairs


def gen_subdomain_pairs(tax, isa_N):
	pairs = {}

	for node_name in tax.all_nodes:
		node = tax.all_nodes[node_name]
		if node.name == '*' or node.parent.name == '*':
			continue

		n_phs = '|'.join(node.ph_list[:isa_N])
		p_phs = '|'.join(node.parent.ph_list[:isa_N])
	
		exp_line = '%s,%s' % (n_phs, p_phs)
		pairs[exp_line] = node.level

	return pairs


def read_taxonomy(tax_f):
	root = TNode('*', [])
	tax = Taxonomy(tax_f, root)

	with open(tax_f) as f:
		for line in f:
			node_name, ph_str = line.strip('\r\n').split('\t')
			node = TNode(node_name, ph_str.split(','))
			tax.add_node(node)

	return tax

def handler(folder, output, N, isa_N, case_N):

	files = ['%s/%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f))]
	taxs = {}

	for tax_f in files:
		method_name = basename(tax_f)
		taxs[method_name] = read_taxonomy(tax_f)

	intru_maps = {}
	isa_maps = {}
	subdomain_map = {}

	for tax_name in taxs:
		print(tax_name)
		# generate intrusion pairs
		# intru_f = '%s/%s.intrusion' % (output, tax_name)
		intru_maps[tax_name] = gen_intrusion_pairs(taxs[tax_name], N, case_N)
		# isa_f = '%s/%s.isa' % (output, tax_name)
		isa_maps[tax_name] = gen_isa_pairs(taxs[tax_name], isa_N, case_N)
		subdomain_map[tax_name] = gen_subdomain_pairs(taxs[tax_name], isa_N)

	# exit(1)

	# The intrusion part
	if True:
		intru_gold_f = '%s/intrusion_gold.txt' % output

		intru_all = {}
		for tax_name in taxs:
			for exp_str  in intru_maps[tax_name]:
				intru_all[exp_str] = (tax_name, intru_maps[tax_name][exp_str])

		each_voter_n = 80
		subset_n = 0

		intru_exp_f = '%s/intrusion_exp_%d.csv' % (output, subset_n)
		g_exp = open(intru_exp_f, 'w+')
		g_exp.write('0,1,2,3,4,5,outlier id\n')
		
		with open(intru_gold_f, 'w+') as g_gold:
			idx = 0
			for exp_str in intru_all:
				g_exp.write('%s\n' % exp_str)
				g_gold.write('%s\t%s\t%d\n' % (exp_str, intru_all[exp_str][0], intru_all[exp_str][1]))

				idx += 1
				if idx % each_voter_n == 0:
					subset_n += 1
					intru_exp_f = '%s/intrusion_exp_%d.csv' % (output, subset_n)
					g_exp.close()
					g_exp = open(intru_exp_f, 'w+')
					g_exp.write('0,1,2,3,4,5,outlier id\n')
		g_exp.close()


	# The old isa evaluation
	if False:
		isa_gold_f = '%s/isa_gold.txt' % output

		intru_all = {}
		for tax_name in taxs:
			for exp_str  in isa_maps[tax_name]:
				intru_all[exp_str] = (tax_name, isa_maps[tax_name][exp_str])

		each_voter_n = 125
		subset_n = 0

		intru_exp_f = '%s/isa_exp_%d.csv' % (output, subset_n)
		g_exp = open(intru_exp_f, 'w+')
		g_exp.write(',0,1,parent id\n')
		
		with open(isa_gold_f, 'w+') as g_gold:
			idx = 0
			for exp_str in intru_all:
				g_exp.write('%s\n' % exp_str)
				g_gold.write('%s\t%s\t%d\n' % (exp_str, intru_all[exp_str][0], intru_all[exp_str][1]))

				idx += 1
				if idx % each_voter_n == 0:
					subset_n += 1
					intru_exp_f = '%s/isa_exp_%d.csv' % (output, subset_n)
					g_exp.close()
					g_exp = open(intru_exp_f, 'w+')
					g_exp.write(',0,1,parent id\n')


	if True:
		sub_gold_f = '%s/subdomain_gold.txt' % output

		intru_all = {}
		for tax_name in taxs:
			for exp_str  in subdomain_map[tax_name]:
				intru_all[exp_str] = (tax_name, subdomain_map[tax_name][exp_str])

		each_voter_n = 80
		subset_n = 0

		intru_exp_f = '%s/subdomain_exp_%d.csv' % (output, subset_n)
		g_exp = open(intru_exp_f, 'w+')
		g_exp.write('child,parent,y or n?\n')
		
		with open(sub_gold_f, 'w+') as g_gold:
			idx = 0
			for exp_str in intru_all:
				g_exp.write('%s\n' % exp_str)
				g_gold.write('%s\t%s\t%d\n' % (exp_str, intru_all[exp_str][0], intru_all[exp_str][1]))

				idx += 1
				if idx % each_voter_n == 0:
					subset_n += 1
					intru_exp_f = '%s/subdomain_exp_%d.csv' % (output, subset_n)
					g_exp.close()
					g_exp = open(intru_exp_f, 'w+')
					g_exp.write('child,parent,y or n?\n')


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='gen_eval.py', \
			description='generate the evaluation pairs of different taxonomies')
	parser.add_argument('-folder', required=True, \
			help='The folder that contains generated taxonomies.')
	parser.add_argument('-output', required=True, \
			help='The folder that contains output files.')
	args = parser.parse_args()

	N = 5 # number of phrase before intrusion
	isa_N = 5 # number of phrases to represent a node in isa judgement
	case_N = 49 # number of cases generated for each taxonomy and task

	handler(args.folder, args.output, N, isa_N, case_N)

