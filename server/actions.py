import editDb
import re
import time
import math
import MySQLdb
import sys
import random
import races

from gameExceptions import BadFieldException
from checkFields import *
from editDb import query, fetchall, fetchone, lastId, commit, rollback
from actions_game import *
from misc_game import *
from misc import *

def createDefaultRaces(): 
	pass
		
def act_register(data):
	username = data['username']
	passwd = data['password']
	if  not re.match(misc.usrnameRegexp, username, re.I):
		raise BadFieldException('badUsername')
	if  not re.match(misc.pwdRegexp, passwd, re.I):
		raise BadFieldException('badPassword')

	if query('SELECT 1 FROM Users WHERE Username=%s', username):
		raise BadFieldException('usernameTaken')
	query('INSERT INTO Users(Username, Password) VALUES (%s, %s)',
		username, passwd)
	return {'result': 'ok'}

def act_login(data):
	username = data['username']
	passwd = data['password']
	if not query('SELECT 1 FROM Users WHERE Username=%s AND Password=%s', username, passwd):
		raise BadFieldException('badUsernameOrPassword')

	while 1:
		sid = misc.generateSidForTest() if misc.TEST_MODE else random.getrandbits(30)
		if not query('SELECT 1 FROM Users WHERE Sid=%s', sid):
			break
	query('UPDATE Users SET Sid=%s WHERE Username=%s', sid, username)
	return {'result': 'ok', 'sid': sid}

def act_logout(data):
	sid = data['sid']
	if not query('UPDATE Users SET Sid=NULL WHERE Sid=%s', sid):
		raise BadFieldException('badSid')
	return {'result': 'ok'}

def act_sendMessage(data):
	userId = getIdBySid(data['sid'])[0]	
	if misc.TEST_MODE:
		msgTime = misc.generateTimeForTest()
	else:
		msgTime = math.trunc(time.time())
	
	text = data['text']
	query('INSERT INTO Chat(UserId, Message, Time) VALUES (%s, %s, %s)', 
		userId, text, msgTime) 
	return {'result': 'ok', 'time': msgTime}

def act_getMessages(data):
	since = data['since']
	query('SELECT UserId, Message, Time FROM Chat WHERE Time > %s ORDER BY Time', since)
	records =  fetchall()
	records = records[-100:]
	messages = []
	for rec in records:
		userId, text, msgTime = rec
		messages.append({'userId': userId, 'text': text, 'time': msgTime})
	return {'result': 'ok', 'messages': messages}

def act_createDefaultMaps(data):
	for map in misc.defaultMaps:
		act_uploadMap(map)
	return {'result': 'ok'}

def act_uploadMap(data):
	name = checkIsUnique('Maps', 'MapName', data['mapName'])
	players = int(data['playersNum'])
	query('INSERT INTO Maps(MapName, PlayersNum, TurnsNum) VALUES(%s, %s, %s)', name, 
		players, data['turnsNum'])
	mapId = lastId()
	if 'regions' in data:
		regions = data['regions']
		curRegion = 1
		for region in regions:
			try:	
				query(checkRegionCorrectness(region), mapId, curRegion, region['population'])
				#add links in graph
				for n in region['adjacent']:
					query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, 
						SecondRegionId, MapId) VALUES(%s, %s, %s)""", curRegion,
						n, mapId)
					query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, 
						SecondRegionId, MapId) VALUES(%s, %s, %s)""", n,
						curRegion, mapId)
				curRegion += 1
			except KeyError:
				raise BadFieldException('badRegion')
	return {'result': 'ok', 'mapId': mapId}
	
def addNewRegions(mapId, gameId):
	query('SELECT RegionId, DefaultTokensNum FROM Regions WHERE MapId=%s', mapId)
	row = fetchall()
	result = list()
	for region in row:
		query("""INSERT INTO CurrentRegionState(RegionId, GameId, TokensNum)
			VALUES(%s, %s, %s)""", region[0], gameId, region[1])
	return result

def act_createGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')
	mapId = extractValues('Maps', ['MapId'], [data['mapId']])
	name = checkIsUnique('Games', 'GameName', data['gameName'])
	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']
	query("""INSERT INTO Games(GameName, GameDescr, MapId, PlayersNum, State) 
		VALUES(%s, %s, %s, %s, %s)""", name, descr, mapId, 1, GAME_WAITING)
	gameId = lastId()
	addNewRegions(mapId, gameId)
	query('UPDATE Users SET GameId=%s, isReady=0, Priority=1 WHERE Id=%s', gameId, userId)
	updateGameHistory(gameId, data)
	return {'result': 'ok', 'gameId': gameId}
	
