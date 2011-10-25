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
			raise BadFieldException(obj)
		else:
			ans = actions.doAction(obj)
	except BadFieldException, e:
		return {'result': e.value}
	return ans

def parseInputData(data):     
	try:
		object = json.loads(data)
	except (TypeError, ValueError), e:
		return {"result": "badJson"}
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
	object = object['test']
	result = list()
	conn = httplib.HTTPConnection("localhost:80", timeout = 10000)
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
