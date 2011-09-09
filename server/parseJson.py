import json
import actions 

def parseInputData(data):
	object = json.loads(data)
	if not('action' in object):
		return 'badJson'
	if not(object['action'] in actions.functions):
		return 'badAction'
	return actions.doAction(object)
	
if __name__ == "__main__":
    import sys
    parseInputData(str(sys.argv[1]))
