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
RACE_NUM = 13
SPECIAL_POWER_NUM = 19

X0 = 5363478883
A = 9995326
C = 235286786
M = 7486379941
global TEST_MODE, TEST_RANDSEED
TEST_MODE=True
TEST_RANDSEED = 12345
global LAST_SID, LAST_TIME

usrnameRegexp = r'^[a-z]+[\w_-]{%s,%s}$' % (MIN_USERNAME_LEN - 1, MAX_USERNAME_LEN - 1)
pwdRegexp = r'^.{%s,%s}$' % (MIN_PASSWORD_LEN, MAX_PASSWORD_LEN)

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
			'name': 'position', 
			'type': int, 
			'mandatory': True,
			'min': 0,
			'max': VISIBLE_RACES-1
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
	'redeploy': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'raceId', 'type': int, 'mandatory': False},
		{'name': 'regions', 'type': list, 'mandatory': True}
	],
	'defend': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'regions', 'type': list, 'mandatory': True}
	],
	'getVisibleTokenBadges': [
		{'name': 'gameId', 'type': int, 'mandatory': True}
	],
	'resetServer': [{'name': 'sid', 'type': int, 'mandatory': False}]
}

possibleLandDescription = [
	'border',
	'coast',
	'sea',
	'mountain',
	'mine',
	'farmland',
	'magic',
	'forest',
	'hill',
	'swamp',
	'cavern',
	'holeInTheGround',
	'encampment', 
	'dragon', 
	'fortress',
	'hero'
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
	},
	{
		'mapName': 'defaultMap6', 
		'playersNum': 2, 
		'turnsNum': 5,
	 	'regions' : 
	 	[
	 		{
	 			'landDescription' : ['sea', 'border'],
	 			'adjacent' : [1, 16, 17] 
	 		},
	 		{
	 			'landDescription' : ['mine', 'border', 'coast', 'forest'],
	 			'adjacent' : [0, 17, 18, 2] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain'],
	 			'adjacent' : [1, 18, 20, 3] 
	 		},
	 		{
	 			'landDescription' : ['farmland', 'border'],
	 			'adjacent' : [2, 20, 21, 4] 
	 		},
	 		{
	 			'landDescription' : ['cavern', 'border', 'swamp'],
	 			'adjacent' : [3, 21, 22, 5] 
	 		},
			{
				'population': 1,
	 			'landDescription' : ['forest', 'border'],
	 			'adjacent' : [4, 22, 6] 
	 		},
			{
	 			'landDescription' : ['mine', 'border', 'swamp'],
	 			'adjacent' : [5, 22, 7, 23, 25] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain', 'coast'],
	 			'adjacent' : [6, 25, 9, 8] 
	 		},
	 		{
	 			'landDescription' : ['border', 'sea'],
	 			'adjacent' : [7, 9, 10] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['cavern', 'coast'],
	 			'adjacent' : [8, 7, 10, 25] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['mine', 'coast', 'forest', 'border'],
	 			'adjacent' : [9, 25, 26, 11] 
	 		},
	 		{
	 			'landDescription' : ['forest', 'border'],
	 			'adjacent' : [10, 26, 29, 12] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'border'],
	 			'adjacent' : [11, 29, 27, 13] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'border'],
	 			'adjacent' : [12, 27, 15, 14] 
	 		},
	 		{
	 			'landDescription' : ['hill', 'border'],
	 			'adjacent' : [13, 15] 
	 		},
	 		{
	 			'landDescription' : ['farmland', 'magic', 'border'],
	 			'adjacent' : [14, 19, 27, 16] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain', 'cavern', 'mine', 
	 				'coast'],
	 			'adjacent' : [15, 19, 0, 17] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['farmland', 'magic', 'coast'],
	 			'adjacent' : [16, 19, 0, 18] 
	 		},
	 		{
	 			'landDescription' : ['swamp'],
	 			'adjacent' : [17, 2, 20, 1, 19] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['swamp'],
	 			'adjacent' : [18, 27, 28, 20] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['hill', 'magic'],
	 			'adjacent' : [19, 28, 2, 3, 21] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'mine'],
	 			'adjacent' : [20, 24, 28, 3, 4, 22] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['farmland'],
	 			'adjacent' : [21, 24, 5, 4, 23] 
	 		},
	 		{
	 			'landDescription' : ['hill', 'magic'],
	 			'adjacent' : [22, 25, 6, 24] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'cavern'],
	 			'adjacent' : [23, 21, 22, 28] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['farmland'],
	 			'adjacent' : [24, 23, 6, 7, 9, 10, 26] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['swamp', 'magic'],
	 			'adjacent' : [25, 10, 11, 29, 28] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['forest', 'cavern'],
	 			'adjacent' : [28, 29, 12, 13, 15, 19] 
	 		},
	 		{
	 			'landDescription' : ['sea'],
	 			'adjacent' : [27, 19, 20, 21, 24, 26, 29] 
	 		},
	 		{
	 			'landDescription' : ['hill'],
	 			'adjacent' : [28, 27, 12, 11, 26] 
	 		},
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
