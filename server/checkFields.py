from gameExceptions import BadFieldException
import misc
import sys

def checkListCorrectness(data, field, type):
	if not field in data:
		raise BadFieldException('badJson')

	msg = 'bad' + field[0].upper() + field[1:]
	for t in data[field]:
		if not isinstance(t, type):
			raise BadFieldException(msg)
	#checkObjectsListCorrection(data, [{'name': field, 'type': type}])
			
def checkObjectsListCorrection(data, fields):
	for obj in data:
		for field in fields:
			if not(field['name'] in obj):
				raise BadFieldException('badJson')
			msg = 'bad' + field['name'][0].upper() + field['name'][1:]
			if not isinstance(obj[field['name']], field['type']):
				raise BadFieldException(msg)
			if 'min' in field:
				if obj[field['name']] < field['min']:
					raise BadFieldException(msg)

def checkFieldsCorrectness(data):
	fields = misc.actionFields[data['action']]
	if not fields:
		raise BadFieldException('actionDoesntExist')
	for field in fields:
		if not field['name'] in data:
			if field['mandatory']:
				raise BadFieldException('badJson')
			continue

	for field in fields:
		if not field['name'] in data:
			continue
		if field['name'] == 'sid':
                        msg = 'badUser' + field['name'][0].upper() + field['name'][1:]
                elif field['name'] == 'text':
                        msg = 'badMessage' + field['name'][0].upper() + field['name'][1:]
                else:
                        msg = 'bad' + field['name'][0].upper() + field['name'][1:]
		if not isinstance(data[field['name']], field['type']):
			raise BadFieldException(msg)
		minValue = field['min'] if 'min' in field else 0
		maxValue = field['max'] if 'max' in field else sys.maxint
		value = data[field['name']] if field['type'] is int else len(data[field['name']])
		if not minValue <= value <= maxValue:
			raise BadFieldException(msg)

def checkRegionCorrectness(data):
	checkListCorrectness(data, 'landDescription', str)
	checkListCorrectness(data, 'adjacent', int)
	if not 'population' in data:
		data['population'] = 0
	
	queryStr = 'INSERT INTO Regions(MapId, RegionId, DefaultTokensNum'
	num = 0
	for descr in data['landDescription']:
		if not descr in misc.possibleLandDescription[:11]:
			raise BadFieldException('unknownLandDescription')
		queryStr += ', ' + descr.title()
		num += 1
	queryStr += ') VALUES(%s, %s, %s'
	for i in range(num):
		queryStr += ', 1'
	queryStr += ')'
	return queryStr
