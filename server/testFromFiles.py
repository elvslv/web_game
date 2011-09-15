import unittest
import parseJson
import editDb
import os
import sys
import json

class TestFromFile(unittest.TestCase):
        def __init__(self, inFile, ansFile):
                super(TestFromFile, self).__init__()
                self.inFile = inFile
                self.ansFile = ansFile

        def runTest(self):
                editDb.clearDb()
                f = open(self.ansFile)
                ans = f.read()
                out = parseJson.parseDataFromFile(self.inFile)
                self.assertListEqual(out, json.loads(ans))
                
def suite():
        suite = unittest.TestSuite()
        suite.addTests(TestFromFile('tests\\test_%d.in' % i, 'tests\\test_%d.ans' % i) for i in range(testNum))
        return suite

def main(n):
        global testNum
        testNum = n
        unittest.TextTestRunner().run(suite())
