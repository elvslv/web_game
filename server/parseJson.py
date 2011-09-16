import json
import actions 

def parseJsonObj(obj):
	try:
		if not('action' in obj):
			ans = {"result": "badJson"}
		else:
			ans = actions.doAction(obj)

	except(TypeError, ValueError):
		return {"result": "badJson"}
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

	try:
		object = json.loads(file.read())
	except (TypeError, ValueError), e:
		return [{"result": "badJson"}]
	
	result = list()
	if isinstance(object, list):
		for obj in object:
			result.append(parseJsonObj(obj))
	else:
		return [parseJsonObj(object)]

	return result
	
if __name__ == "__main__":
    import sys
    parseDataFromFile(str(sys.argv[1]))
