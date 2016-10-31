class DB:
	def __init__(self, id, start, end, parent):
		self.id = id
		self.start = start
		self.end = end
		self.parent = parent

def myhash(strlist):
	return ','.join(strlist)

class PrefixTreeESpan:
	def __init__(self):
		self.trees = []
		self.DBs = {}
		self.frequentLabels = []
		self.frequentSubTrees = []

	def clear(self):
		self.trees = []
		self.DBs = {}
		self.frequentLabels = []
		self.frequentSubTrees = []

	def loaddata(self, filename):
		self.minsup = minsup
		datafile = open(filename, 'r')
		for line in datafile.readlines():
			# print line.split(' ')
			count = 1
			while line[-count] in [' ', '\n']:
				count += 1
			# print line[:1-count].split(' ')
			self.trees.append(line[:1-count].split(' '))
		# print self.trees[-1][-1]

	def addResult(self, subtreelist):
		self.frequentSubTrees.append(subtreelist)

	def findFrequentLabel(self, minsup):
		labelcount = {}
		for tree in self.trees:
			visited = []
			for label in tree:
				if label != -1 and label not in visited:
					if label in labelcount.keys():
						labelcount[label] += 1
					else:
						labelcount[label] = 1
					visited.append(label)
		for label in labelcount.keys():
			if labelcount[label] >= minsup:
				self.frequentLabels.append(label)

	def initDB(self, label):
		curdb = []
		for tree in self.trees:
			idx = 0
			while idx < len(tree):
				if tree[i] == label:
					idx += 1
					start = idx
					expends = 1 # the number of expected end signal ('-1')
					while expends > 0:
						if tree[idx] == '-1':
							expends -= 1
						else:
							expends += 1
						idx += 1
					end = idx - 2
					if end > start:
						curdb.append(DB(self.trees.index(tree), start, end, label))
				else:
					idx += 1
		self.DBs[myhash([label, '-1'])] = curbd

	def run(self, minsup):
		self.findFrequentLabel(minsup)
		for label in self.frequentLabels:
			self.initDB(label)
			pattern = [label, '-1']
			self.addResult(pattern)
			self.Fre(pattern, 1, self.DBs[myhash(pattern)], minsup)

	def Fre(self, pattern, patternLength, ProDB, minsup):
		GEs = {}
		for db in ProDB:
			sequence = self.trees[db.id][db.start : db.end + 1]
			deep = 0


if __name__ == '__main__':
	espan = PrefixTreeESpan()
	espan.loaddata('treedata/D10.data', 2)
	# print espan.trees[-1][-1], type(espan.trees[-1][-1])
