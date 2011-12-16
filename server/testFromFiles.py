import unittest
import parseJson
import os
import sys
import json
import misc
import actions
import db

from db import dbi

class TestFromFile(unittest.TestCase):
	def __init__(self, inFile, ansFile):
		super(TestFromFile, self).__init__()
		self.inFile = inFile
		self.ansFile = ansFile
		self.testDescr = ''
		self.maxDiff = None

	def tearDown(self):
		print "Test %s description: %s\n" % (self.inFile, self.testDescr)
		misc.TEST_MODE = False
		
	def runTest(self):
		misc.LAST_SID = 0
		misc.LAST_TIME = 0
		misc.TEST_MODE = True
		f = open(self.ansFile)
		ans = f.read()
		out = parseJson.parseDataFromFile(self.inFile)
		self.testDescr = out['description']
		self.assertListEqual(out['result'], json.loads(ans))
		

def suite():
	suite = unittest.TestSuite()
	suite.addTests(TestFromFile('%s\\test_%d.in' % (testDir, i), '%s\\test_%d.ans' % (testDir, i)) for i in range(begin, end))
	#suite.addTests(TestFromFile('%s\\t%d._in' % (testDir, i), '%s\\t%d.ans' % (testDir, i)) for i in range(begin, end))
	return suite

def main(a, b, c):
	global begin
	global end
	global testDir
	begin = a
	end = b
	testDir = c
	unittest.TextTestRunner().run(suite())
		
if __name__=='__main__':
	argc = len(sys.argv)
	if argc < 2:             
		sys.exit("Format: python TestFromFiles.py [begin] end [directory]")
	fin = int(sys.argv[1]) if argc == 2 else int(sys.argv[2])
	start =  int (sys.argv[1]) if argc >= 3 else 0
	directory = sys.argv[3] if argc == 4 else "tests"
	main(start, fin, directory)
