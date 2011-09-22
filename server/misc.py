MIN_USERNAME_LEN = 3
MIN_PASSWORD_LEN = 6
MAX_USERNAME_LEN = 16
MAX_PASSWORD_LEN = 18
MAX_MAPNAME_LEN = 15
DEFAULT_PLAYERS_NUM = 5
MIN_PLAYERS_NUM = 2
MAX_PLAYERS_NUM = 5
MIN_GAMENAME_LEN = 1
MAX_GAMENAME_LEN = 50
MAX_RACENAME_LEN = 20
MAX_GAMEDESCR_LEN = 300
X0 = 5363478883
A = 9995326
C = 235286786
M = 7486379941
global LAST_SID

def generateSid():
	global LAST_SID
	LAST_SID = (A * LAST_SID + C) % M
	return LAST_SID

def generateSidForTest():
	global LAST_SID
	LAST_SID = LAST_SID + 1
	return LAST_SID
	
def generateSids(n):
	global LAST_SID
	LAST_SID = X0
	for i in range(n):
		print generateSid()
		
		

userStages = {
	'notPlaying': 1, 
	'waitingTurn': 2, 
	'choosingRace': 3, 
	'firstAttack' : 4, 
	'notFirstAttack' : 5,
	'declined' : 6,
}

actionFields = {
	'register': [
		{'name': 'username', 'type': unicode, 'mandatory': True}, 
		{'name': 'password', 'type': unicode, 'mandatory': True}
	],
	'login': [
		{'name': 'username', 'type': unicode, 'mandatory': True}, 
		{'name': 'password', 'type': unicode, 'mandatory': True}
	],
	'logout': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'doSmth': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'sendMessage': [
		{'name': 'userId', 'type': int, 'mandatory': True}, 
		{'name': 'message', 'type': unicode, 'mandatory': True}
	],
	'getMessages': [
		{'name': 'since', 'type': float, 'mandatory': True}
	],
	'createDefaultMaps': [
		{'name': 'sid', 'type': int, 'mandatory': False}
	],
	
	'uploadMap': [
		{'name': 'mapName', 'type': unicode, 'mandatory': True}, 
		{'name': 'playersNum', 'type': int, 'mandatory': True},
		{'name': 'regions', 'type': list, 'mandatory': False}
	],
	'createGame': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'gameName', 'type': unicode, 'mandatory': True},
		{'name': 'mapId', 'type': int, 'mandatory': True},
		{'name': 'gameDescr', 'type': unicode, 'mandatory': False}
	],
	'getGameList': [
		{'name': 'sid', 'type': int, 'mandatory': False}
	],
	'joinGame': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'gameId', 'type': int, 'mandatory': True}
	],
	'leaveGame': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'setReadinessStatus': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'readinessStatus', 'type': int, 'mandatory': True}
	],
	'selectRace': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'raceId', 'type': int, 'mandatory': True}
	],
	'conquer': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'regionId', 'type': int, 'mandatory': True}
	],
	'decline':[
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'finishTurn': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	]
}
 
			
defaultMaps = [
	{'mapName': 'defaultMap1', 'playersNum': 2}, 
	{'mapName': 'defaultMap2', 'playersNum': 3},
	{'mapName': 'defaultMap3', 'playersNum': 4},
	{'mapName': 'defaultMap4', 'playersNum': 5},
	{
		'mapName': 'defaultMap5', 
		'playersNum': 5, 
		'regions' : 
		[
			{
				'population' : 1,
				'borderline' : 0,
				'seaside'    : 0,
				'highland'   : 1,
				'coastal'    : 0,
			},
			{
				'population' : 3,
				'seaside'    : 1,
				'borderline' : 0,
				'highland'   : 0,
				'coastal'    : 0,
			},
			{
				'population' : 2,
				'seaside'    : 0,
				'borderline' : 1,
				'highland'   : 0,
				'coastal'    : 0,
			},
			{
				'population' : 0,
				'borderline' : 0,
				'seaside'    : 0,
				'highland'   : 0,
				'coastal'    : 1,
			},
		]
	}	
			
]

defaultRaces = [
	{'raceName': 'caucasian', 'initialNum': 5},
	{'raceName': 'negroid', 'initialNum': 2},
				
]

gameStates = {'waiting': 1, 'processing': 2, 'ended': 3}
