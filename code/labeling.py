import argparse
import utils
import operator
import Queue
from os import listdir
from os.path import isfile, join, isdir, abspath, dirname
from case_ranker import read_caseolap_result, rank_phrase

def label(folder):
	print dirname(folder)
	# p_case_f = '%s'
	return ''


def recursion(root):

	q = Queue.Queue()
	q.put(root)

	while not q.empty():
		c_folder = q.get()
		# expand children
		children_fs = ['%s/%s' % (c_folder, f) for f in listdir(c_folder) if isdir(join(c_folder, f))]
		for child in children_fs:
			q.put(child)

		# handle current
		if c_folder != root:
			l = label(c_folder)
			# print 'label for %s is: %s' % (c_folder, l)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(prog='labeling.py', \
			description='')
	parser.add_argument('-root', required=True, \
			help='root of data files.')
	args = parser.parse_args()

	recursion(args.root)
