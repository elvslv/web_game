import json
import actions 

def parseInputData(data):
        object = json.loads(data)
	if not('action' in object):
		return 'badJson'
	if not(object['action'] in actions.functions):
		return 'badAction'
	return actions.doAction(object)
	
def parseDataFromFile(fileName):
	try:
		file = open(fileName, 'r')
	except:
		return 'Cannot open file %s' % fileName
	return parseInputData(file.read())
	
if __name__ == "__main__":
    import sys
    parseDataFromFile(str(sys.argv[1]))
