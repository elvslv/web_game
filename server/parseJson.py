import json
import actions 
from gameExceptions import BadFieldException
import misc
import random
import httplib

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

	conn = httplib.HTTPConnection("localhost:80")
	if isinstance(object, list):
		for obj in object:
			conn.request("POST", "/small_worlds/", json.dumps(obj))
			r1 = conn.getresponse()
			ans = r1.read()
			result.append(json.loads(ans))
	else:
		conn.request("POST", "/small_worlds/", json.dumps(object))
		r1 = conn.getresponse()
		return {'result': [r1], 'description': description}

	return {'result': result, 'description': description}
	
#if __name__ == "__main__":
#    import sys
#    parseDataFromFile(str(sys.argv[1]))
