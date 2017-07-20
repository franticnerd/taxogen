import numpy as np
from os import listdir
from os.path import isfile, join
import operator
import utils


def get_candidates(folder, o_file):

	files = ['%s%s' % (folder, f) for f in listdir(folder) if isfile(join(folder, f))]
	quality_phrases = set()

	for file in files:
		with open(file) as f:
			for line in f:
				phrase = line.split(' ')[0]
				quality_phrases.add(phrase)

	print 'Quality phrase count: ' + str(len(quality_phrases))

	with open(o_file, 'w+') as g:
		for phrase in quality_phrases:
			g.write('%s\n' % phrase)


folder = '../data/leef/query_relevant/'
o_file = '../data/candidates.txt'

get_candidates(folder, o_file)






