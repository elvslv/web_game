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
		f = open(self.ansFile)
		ans = f.read()
		out = parseJson.parseDataFromFile(self.inFile)
		self.testDescr = out['description']
		self.assertListEqual(out['result'], json.loads(ans))
                
def suite():
        suite = unittest.TestSuite()
        suite.addTests(TestFromFile('%s\\test_%d.in' % (diri, i), '%s\\test_%d.ans' % (diri, i)) for i in range(start, end))
        return suite

def main(a, b, c):
        global start
        global end
        global diri
        start = a
        end = b
        diri = c
        unittest.TextTestRunner().run(suite())
if __name__=='__main__':
	main(0, 43, "simple_protocol_tests")