def act_getGameList(data):
	result = {'result': 'ok'}
	query('SELECT * FROM Games')
	games = fetchall()
	result['games'] = list()

	gameRowNames = ['gameId', 'gameName', 'gameDescr', 'playersNum', 'state', 'turn', 
		'activePlayer']
	mapRowNames = ['mapId', 'mapName', 'playersNum', 'turnsNum']
	playerRowNames = ['userId', 'username', 'state', 'sid']

	for game in games:
		curGame = dict()

		for i in range(len(gameRowNames)):
			if not (gameRowNames[i] == 'gameDescr' and not game[i]):
				curGame[gameRowNames[i]] = game[i]

		gameId = game[0]
		mapId = game[len(game) - 1]

		query('SELECT * FROM Maps WHERE MapId=%s', mapId)
		map = fetchone()
		curGame['map'] = dict()
		for i in range(len(mapRowNames)):
			curGame['map'][mapRowNames[i]] = map[i]

		query("""SELECT Id, Username, IsReady, Sid FROM Users WHERE GameId=%s 
			ORDER BY Priority ASC""", gameId)
		players = fetchall()
		resPlayers = list()
		priority = 0
		for player in players:
			curPlayer = dict()
			for i in range(len(playerRowNames)):
				curPlayer[playerRowNames[i]] = player[i]
			priority += 1	
			curPlayer['priority'] = priority
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		result['games'].append(curGame)
	return result

def act_getMapState(data):
	return {'result': 'ok', 'mapState': getMapState(data['mapId'])}

def act_getGameState(data):
	gameQueryFields = ['GameId', 'GameName', 'GameDescr', 'PlayersNum', 'State', 
		'Turn', 'ActivePlayer', 'MapId']
	gameResFields = ['gameId', 'gameName', 'gameDescription', 'currentPlayersNum', 
		'state', 'currentTurn', 'activePlayerId']
		
	game = extractValues('Games', gameFields, data['gameId'])
	gameId = game[0]
	mapId = game[len(gameQueryFields) - 1]
	result = dict()
	for i in range(len(gameResFields)):
		result[gameResFields[i]] = game[i]
		
	result['map'] = getMapState(mapId, gameId)
	query('SELECT Id FROM Users WHERE GameId=%s', gameId)
	
	users = list()
	usersDescr = fetchall()
	for user in usersDescr:
		users.append(getUserState(user[0]))
	result['users'] = users
	
	result['visibleTokenBadges'] = getVisibleTokenBadges(gameId) 
	
	return {'result': ok, 'gameState': result}

def act_joinGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')

	gameId, playersNum, mapId, state = extractValues('Games', ['GameId', 
		'PlayersNum', 'MapId', 'State'],  [data['gameId']])
	if state != GAME_WAITING:
		raise BadFieldException('badGameState')
	query('SELECT PlayersNum From Maps WHERE MapId=%s', mapId)
	maxPlayersNum = fetchone()[0]
	if playersNum >= maxPlayersNum:
		raise BadFieldException('tooManyPlayers')

	query('SELECT MAX(Priority) FROM Users WHERE GameId=%s', gameId)
	priority = fetchone()[0]
	query('UPDATE Users SET GameId=%s, IsReady=0, Priority=%s+1 WHERE Id=%s', 
		gameId, priority, userId)
	query('UPDATE Games SET PlayersNum=PlayersNum+1 WHERE GameId=%s', gameId)
	updateGameHistory(gameId, data)
	return {'result': 'ok'}
	
def act_leaveGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if not gameId: raise BadFieldException('notInGame')

	query('SELECT PlayersNum FROM Games WHERE GameId=%s', gameId)
	curPlayersNum = fetchone()[0]
	query('UPDATE Users SET GameId=NULL, IsReady=NULL, Priority=NULL WHERE Id=%s',
		userId)
	query("""UPDATE CurrentRegionState SET TokenBadgeId=NULL, Encampment=0, 
		HoleInTheGround=FALSE, Dragon=FALSE, Fortress=FALSE, Hero=FALSE
		WHERE TokenBadgeId=(SELECT TokenBadgeId FROM TokenBadges WHERE OwnerId=%s)""", 
		userId)
	if curPlayersNum > 1: 
		query('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
	else:
		query('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', 
			GAME_ENDED, gameId)
	updateGameHistory(gameId, data)
	return {'result': 'ok'}

def act_doSmth(data):
	userId = getIdBySid(data['sid'])[0]
	return {'result': 'ok'}

def act_resetServer(data):
	misc.LAST_SID = 0
	misc.LAST_TIME = 0
	misc.TEST_MODE = True
	if 'randseed' in data:
		misc.TEST_RANDSEED = data['randseed']
	else:
		misc.TEST_RANDSEED = 21425364547
	random.seed(misc.TEST_RANDSEED)
	editDb.clearDb()
	createDefaultRaces()
	return {'result': 'ok'}

def act_saveGame(data):
	gameId = extractValues('Games', ['GameId'], data['gameId'])
	query("""SELECT Actions FROM GameHistory WHERE GameId=%s ORDER BY 
		GameHistoryId ASC""")
	row = fetchall()
	result = list()
	for action in row:
		result.append(action[0])

	return {'result': 'ok', 'actions': result}

def act_loadGame(data):
	for act in data:
		if 'userId' in act:
			sid = extractValues('Users', ['Id', 'Sid'], [data['userId']])[1]
			del act['userId']
			act['sid'] = sid

	for act in data:
		doAction(act)

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			raise BadFieldException('badAction')
		checkFieldsCorrectness(data);
		res = globals()[func](data)
		commit()
		return res
	except MySQLdb.Error, e:
		rollback()
		return e
