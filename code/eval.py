# generate the evaluation pairs of different taxonomies
import argparse
import utils
import operator
import random
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname, basename, exists
from taxonomy import Taxonomy, TNode



def handler(folder):

	if True:
		files = ['%s/%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f)) and 'intrusion_exp' in f]
		print(files)

		intru_gold = '%s/%s' % (folder, 'intrusion_gold.txt')

		gold = {}
		methods = set()
		with open(intru_gold, 'r') as f:
			for line in f:
				segs = line.strip('\r\n').split('\t')
				gold[segs[0]] = (segs[1], segs[2])
				methods.add(segs[1])


		total = {x:0 for x in methods}
		correct = {x:0 for x in methods}

		idx = 0
		for intru_f in files:
			# print idx
			# print intru_f
			first = True
			with open(intru_f) as f:
				for line in f:
					# print line
					idx += 1
					if first:
						first = False
						continue
					segs = line.strip('\r\n').split(',')
					key = ','.join(segs[:6])
					value = segs[6]
					(method, gold_value) = gold[key]
					total[method] += 1
					if gold_value == value:
						correct[method] += 1

		# print idx

		print('\nIntrusion results!!')
		for method in total:
			print('%s accuracy: %d/%d - %f' % (method, correct[method], total[method], float(correct[method]) / total[method]))


	# files = ['%s/%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f)) and 'isa_exp' in f]
	# print files

	# intru_gold = '%s/%s' % (folder, 'isa_gold.txt')

	# gold = {}
	# methods = set()
	# with open(intru_gold, 'r') as f:
	# 	for line in f:
	# 		segs = line.strip('\r\n').split('\t')
	# 		gold[segs[0]] = (segs[1], segs[2])
	# 		methods.add(segs[1])


	# total = {x:0 for x in methods}
	# correct = {x:0 for x in methods}

	# for intru_f in files:
	# 	first = True
	# 	with open(intru_f) as f:
	# 		for line in f:
	# 			if first:
	# 				first = False
	# 				continue
	# 			segs = line.strip('\r\n').split(',')
	# 			key = ','.join(segs[:-1])
	# 			value = segs[-1]
	# 			(method, gold_value) = gold[key]
	# 			total[method] += 1
	# 			if gold_value == value:
	# 				correct[method] += 1

	# print '\nIsa results!!'
	# for method in total:
	# 	print '%s accuracy: %d/%d - %f' % (method, correct[method], total[method], float(correct[method]) / total[method])


	# subdomain result
	files = ['%s/%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f)) and 'subdomain_exp' in f]
	print(files)

	intru_gold = '%s/%s' % (folder, 'subdomain_gold.txt')

	gold = {}
	methods = set()
	with open(intru_gold, 'r') as f:
		for line in f:
			segs = line.strip('\r\n').split('\t')
			gold[segs[0]] = (segs[1], segs[2])
			methods.add(segs[1])


	total = {x:0 for x in methods}
	correct = {x:0 for x in methods}
	incorrect = {x:0 for x in methods}

	for intru_f in files:
		first = True
		with open(intru_f) as f:
			for line in f:
				if first:
					first = False
					continue
				segs = line.strip('\r\n').split(',')
				key = segs[0] + ',' + segs[1]
				value = segs[2]
				(method, lvl) = gold[key]
				total[method] += 1
				if value == 'y':
					correct[method] += 1
				if value == 'n':
					incorrect[method] += 1

	print('\nSubdomain results!!')
	for method in total:
		print('%s accuracy: %d/%d/%d - %f' % (method, correct[method], incorrect[method], total[method], float(correct[method]) / total[method]))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='gen_eval.py', \
			description='generate the evaluation pairs of different taxonomies')
	parser.add_argument('-folder', required=True, \
			help='The folder that contains generated taxonomies.')
	args = parser.parse_args()

	handler(args.folder)

