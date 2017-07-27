import numpy as np
from collections import defaultdict
from math import log
import random
import copy

class TNode:
	def __init__(self, name, ph_list):

		self.name = name
		self.ph_list = ph_list
		self.ph_cnt = len(ph_list)
		self.parent = None
		self.children = []
		self.level = len(name.split('/'))

	def add_child(self, node):
		if node not in self.children:
			self.children.append(node)
			node.parent = self

	def get_siblings(self):
		if self.parent is None:
			return []
		sibs = copy.copy(self.parent.children)
		sibs.remove(self)
		return sibs

	def __repr__(self):
		return self.name

	def __str__(self):
		return self.name


# the complete taxonomy
class Taxonomy:

	def __init__(self, path, root):
		self.path = path
		self.root = root
		self.all_nodes = {root.name:root}

	def add_node(self, node):
		self.all_nodes[node.name] = node
		p_name = '/'.join(node.name.split('/')[:-1])
		if self.find_node(p_name) is not None:
			self.find_node(p_name).add_child(node)

	def find_node(self, name):
		if name in self.all_nodes:
			return self.all_nodes[name]
		return None

	def sample_a_node(self):
		return random.choice(self.all_nodes.values())



