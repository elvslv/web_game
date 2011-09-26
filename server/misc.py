MIN_USERNAME_LEN = 3
MIN_PASSWORD_LEN = 6
MAX_USERNAME_LEN = 16
MAX_PASSWORD_LEN = 18
MAX_MAPNAME_LEN = 15
MIN_PLAYERS_NUM = 2
MAX_PLAYERS_NUM = 5
MIN_GAMENAME_LEN = 1
MAX_GAMENAME_LEN = 50
MAX_RACENAME_LEN = 20
MAX_SKILLNAME_LEN = 20
MAX_GAMEDESCR_LEN = 300

VISIBLE_RACES = 6
INIT_COINS_NUM = 5
BASIC_CONQUER_COST = 2
RACE_NUM = 14
SPECIAL_POWER_NUM = 20

X0 = 5363478883
A = 9995326
C = 235286786
M = 7486379941
global LAST_SID, LAST_TIME

usrnameRegexp = r'^[a-z]+[\w_-]{%s,%s}$' % (MIN_USERNAME_LEN - 1, MAX_USERNAME_LEN - 1)
pwdRegexp = r'^.{%s,%s}$' % (MIN_PASSWORD_LEN, MAX_PASSWORD_LEN)

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

def generateTimeForTest():
	global LAST_TIME
	LAST_TIME = LAST_TIME + 1
	return LAST_TIME

actionFields = {
	'register': [
		{
			'name': 'username', 
			'type': unicode, 
			'mandatory': True,
			'min': MIN_USERNAME_LEN,
			'max': MAX_USERNAME_LEN
		}, 
		{
			'name': 'password', 
			'type': unicode, 
			'mandatory': True,
			'min': MIN_PASSWORD_LEN,
			'max': MAX_PASSWORD_LEN
		}
	],
	'login': [
		{
			'name': 'username', 
			'type': unicode, 
			'mandatory': True,
			'min': MIN_USERNAME_LEN,
			'max': MAX_USERNAME_LEN
		}, 
		{
			'name': 'password', 
			'type': unicode, 
			'mandatory': True,
			'min': MIN_PASSWORD_LEN,
			'max': MAX_PASSWORD_LEN			
		}
	],
	'logout': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'sendMessage': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'text', 'type': unicode, 'mandatory': True}
	],
	'getMessages': [
		{'name': 'since', 'type': int, 'mandatory': True}
	],
	'createDefaultMaps': [
		{'name': 'sid', 'type': int, 'mandatory': False}
	],
	'uploadMap': [
		{
			'name': 'mapName', 
			'type': unicode, 
			'mandatory': True,
			'max': MAX_MAPNAME_LEN
		}, 
		{
			'name': 'playersNum', 
			'type': int, 
			'mandatory': True,
			'min': MIN_PLAYERS_NUM,
			'max': MAX_PLAYERS_NUM
		},
		{
			'name': 'regions', 
			'type': list, 
			'mandatory': False,
		},
		{
			'name': 'turnsNum',
			'mandatory': True,
			'type': int,
			'min': 5,
			'max': 10
		}
	],
	'createGame': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{
			'name': 'gameName', 
			'type': unicode, 
			'mandatory': True,
			'min': MIN_GAMENAME_LEN,
			'max': MAX_GAMENAME_LEN
		},
		{'name': 'mapId', 'type': int, 'mandatory': True},
		{
			'name': 'gameDescr', 
			'type': unicode, 
			'mandatory': False,
			'max': MAX_GAMEDESCR_LEN	
		}
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
		{
			'name': 'isReady', 
			'type': int, 
			'mandatory': True,
			'min': 0,
			'max': 1
		}
	],
	'selectRace': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{
			'name': 'farFromStack', 
			'type': int, 
			'mandatory': True,
			'min': 0,
			'max': VISIBLE_RACES
		}
	],
	'conquer': [
		{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'regionId', 'type': int, 'mandatory': True},
		{'name': 'raceId', 'type': int, 'min': 0, 'max': RACE_NUM, 'mandatory': False}
	],
	'decline':[
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'finishTurn': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'doSmth': [
		{'name': 'sid', 'type': int, 'mandatory': True}
	],
	'redeployment': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'raceId', 'type': int, 'mandatory': False},
		{'name': 'regions', 'type': list, 'mandatory': True}
	]
}

possibleLandDescription = [
	'border', #3
	'coast',#4
	'sea',#5
	'mountain',#6
	'mine',#7
	'farmland',#8
	'magic',#9
	'forest',#10
	'hill',#11
	'swamp',#12
	'cavern' #13
]

defaultMaps = [
	{'mapName': 'defaultMap1', 'playersNum': 2, 'turnsNum': 5}, 
	{'mapName': 'defaultMap2', 'playersNum': 3, 'turnsNum': 5},
	{'mapName': 'defaultMap3', 'playersNum': 4, 'turnsNum': 5},
	{'mapName': 'defaultMap4', 'playersNum': 5, 'turnsNum': 5},
	{
		'mapName': 'defaultMap5', 
		'playersNum': 2, 
		'turnsNum': 5,
	 	'regions' : 
	 	[
	 		{
	 			'population' : 1,
	 			'landDescription' : ['mountain'],
	 			'adjacent' : [3, 4] 
	 		},
	 		{
	 			'population' : 1,
	 			'landDescription' : ['sea'],
	 			'adjacent' : [1, 4] 
	 		},
	 		{
	 			'population' : 1,
	 			'landDescription' : ['border', 'mountain'],
	 			'adjacent' : [1] 
	 		},
	 		{
	 			'population' : 1,
	 			'landDescription' : ['coast'],
	 			'adjacent' : [1, 2] 
	 		}
	 	]
	}	
			
]

gameStates = {
	'waiting': 1, 
	'processing': 2, 
	'ended': 3, 
	'finishTurn': 4, 
	'selectRace': 5,
	'conquer': 6, 
	'decline': 7,
	'redeployment': 8
}
