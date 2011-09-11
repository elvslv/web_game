import unittest
import parseJson
import editDb
import os

testNum = 1

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
                self.assertEqual(str(out), ans)
                
def suite():
        suite = unittest.TestSuite()
        suite.addTests(TestFromFile('tests\\test_%d.in' % i, 'tests\\test_%d.ans' % i) for i in range(testNum))
        return suite

if __name__ == '__main__':
        unittest.TextTestRunner().run(suite())

