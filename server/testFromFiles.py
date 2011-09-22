import unittest
import parseJson
import editDb
import os
import sys
import json
import random
import misc
import actions

class TestFromFile(unittest.TestCase):
	def __init__(self, inFile, ansFile):
		super(TestFromFile, self).__init__()
		self.inFile = inFile
		self.ansFile = ansFile
		self.testDescr = ''
		self.maxDiff = None

	def tearDown(self):
		print "Test %s description:%s " % (self.inFile, self.testDescr)
		
	def runTest(self):
		misc.LAST_SID = 0
		editDb.clearDb()
		actions.createDefaultRaces()
		f = open(self.ansFile)
		ans = f.read()
		out = parseJson.parseDataFromFile(self.inFile)
		self.testDescr = out['description']
		self.assertListEqual(out['result'], json.loads(ans))
                
def suite():
	suite = unittest.TestSuite()
        suite.addTests(TestFromFile('tests\\test_%d.in' % i, 'tests\\test_%d.ans' % i) for i in range(start, end))
        return suite

def main(a, b):
        global start
        global end
        start = a
        end = b
        unittest.TextTestRunner().run(suite())
		
if __name__=='__main__':
        if len(sys.argv) != 3:             
                sys.exit("Need two numbers as the first and the last test numbers")
	main(int(sys.argv[1]), int(sys.argv[2]))
