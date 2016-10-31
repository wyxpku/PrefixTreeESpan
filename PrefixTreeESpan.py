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
		# self.minsup = minsup
		datafile = open(filename, 'r')
		for line in datafile.readlines():
			# print line.split(' ')
			count = 1
			while line[-count] in [' ', '\n']:
				count += 1
			# print line[:1-count].split(' ')
			# print line[:1-count], '---'
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
				if label != '-1' and label not in visited:
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
		# print 'freqlabel:',label
		for tree in self.trees:
			idx = 0
			while idx < len(tree):
				# print idx, ':', tree[idx]
				if tree[idx] == label:
					idx += 1
					start = idx
					deepth = 1 # the number of expected end signal ('-1')
					while deepth > 0:
						# print "curdeepth:", deepth
						# print "idx is", idx, ', node value', tree[idx]
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
		# print myhash([label, '-1'])
		# for db in curdb:
		# 	print db.__dict__

	def updateDB(self, freqGE, pattern, oldDB):
		# print freqGE
		# print pattern
		# print '------------------'
		newDB = []
		for db in oldDB:
			# print db.__dict__
			subtree = self.trees[db.id][db.start : db.end + 1]
			# print subtree
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
		self.findFrequentLabel(minsup)
		# print len(self.trees)
		# for tree in self.trees:
		# 	print tree
		# print self.frequentLabels
		for label in self.frequentLabels:
			self.initDB(label)
			pattern = [label, '-1']
			self.addResult(pattern)
			self.Fre(pattern, 1, self.DBs[myhash(pattern)], minsup)

	def Fre(self, pattern, patternLength, ProDB, minsup):
		GEs = {}
		# print "pattern:", pattern
		# print "pattern len:", patternLength
		# print "freqGEs:",freqGEs
		for db in ProDB:
			# print 'curdb:', db.__dict__
			subtree = self.trees[db.id][db.start : db.end + 1]
			# print 'subtree:', subtree
			deepth = 0
			tmp_GE = {}
			for label in subtree:
				if label == '-1':
					deepth -= 1
				else:
					deepth += 1
				# print label, deepth
				if label != '-1' and deepth == 1:
					# print label
					tmpkey = str(label) + '|' + db.parent
					# print "tmpkey:",tmpkey
					if tmpkey not in tmp_GE.keys():
						if tmpkey in GEs.keys():
							GEs[tmpkey] += 1
						else:
							GEs[tmpkey] = 1
						tmp_GE[tmpkey] = 1
					# print tmp_GE
					# print GEs
		freqGEs = {}
		for k in GEs.keys():
			# print k, v
			if GEs[k] >= minsup:
				freqGEs[k] = GEs[k]
		# print 'freqGEs:', freqGEs
		for ge in freqGEs:
			[ge, parent] = ge.split('|')
			# parent = parent.split(',')
			# print 'ge', ge
			# print 'parent', parent

			deepth = 0
			newpattern = []
			for i in range(len(pattern)):
				curlabel = pattern[i]
				if curlabel == '-1':
					deepth -= 1
				else:
					deepth += 1
				# print deepth, curlabel, parent
				if deepth in [patternLength - 1, patternLength] and curlabel == parent:
					newpattern = pattern[:i+1] + [ge, '-1'] + pattern[i+1:]
					# print newpattern
					break
			if len(newpattern) != 0:
				self.addResult(newpattern)

			self.updateDB(ge, newpattern, ProDB)
			self.Fre(newpattern, patternLength + 1, self.DBs[myhash(newpattern)], minsup)


if __name__ == '__main__':
	espan = PrefixTreeESpan()
	# espan.loaddata('treedata/test.data')
	import time
	start = time.clock()
	files = ['CSlog.data', 'D10.data', 'F5.data', 'T1M.data']
	datadir = 'treedata/'
	# espan.trees = espan.trees[:100]
	inputfile = files[0]
	print "Dealing with datafile: %s" % (datadir + inputfile)
	espan.loaddata(datadir + inputfile)

	start = time.clock()
	espan.run(10000)
	end = time.clock()
	print "Programe end in %f seconds." % (end - start)
	outputfile = open('result/' + inputfile, 'w')
	for subtree in espan.frequentSubTrees:
		for i in subtree:
			outputfile.write(subtree[i])
		outputfile.write('\n')
	# for inputfile in files:
	# 	espan.loaddata(datadir + inputfile)
	# 	print "Dealing with datafile: %s" % (datadir + inputfile)
	# 	espan.trees = espan.trees[:100]
	# 	start = time.clock()
	# 	espan.run(2)
	# 	end = time.clock()

	# 	espan.clear()
	# 	print "Programe end in %f seconds." % (end - start)
	# 	print "Find %d frequent subtrees" % len(espan.frequentSubTrees)

	# 	outputfile = open('result/' + inputfile, 'w')
	# 	for subtree in espan.frequentSubTrees:
	# 		for i in subtree:
	# 			outputfile.write(subtree[i])
	# 		outputfile.write('\n')
