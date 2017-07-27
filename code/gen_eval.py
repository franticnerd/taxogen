# generate the evaluation pairs of different taxonomies
import argparse
import utils
import operator
import random
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from taxonomy import Taxonomy, TNode


def gen_intrusion_pairs(tax, N, case_N, intru_f):
	# generate the sibling intrusion set
	cnt = 0

	exp_file = open('%s_exp' % intru_f, 'w+')
	gold_file = open('%s_gold' % intru_f, 'w+')

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
				exp_line = '%d\t%s\n' % (cnt, ','.join(shuf_phs))
				exp_file.write(exp_line)
				gold_line = '%d\t%s\t%s\t%s\n' % (cnt, node.name,
					s_node.name, n_ph)
				gold_file.write(gold_line)
				cnt += 1
				break

	exp_file.close()
	gold_file.close()


def gen_isa_pairs(tax, isa_N, case_N, isa_f):
	cnt = 0

	exp_file = open('%s_exp' % isa_f, 'w+')
	gold_file = open('%s_gold' % isa_f, 'w+')

	while cnt < case_N:
		node = tax.sample_a_node()
		rmd_node = tax.sample_a_node()
		if node.parent == None or node.parent == rmd_node:
			continue
		p_node = node.parent

		n_phs = ','.join(node.ph_list[:isa_N])
		p_phs = ','.join(p_node.ph_list[:isa_N])
		rmd_phs = ','.join(rmd_node.ph_list[:isa_N])
		order = random.choice([0, 1])
		if order == 0:
			exp_line = '%d\t%s\t%s\t%s\n' % (cnt, n_phs, p_phs, rmd_phs)
		else:
			exp_line = '%d\t%s\t%s\t%s\n' % (cnt, n_phs, rmd_phs, p_phs)
		exp_file.write(exp_line)
		if order == 0:
			gold_line = '%d\t%s\tleft\n' % (cnt, node.name)
		else:
			gold_line = '%d\t%s\tright\n' % (cnt, node.name)
		gold_file.write(gold_line)

		cnt += 1


	exp_file.close()
	gold_file.close()
	
	return


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

	for tax_name in taxs:
		# generate intrusion pairs
		intru_f = '%s/%s.intrusion' % (output, tax_name)
		gen_intrusion_pairs(taxs[tax_name], N, case_N, intru_f)

		isa_f = '%s/%s.isa' % (output, tax_name)
		gen_isa_pairs(taxs[tax_name], isa_N, case_N, isa_f)



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
	case_N = 20 # number of cases generated for each taxonomy and task

	handler(args.folder, args.output, N, isa_N, case_N)

