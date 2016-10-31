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
		datafile = open(filename, 'r')
		for line in datafile.readlines():
			count = 1
			while line[-count] in [' ', '\n']:
				count += 1
			self.trees.append(line[:1-count].split(' '))
		# self.trees = self.trees[:20000]

	def addResult(self, subtreelist):
		self.frequentSubTrees.append(subtreelist)

	def findFrequentLabel(self, minsup):
		print "Finding frequent labels..."
		labelcount = {}
		for tree in self.trees:
			visited = []
			# print self.trees.index(tree)
			for label in tree:
				if label != '-1' and label not in visited:
					if label in labelcount.keys():
						labelcount[label] += 1
					else:
						labelcount[label] = 1
					visited.append(label)
		for label in labelcount.keys():
			if labelcount[label] >= minsup:
				self.frequentLabels.append(label)
		print "%d frequent labels found." % len(self.frequentLabels)

	def initDB(self, label):
		curdb = []
		for tree in self.trees:
			idx = 0
			while idx < len(tree):
				if tree[idx] == label:
					idx += 1
					start = idx
					deepth = 1 # the number of expected end signal ('-1')
					while deepth > 0:
						if tree[idx] == '-1':
							deepth -= 1
						else:
							deepth += 1
						idx += 1
					end = idx - 2
					# print end
					if end > start:
						curdb.append(DB(self.trees.index(tree), start, end, label))
				else:
					idx += 1
		self.DBs[myhash([label, '-1'])] = curdb

	def updateDB(self, freqGE, pattern, oldDB):
		newDB = []
		for db in oldDB:
			subtree = self.trees[db.id][db.start : db.end + 1]
			idx  = 0
			deepth = 0
			flag = -1
			for idx in range(len(subtree)):
				if subtree[idx] == '-1':
					deepth -= 1
				else:
					deepth += 1
				if deepth == 1 and subtree[idx] == freqGE:
					flag = idx + 1
					break
				idx += 1
			if flag != -1:
				idx = flag
				deepth = 1
				curdb = []
				while idx < len(subtree):
					if subtree[idx] == '-1':
						deepth -= 1
					else:
						deepth += 1
					if deepth == 0:
						if len(curdb) > 0:
							curdb.append(subtree[idx])
							start = db.start + flag + idx - len(curdb)
							end = start + len(curdb) - 1
							if len(curdb) % 2:
								newDB.append(DB(db.id, start, end, freqGE))
							else:
								newDB.append(DB(db.id, start, end, db.parent))
							curdb = []
					else:
						curdb.append(subtree[idx])
					idx += 1
		self.DBs[myhash(pattern)] = newDB
		
	def run(self, minsup):
		print "Program starting, minsup is", minsup
		self.findFrequentLabel(minsup)
		# count = 1
		# total = len(self.frequentLabels)
		for label in self.frequentLabels:
			# print "Dealing the %dth label in %d labels" % (count, total)
			# count += 1
			self.initDB(label)
			pattern = [label, '-1']
			self.addResult(pattern)
			self.Fre(pattern, 1, self.DBs[myhash(pattern)], minsup)

	def Fre(self, pattern, patternLength, ProDB, minsup):
		GEs = {}
		for db in ProDB:
			subtree = self.trees[db.id][db.start : db.end + 1]
			deepth = 0
			tmp_GE = {}
			for label in subtree:
				if label == '-1':
					deepth -= 1
				else:
					deepth += 1
				if label != '-1' and deepth == 1:
					tmpkey = str(label) + '|' + db.parent
					if tmpkey not in tmp_GE.keys():
						if tmpkey in GEs.keys():
							GEs[tmpkey] += 1
						else:
							GEs[tmpkey] = 1
						tmp_GE[tmpkey] = 1
		freqGEs = {}
		for k in GEs.keys():
			if GEs[k] >= minsup:
				freqGEs[k] = GEs[k]
		for ge in freqGEs:
			[ge, parent] = ge.split('|')

			deepth = 0
			newpattern = []
			for i in range(len(pattern)):
				curlabel = pattern[i]
				if curlabel == '-1':
					deepth -= 1
				else:
					deepth += 1
				if deepth in [patternLength - 1, patternLength] and curlabel == parent:
					newpattern = pattern[:i+1] + [ge, '-1'] + pattern[i+1:]
					break
			if len(newpattern) != 0:
				self.addResult(newpattern)

			self.updateDB(ge, newpattern, ProDB)
			self.Fre(newpattern, patternLength + 1, self.DBs[myhash(newpattern)], minsup)


if __name__ == '__main__':
	espan = PrefixTreeESpan()
	# espan.loaddata('treedata/test.data')
	import time
	files = ['CSlog.data', 'D10.data', 'F5.data', 'T1M.data']
	datadir = 'treedata/'
	# espan.trees = espan.trees[:100]
	inputfile = files[0]
	print "Dealing with datafile: %s" % (datadir + inputfile)
	espan.loaddata(datadir + inputfile)
	totalnum = len(espan.trees)

	minsup = int(totalnum * 0.01)

	start = time.clock()
	espan.run(minsup)
	end = time.clock()

	print "Programe end in %f seconds." % (end - start)
	outputfile = open('result/' + str(minsup) + '-' + inputfile, 'w')
	for subtree in espan.frequentSubTrees:
		for i in subtree:
			outputfile.write(i + ' ')
		outputfile.write('\n')