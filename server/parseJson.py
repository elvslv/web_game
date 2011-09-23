import json
import actions 

def parseJsonObj(obj):
	if not('action' in obj):
		ans = {"result": "badJson"}
	else:
		ans = actions.doAction(obj)
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
	except (TypeError, ValueError), e:
		return {'result': [{"result": "badJson"}], 'description': description}

        if not ('test' in object):
                return {'result': [{'result': 'badTest'}], 'description': description}

        if 'description' in object:
                description = object['description']
	
        object = object['test']
	result = list()
	if isinstance(object, list):
		for obj in object:
			result.append(parseJsonObj(obj))
	else:
		return {'result': [parseJsonObj(object)], 'description': description}

	return {'result': result, 'description': description}
	
#if __name__ == "__main__":
#    import sys
#    parseDataFromFile(str(sys.argv[1]))
