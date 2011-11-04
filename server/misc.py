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
				'landDescription' : ['border', 'coast', 'magic', 'forest'],  		#1
				'coordinates' : [[0, 0], [0, 128], [46, 145], [125, 140], [103, 0]],
	 			'adjacent' : [2, 6],
				'bonusCoords' : [74, 30],
				'raceCoords': [31, 36],
				'powerCoords' : [26, 96]
	 		},
			{	
	 			'landDescription' : ['border', 'coast', 'magic', 'sea'], 			#2
				'coordinates' : [[103, 0], [125, 140], [202, 103], [258, 101], [275, 77], [264, 0]],
	 			'adjacent' : [1, 3, 6, 7],
				'raceCoords': [184, 73],
				'powerCoords' : [234, 53]
	 		},			
			
			{	
	 			'landDescription' : ['coast', 'magic', 'farmland'],					#3  
				'coordinates' : [[264, 0], [275, 77], [258, 101], [273, 137], [295, 142], [391, 109], [409, 94], [393, 42], [403, 0]],
	 			'adjacent' : [2, 7, 6, 8],
				'bonusCoords' : [307, 94],
				'raceCoords': [330, 32],
				'powerCoords' : [364, 83]
	 		},
		
			{		
	 			'landDescription' : ['border', 'coast', 'mine', 'forest'],			#4 
	 			'adjacent' : [3, 5, 8, 9, 10],
				'coordinates' : [[403, 0], [392, 42], [409, 94], [391, 109], [422, 176], [508, 158], [535, 104], [502, 78], [555, 0]],
				'raceCoords': [8, 412],
				'powerCoords' : [444, 39],
				'bonusCoords' : [459, 75]
	 		},

			{	
	 			'landDescription' : ['border', 'swamp', 'cavern'], 					#5
				'coordinates' : [[555, 0],  [502, 78], [535, 104], [630, 120], [630, 0]],
	 			'adjacent' : [4, 10],
				'raceCoords': [560, 4],
				'powerCoords' : [570, 55],
				'bonusCoords' : [548, 68]
	 		},
			
			{	
	 			'landDescription' : ['border', 'coast', 'hill'],					#6
				'coordinates' : [[0, 128], [46, 145], [125, 140], [130, 253], [89, 235], [0, 279]],		
	 			'adjacent' : [1, 2, 7, 11],
				'raceCoords': [63, 145],
				'powerCoords' : [6, 195]
	 		},

			{																		#7
	 			'landDescription' : ['mountain', 'coast', 'mine', 'mountain'],  
	 			'adjacent' : [2, 3, 6, 8, 11, 12],
				'coordinates' : [[125, 140], [130, 253], [160, 251], [268, 218], [303, 172], [295, 142], [273, 137], [258, 101], [202, 103]],
				'bonusCoords': [263, 166],
				'raceCoords': [150, 190],
				'powerCoords' : [167, 35],
	 		},

			{	
	 			'landDescription' : [ 'coast', 'hill'], 							#8
	 			'adjacent' : [3, 4, 7, 9, 12, 13],
				'coordinates' : [[268, 218], [303, 172], [295, 142], [391, 109], [422, 176], [446, 232], [393, 273], [348, 248], [309, 251]],
				'raceCoords': [300, 191],
				'powerCoords' : [333, 137],
	 		},

			{																		#9
	 			'landDescription' : ['sea'],  
				'coordinates' : [[393, 273], [446, 232], [422, 176], [508, 158], [547, 238], [565, 271], [508, 314]],
	 			'adjacent' : [4, 8, 10, 13, 14],
				'raceCoords': [448, 240],
				'powerCoords' : [453, 180]
 			},

			{																		#10
	 			'landDescription' : ['border', 'coast', 'mountain'],
	 			'adjacent' : [4, 5, 9, 14],
				'coordinates' : [[508, 158],  [535, 104], [630, 120], [630, 240], [547, 238]],
				'raceCoords': [546, 180],
				'powerCoords' : [536, 123]
	 		},

			{																		#11
	 			'landDescription' : ['border', 'sea'],  
	 			'adjacent' : [6, 7, 12, 15],
				'coordinates' : [[0, 279],[89, 235],[130, 253], [160, 251], [155, 340], [113, 343], [0, 375]],
				'raceCoords': [7, 305],
				'powerCoords' : [65, 253]
	 		},

			{																		#12
	 			'landDescription' : ['coast', 'farmland'], 
				'coordinates' : [[160, 251], [155, 340], [216, 339], [278, 329], [310, 287], [309, 251], [268, 218]],
	 			'adjacent' : [7, 8, 11, 13, 15, 17],
				'raceCoords': [214, 253],
				'powerCoords' : [163, 287]
	 		},

			{																		#13
	 			'landDescription' : ['coast', 'forest'],  
				'coordinates' : [[278, 329], [310, 287], [309, 251], [348, 248], [393, 273],  [508, 314], [512, 371], [405, 410]],
	 			'adjacent' : [8, 9, 12, 14, 17, 18, 19],
				'raceCoords': [380, 313],
				'powerCoords' : [318, 215]
	 		},

			{	
	 			'landDescription' : ['border', 'coast', 'magic', 'farmland'],		#14
				'coordinates' : [[508, 314], [512, 371], [556, 415], [630, 416], [630, 240], [547, 238], [565, 271]], 
	 			'adjacent' : [9, 10, 13, 19, 20],
				'bonusCoords' : [599, 275],
				'raceCoords': [546, 348],
				'powerCoords' : [565, 287]
		
	 		},

			{																		#15
	 			'landDescription' : ['border', 'coast', 'magic', 'swamp'], 
	 			'adjacent' : [11, 12, 16, 17],
				'coordinates' : [[0, 375], [113, 343], [155, 340],[216, 339],[245, 385], [184, 465], [0, 421]],
				'bonusCoords' : [192, 379],
				'raceCoords': [87, 375],
				'powerCoords' : [28, 376] 
			},

			{	
	 			'landDescription' : ['border', 'hill', 'cavern'],					#16
				'coordinates' : [[0, 421], [184, 465], [186, 515], [0, 515]],
				'bonusCoords' : [129, 483],
				'raceCoords': [62, 458],
				'powerCoords' : [6, 458],
	 			'adjacent' : [15, 17]
	 		},

			{																		#17
	 			'landDescription' : ['border', 'mountain', 'mine'],  
	 			'adjacent' : [12, 13, 15, 16, 18],
				'coordinates' : [[216, 339], [278, 329], [335, 365], [289, 515], [186, 515], [184, 465], [245, 385]],
				'bonusCoords' : [273, 360],
				'raceCoords': [202, 460],
				'powerCoords' : [244, 398]
	 		},

			{																		#18
	 			'landDescription' : ['border', 'cavern', 'hill'],  
				'coordinates' : [[289, 515], [335, 365], [405, 410], [408, 515]],
				'bonusCoords' : [378, 486],
	 			'adjacent' : [13, 17, 19],
				'raceCoords': [324, 411],
				'powerCoords' : [308, 464]
	 		},

			{																		#19
	 			'landDescription' : ['border', 'mine', 'swamp'],
				'coordinates' : [[408, 515], [405, 410], [512, 371], [556, 415], [518, 468], [523, 515]],
	 			'adjacent' : [13, 14, 18, 20],
				'bonusCoords' : [514, 418],
				'raceCoords': [419, 411],
				'powerCoords' : [437, 466]
	 		},

			{																		#20
	 			'landDescription' : ['border', 'mountain'], 
				'coordinates' : [[523, 515], [518, 468], [556, 415], [630, 416], [630, 515]],
				'adjacent' : [14, 19],
				'raceCoords': [529, 466],
				'powerCoords' : [582, 422]
			}
		],
		'thumbnail': 'maps/map1Thumb.jpg', 'picture': 'maps/map1.jpg'
	}
];
