import json
import actions 
from gameExceptions import BadFieldException
import misc
import random
import sys
import httplib
from db import dbi

def parseJsonObj(obj):
	try:
		if not('action' in obj):
			raise BadFieldException('badJson')
		else:
			ans = actions.doAction(obj)
	except BadFieldException, e:
		return {'result': e.value}
	return ans

def parseInputData(data):     
	try:
		object = json.loads(data)
	except (TypeError, ValueError), e:
		return {"result": "badJson"}				## Redo by friday
	if isinstance(object, list):
		return {"result": "badJson"}
	else:
		return parseJsonObj(object)
	
def parseDataFromFile(fileName):
	try:
		file = open(fileName, 'r')
	except:
		return 'Cannot open file %s' % fileName
	description = ''
	try:
		object = json.loads(file.read())
	except (TypeError, ValueError):
		return {'result': [{"result": "badJson"}], 'description': description}

	if not ('test' in object):
		return {'result': [{'result': 'badTest'}], 'description': description}

	if 'description' in object:
		description = object['description']
	if 'randseed' in object:
		misc.TEST_RANDSEED = object['randseed']
	else:
		misc.TEST_RANDSEED = 21425364547
		random.seed(misc.TEST_RANDSEED)
	conn = httplib.HTTPConnection("localhost:80", timeout = 10000)
	if 'include' in object:
		f1 = open('02_GameLogic/%s' % object['include'][0], 'r')
		incl = json.loads(f1.read())
		for obj in incl:
			conn.request("POST", "/small_worlds/", json.dumps(obj))
			r1 = conn.getresponse()
			ans = json.loads(r1.read())
			if not('result' in ans) or ans['result'] != 'ok':
				return {'result': 'include failed', 'description': description}
	object = object['test']			
	result = list()
	if isinstance(object, list):
		for obj in object:
			conn.request("POST", "/small_worlds/", json.dumps(obj))
			r1 = conn.getresponse()
			result.append(json.loads(r1.read()))
	else:
		conn.request("POST", "/small_worlds/", json.dumps(object))
		r1 = conn.getresponse()
		return {'result': [r1.read()], 'description': description}

	return {'result': result, 'description': description}
	
if __name__ == "__main__":
	import sys
	if len(sys.argv) > 0 and sys.argv[1] == 'resetServer':
		parseInputData(parseJsonObj({'action': 'resetServer'}))
