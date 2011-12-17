from gameExceptions import BadFieldException
import misc
import sys
import os

def checkListCorrectness(data, field, type):
	msg = 'bad' + field[0].upper() + field[1:]
	if not field in data:
		raise BadFieldException(msg)
	
	for t in data[field]:
		if not isinstance(t, type):
			if type is str and not isinstance(t, unicode):
				raise BadFieldException(msg)
	#checkObjectsListCorrection(data, [{'name': field, 'type': type}])
			
def checkObjectsListCorrection(data, fields):
	for obj in data:
		for field in fields:
			msg = 'bad' + field['name'][0].upper() + field['name'][1:]
			if not(field['name'] in obj):
				raise BadFieldException(msg)
			
			if not isinstance(obj[field['name']], field['type']):
				raise BadFieldException(msg)
			if 'min' in field:
				if obj[field['name']] < field['min']:
					raise BadFieldException(msg)

def constructMsg(field):
	if field['name'] == 'sid':
		msg = 'badUser' + field['name'][0].upper() + field['name'][1:]
	elif field['name'] == 'text':
		msg = 'badMessage' + field['name'][0].upper() + field['name'][1:]
	elif field['name'] == 'isReady':
		msg = 'badReadinessStatus'
	else:
		msg = 'bad' + field['name'][0].upper() + field['name'][1:]
	return msg

def checkFieldsCorrectness(data):
	fields = misc.actionFields[data['action']]
	if not fields:
		raise BadFieldException('actionDoesntExist')
	for field in fields:
		if not field['name'] in data:
			if field['mandatory']:
				raise BadFieldException(constructMsg(field))

	for field in fields:
		if not field['name'] in data:
			continue
		msg = constructMsg(field)
		if not isinstance(data[field['name']], field['type']):
			raise BadFieldException(msg)
		minValue = field['min'] if 'min' in field else 0
		maxValue = field['max'] if 'max' in field else sys.maxint
		value = data[field['name']] if field['type'] is int else len(data[field['name']])
		if not minValue <= value <= maxValue:
			raise BadFieldException(msg)

def checkFiles(thumbSrc, pictSrc):
	path = os.path.dirname(__file__)
	sys.path.append(path)
	os.chdir(path)
	path1 = os.pardir
	path1 += '\\client'
	os.chdir(path1)
	if not(os.path.exists(thumbSrc) and os.path.exists(pictSrc)):
		raise BadFieldException("Thumbnail or picture files aren't found")
	os.chdir(path)
