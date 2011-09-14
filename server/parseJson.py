import json
import actions 

def parseInputData(data):
        try:
                object = json.loads(data)
        except (TypeError, ValueError), e:
                return ['badJson']
        result = json.loads('[]')
        for obj in object:
                if not('action' in obj):
                        ans = 'badJson'
                elif not(obj['action'] in actions.functions):
                        ans = 'badAction'
                else:
                        ans = actions.doAction(obj)
                result.append(ans)
        return result
	
def parseDataFromFile(fileName):
	try:
		file = open(fileName, 'r')
	except:
		return 'Cannot open file %s' % fileName
	return parseInputData(file.read())
	
if __name__ == "__main__":
    import sys
    parseDataFromFile(str(sys.argv[1]))
