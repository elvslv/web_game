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
TEST_MODE=False
TEST_RANDSEED = 12345
global LAST_SID, LAST_TIME

GAME_START = 0
GAME_WAITING = 1
GAME_PROCESSING = 2
GAME_ENDED = 3
GAME_FINISH_TURN = 4
GAME_SELECT_RACE = 5
GAME_CONQUER = 6
GAME_DECLINE = 7
GAME_REDEPLOY = 8
GAME_THROW_DICE = 9
GAME_DEFEND = 12
GAME_CHOOSE_FRIEND = 13
GAME_UNSUCCESSFULL_CONQUER = 14

ATTACK_CONQUER = 0
ATTACK_DRAGON = 1
ATTACK_ENCHANT = 2

DEFAULT_THUMB = 'maps/mapThumb.jpg'
DEFAULT_MAP_PICTURE = 'maps/map.jpg'

possiblePrevCmd = {
	GAME_FINISH_TURN: [GAME_DECLINE, GAME_REDEPLOY, GAME_CHOOSE_FRIEND],
	GAME_SELECT_RACE: [GAME_START, GAME_FINISH_TURN],
	GAME_CONQUER: [GAME_CONQUER, GAME_SELECT_RACE, GAME_FINISH_TURN,
	GAME_THROW_DICE, GAME_DEFEND],
	GAME_DECLINE: [GAME_FINISH_TURN, GAME_REDEPLOY],
	GAME_REDEPLOY: [GAME_CONQUER, GAME_THROW_DICE, GAME_DEFEND, 
	GAME_UNSUCCESSFULL_CONQUER],
	GAME_THROW_DICE: [GAME_SELECT_RACE, GAME_FINISH_TURN, GAME_CONQUER, 
	GAME_DEFEND],
	GAME_DEFEND: [GAME_CONQUER],
	GAME_CHOOSE_FRIEND: [GAME_REDEPLOY]
}

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
		{'name': 'text', 'type': unicode, 'mandatory': True, 'max':300}
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
		},
		{
			'name': 'thumbnail',
			'mandatory': True,
			'type': unicode
		},
		{
			'name': 'picture',
			'mandatory': True,
			'type': unicode
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
	'getMapList': [
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
		},
                {'name': 'visibleRaces', 'type': list, 'mandatory': False},
                {'name': 'visibleSpecialPowers', 'type': list, 'mandatory': 
False}
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
		{'name': 'raceId', 'type': int, 'min': 0, 'max': RACE_NUM, 'mandatory': 
False}
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
	'saveGame': [
		{'name': 'sid', 'type': int, 'mandatory': False},
		{'name': 'gameId', 'type': int, 'mandatory': True}
	],
	'loadGame': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'actions', 'type': list, 'mandatory': True}
	],
	'redeploy': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'raceId', 'type': int, 'mandatory': False},
		{'name': 'regions', 'type': list, 'mandatory': True},
		{'name': 'encampments', 'type': list, 'mandatory': False},
		{'name': 'fortified', 'type': dict, 'mandatory': False},
		{'name': 'heroes', 'type': list, 'mandatory': False}
	],
	'defend': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'regions', 'type': list, 'mandatory': True}
	],
        'enchant': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'regionId', 'type': int, 'mandatory': True}
	],
	'getVisibleTokenBadges': [
		{'name': 'gameId', 'type': int, 'mandatory': True}
	],
	'resetServer': [{'name': 'sid', 'type': int, 'mandatory': False}],
	'throwDice': [{'name': 'sid', 'type': int, 'mandatory': True}, 
		{'name': 'dice', 'type': int, 'mandatory': False}],
	'getGameState': [{'name': 'gameId', 'type': int, 'mandatory': True}],
	'getMapState': [{'name': 'mapId', 'type': int, 'mandatory': True}],
	'selectFriend': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'friendId', 'type': int, 'mandatory': True}],
	'dragonAttack': [
		{'name': 'sid', 'type': int, 'mandatory': True},
		{'name': 'regionId', 'type': int, 'mandatory': True}
	]
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
	{'mapName': 'defaultMap1', 'playersNum': 2, 'turnsNum': 5, 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE}, 
	{'mapName': 'defaultMap2', 'playersNum': 3, 'turnsNum': 5, 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE},
	{'mapName': 'defaultMap3', 'playersNum': 4, 'turnsNum': 5, 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE},
	{'mapName': 'defaultMap4', 'playersNum': 5, 'turnsNum': 5, 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE},
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
	 	], 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE
	},
	{
		'mapName': 'defaultMap6', 
		'playersNum': 2, 
		'turnsNum': 7,
	 	'regions' : 
	 	[
	 		{
	 			'landDescription' : ['sea', 'border'], #1
	 			'adjacent' : [2, 17, 18] 
	 		},
	 		{
	 			'landDescription' : ['mine', 'border', 'coast', 'forest'], #2
	 			'adjacent' : [1, 18, 19, 3] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain'], #3
	 			'adjacent' : [2, 19, 21, 4] 
	 		},
	 		{
	 			'landDescription' : ['farmland', 'border'], #4
	 			'adjacent' : [3, 21, 22, 5] 
	 		},
	 		{
	 			'landDescription' : ['cavern', 'border', 'swamp'], #5
	 			'adjacent' : [4, 22, 23, 6] 
	 		},
			{
				'population': 1,
	 			'landDescription' : ['forest', 'border'], #6
	 			'adjacent' : [5, 23, 7] 
	 		},
			{
	 			'landDescription' : ['mine', 'border', 'swamp'], #7
	 			'adjacent' : [6, 23, 8, 24, 26] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain', 'coast'], #8
	 			'adjacent' : [7, 26, 10, 9, 24] 
	 		},
	 		{
	 			'landDescription' : ['border', 'sea'], #9
	 			'adjacent' : [8, 10, 11] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['cavern', 'coast'], #10
	 			'adjacent' : [9, 8, 11, 26] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['mine', 'coast', 'forest', 'border'], #11
	 			'adjacent' : [10, 26, 27, 12] 
	 		},
	 		{
	 			'landDescription' : ['forest', 'border'], #12
	 			'adjacent' : [11, 27, 30, 13] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'border'], #13
	 			'adjacent' : [12, 30, 28, 14] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'border'], #14
	 			'adjacent' : [13, 28, 16, 15] 
	 		},
	 		{
	 			'landDescription' : ['hill', 'border'], #15
	 			'adjacent' : [14, 16] 
	 		},
	 		{
	 			'landDescription' : ['farmland', 'magic', 'border'], #16
	 			'adjacent' : [15, 20, 28, 17] 
	 		},
	 		{
	 			'landDescription' : ['border', 'mountain', 'cavern', 'mine', #17 
	 				'coast'],
	 			'adjacent' : [16, 20, 1, 18] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['farmland', 'magic', 'coast'], #18
	 			'adjacent' : [17, 20, 1, 19] 
	 		},
	 		{
	 			'landDescription' : ['swamp'], #19
	 			'adjacent' : [18, 3, 21, 2, 20] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['swamp'], #20
	 			'adjacent' : [19, 28, 29, 21] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['hill', 'magic'], #21
	 			'adjacent' : [20, 29, 3, 4, 22] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'mine'], #22
	 			'adjacent' : [21, 25, 29, 4, 5, 23] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['farmland'], #23
	 			'adjacent' : [22, 25, 6, 5, 24] 
	 		},
	 		{
	 			'landDescription' : ['hill', 'magic'], #24
	 			'adjacent' : [23, 26, 7, 25, 8] 
	 		},
	 		{
	 			'landDescription' : ['mountain', 'cavern'], #25
	 			'adjacent' : [24, 22, 23, 29] 
	 		},
	 		{
	 			'landDescription' : ['farmland'], #26
	 			'adjacent' : [25, 24, 7, 8, 10, 11, 27] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['swamp', 'magic'], #27
	 			'adjacent' : [26, 11, 12, 30, 29] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['forest', 'cavern'], #28
	 			'adjacent' : [29, 30, 13, 14, 16, 20] 
	 		},
	 		{
	 			'landDescription' : ['sea'],
	 			'adjacent' : [28, 20, 21, 22, 25, 27, 30]  #29
	 		},
	 		{
	 			'landDescription' : ['hill'],  #30
	 			'adjacent' : [29, 28, 13, 12, 27] 
	 		},
	 	], 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE
	},	{
		'mapName': 'defaultMap7', 
		'playersNum': 2, 
		'turnsNum': 5,
	 	'regions' : 
	 	[
	 		{
	 			'landDescription' : ['border', 'mountain', 'mine', 'farmland','magic'],
	 			'adjacent' : [2] 
	 		},
	 		{
	 			'landDescription' : ['mountain'],
	 			'adjacent' : [1, 3] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['mountain', 'mine'],
	 			'adjacent' : [2, 4] 
	 		},
	 		{
	 			'population': 1,
	 			'landDescription' : ['mountain'],
	 			'adjacent' : [3, 5] 
	 		},
			{
	 			'landDescription' : ['mountain', 'mine'],
	 			'adjacent' : [4] 
	 		}
	 	], 
		'thumbnail': DEFAULT_THUMB, 'picture': DEFAULT_MAP_PICTURE
	},
	{
		'mapName': 'map1', 
		'playersNum': 2, 
		'turnsNum': 10,
	 	'regions' : 
	 	[
	 		{
				'population': 1,
	 			'landDescription' : ['border', 'coast', 'forest', 'magic'],  
	 			'adjacent' : [2, 6],
				'x_race': 15,
				'y_race': 15,
				'x_power': 15,
				'y_power': 80,
				'x_min': 0,
				'x_max': 104,
				'y_min': 0,
				'y_max': 145
	 		},
			{
	 			'landDescription' : ['border', 'sea'],  
	 			'adjacent' : [1, 3, 6, 7],
				'x_race': 130,
				'y_race': 8,
				'x_power': 130,
				'y_power': 64,
				'x_min': 113,
				'x_max': 261,
				'y_min': 0,
				'y_max': 101
	 		},{
	 			'landDescription' : ['border', 'coast', 'farmland', 'magic'],  
	 			'adjacent' : [2, 4, 7, 8],
				'x_race': 285,
				'y_race': 8,
				'x_power': 317,
				'y_power': 65,
				'x_min': 267,
				'x_max': 391,
				'y_min': 0,
				'y_max': 114
	 		},
			{
				'population': 1,
	 			'landDescription' : ['border', 'coast', 'forest', 'mine'],  
	 			'adjacent' : [3, 5, 8, 9, 10],
				'x_race': 8,
				'y_race': 412,
				'x_power': 419,
				'y_power': 65,
				'x_min': 407,
				'x_max': 515,
				'y_min': 0,
				'y_max': 155
	 		},
			{
	 			'landDescription' : ['border', 'swamp', 'cavern'],  
	 			'adjacent' : [4, 10],
				'x_race': 560,
				'y_race': 4,
				'x_power': 570,
				'y_power': 55,
				'x_min': 553,
				'x_max': 634,
				'y_min': 0,
				'y_max': 112
	 		},
			{
	 			'landDescription' : ['border', 'coast', 'hill'],  
	 			'adjacent' : [1, 2, 7, 11],
				'x_race': 63,
				'y_race': 165,
				'x_power': 6,
				'y_power': 195,
				'x_min': 0,
				'x_max': 144,
				'y_min': 153,
				'y_max': 231
	 		},
			{
	 			'landDescription' : ['mountain', 'coast', 'mountain', 'mine', 'cavern'],  
	 			'adjacent' : [2, 3, 6, 8, 11, 12],
				'x_race': 150,
				'y_race': 190,
				'x_power': 167,
				'y_power': 35,
				'x_min': 149,
				'x_max': 278,
				'y_min': 126,
				'y_max': 229
	 		},
			{
				'population': 1,
	 			'landDescription' : ['mountain', 'coast', 'hill'],  
	 			'adjacent' : [3, 4, 7, 9, 12, 13],
				'x_race': 300,
				'y_race': 191,
				'x_power': 333,
				'y_power': 137,
				'x_min': 303,
				'x_max': 426,
				'y_min': 144,
				'y_max': 254
	 		},
			{
	 			'landDescription' : ['sea'],  
	 			'adjacent' : [4, 8, 10, 13, 14],
				'x_race': 448,
				'y_race': 240,
				'x_power': 453,
				'y_power': 180,
				'x_min': 426,
				'x_max': 529,
				'y_min': 181,
				'y_max': 304
	 		},
			{
				'population': 1,
	 			'landDescription' : ['border', 'coast', 'mountain'],  
	 			'adjacent' : [4, 5, 9, 14],
				'x_race': 546,
				'y_race': 180,
				'x_power': 536,
				'y_power': 123,
				'x_min': 537,
				'x_max': 634,
				'y_min': 108,
				'y_max': 240
	 		},
			{
	 			'landDescription' : ['border', 'sea'],  
	 			'adjacent' : [6, 7, 12, 15],
				'x_race': 7,
				'y_race': 305,
				'x_power': 65,
				'y_power': 253,
				'x_min': 0,
				'x_max': 158,
				'y_min': 255,
				'y_max': 350
	 		},
			{
	 			'landDescription' : ['coast', 'farmland'],  
	 			'adjacent' : [7, 8, 11, 13, 15, 17],
				'x_race': 214,
				'y_race': 253,
				'x_power': 163,
				'y_power': 287,
				'x_min': 159,
				'x_max': 309,
				'y_min': 249,
				'y_max': 327
	 		},
			{
				'population': 1,
	 			'landDescription' : ['coast', 'forest'],  
	 			'adjacent' : [8, 9, 12, 14, 17, 18, 19],
				'x_race': 380,
				'y_race': 313,
				'x_power': 318,
				'y_power': 295,
				'x_min': 313,
				'x_max': 510,
				'y_min': 282,
				'y_max': 378
	 		},
			{
	 			'landDescription' : ['border', 'coast', 'farmland', 'magic'],  
	 			'adjacent' : [9, 10, 13, 19, 20],
				'x_race': 546,
				'y_race': 348,
				'x_power': 565,
				'y_power': 287,
				'x_min': 531,
				'x_max': 242,
				'y_min': 634,
				'y_max': 407
	 		},
			{
				'population': 1,
	 			'landDescription' : ['border', 'coast', 'swamp', 'magic'],  
	 			'adjacent' : [11, 12, 16, 17],
				'x_race': 87,
				'y_race': 375,
				'x_power': 28,
				'y_power': 376,
				'x_min': 50,
				'x_max': 214,
				'y_min': 342,
				'y_max': 435
	 		},
			{
				'population': 1,
	 			'landDescription' : ['border', 'hill', 'cavern'],  
	 			'adjacent' : [15, 17],
				'x_race': 62,
				'y_race': 458,
				'x_power': 6,
				'y_power': 458,
				'x_min': 0,
				'x_max': 184,
				'y_min': 453,
				'y_max': 515
	 		},
			{
	 			'landDescription' : ['border', 'mountain', 'mine'],  
	 			'adjacent' : [12, 13, 15, 16, 18],
				'x_race': 202,
				'y_race': 460,
				'x_power': 244,
				'y_power': 398,
				'x_min': 223,
				'x_max': 314,
				'y_min': 346,
				'y_max': 515
	 		},
			{
	 			'landDescription' : ['border', 'hill', 'cavern'],  
	 			'adjacent' : [13, 17, 19],
				'x_race': 324,
				'y_race': 411,
				'x_power':308,
				'y_power': 464,
				'x_min': 313,
				'x_max': 407,
				'y_min': 398,
				'y_max': 515
	 		},
			{
				'population': 1,
	 			'landDescription' : ['border', 'swamp', 'mine'],  
	 			'adjacent' : [13, 14, 18, 20],
				'x_race': 419,
				'y_race': 411,
				'x_power': 437,
				'y_power': 466,
				'x_min': 407,
				'x_max': 528,
				'y_min': 391,
				'y_max': 515
	 		},
			{
	 			'landDescription' : ['border', 'mountain'],  
	 			'adjacent' : [14, 19],
				'x_race': 529,
				'y_race': 466,
				'x_power': 582,
				'y_power': 422,
				'x_min': 529,
				'x_max': 634,
				'y_min': 423,
				'y_max': 515
	 		}
	 	],
		'thumbnail': 'maps/map1Thumb.jpg', 'picture': 'maps/map1.jpg'
	}
			
]

