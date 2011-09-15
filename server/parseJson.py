import json
import actions 

def parseJsonObj(obj):
        try:
                if not('action' in obj):
                        ans = 'badJson'
                elif not(obj['action'] in actions.functions):
                        ans = 'badAction'
                else:
                        ans = actions.doAction(obj)
        except(TypeError, ValueError):
                return 'badJson'
        return ans

def parseInputData(data):     
        try:
                object = json.loads(data)
        except (TypeError, ValueError), e:
                return [{'result': 'badJson'}]
        
        result = list()
        if isinstance(object, list):
                for obj in object:
                        result.append({'result': parseJsonObj(obj)})
        else:
                result.append({'result': 'badJson'})
                
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
