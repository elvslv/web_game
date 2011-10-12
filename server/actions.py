from db import Database, User, Message, Game, Map, Adjacency, RegionState
import re
import time
import math
import MySQLdb
import sys
import random

from gameExceptions import BadFieldException
from sqlalchemy import func 
from sqlalchemy.exc import SQLAlchemyError
from checkFields import *
from actions_game import *
from misc import *

dbi = Database()

	
def act_register(data):
	username = data['username']
	passwd = data['password']
	if  not re.match(misc.usrnameRegexp, username, re.I):
		raise BadFieldException('badUsername')
	if  not re.match(misc.pwdRegexp, passwd, re.I):
		raise BadFieldException('badPassword')
	dbi.addUnique(User(username, passwd), 'username')	
	return {'result': 'ok'}

def act_login(data):
	username = data['username']
	passwd = data['password']
	user = dbi.getUserByNameAndPwd(username, passwd)
	while 1:
		sid = misc.generateSidForTest() if misc.TEST_MODE else random.getrandbits(30)
		if not dbi.getXbyY('User', 'sid', sid, False): break
	user.sid = sid
	return {'result': 'ok', 'sid': sid}

def act_logout(data):
	dbi.getXbyY('User', 'sid', data['sid']).sid = None
	return {'result': 'ok'}

def act_sendMessage(data):
	userId = dbi.getXbyY('User', 'sid', data['sid']).id
	msgTime = misc.generateTimeForTest() if misc.TEST_MODE else math.trunc(time.time())
	text = data['text']
	dbi.add(Message(userId, text, msgTime))
	return {'result': 'ok', 'time': msgTime}

def act_getMessages(data):
	since = data['since']
	records =  dbi.query(Message).filter(Message.time > since).order_by(Message.time).all()[-100:]
	messages = []
	for rec in records:
		messages.append({'userId': rec.sender, 'text': rec.text, 'time': rec.time})
	return {'result': 'ok', 'messages': messages}

def act_uploadMap(data):
	name = data['mapName']
	playersNum = int(data['playersNum'])
	newMap = Map(name, playersNum, data['turnsNum'])
	result = list()
	dbi.addUnique(newMap, 'mapName')
	mapId = newMap.id
	if 'regions' in data:
		regions = data['regions']
		curId = 1
		for regInfo in regions:
			try:	
				dbi.addRegion(curId, newMap, regInfo)
			except KeyError:
				raise BadFieldException('badRegion')
			curId += 1
		i = 0
		for reg in newMap.regions:			#This is quite bad but I didn't manage to find the other way
			regInfo = data['regions'][i]			
			dbi.addNeighbors(reg, map(lambda x: Adjacency(reg.id, x), regInfo['adjacent']))
        		i += 1
	return {'result': 'ok', 'mapId': mapId, 'regions': result} if len(result) else {'result': 'ok', 'mapId': mapId}
	

def initRegions(map, game):
	for region in map.regions:
		regState = RegionState(region, game)
		dbi.add(regState)

def act_createGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if user.gameId: raise BadFieldException('alreadyInGame')
	map_ = dbi.getXbyY('Map', 'id', data['mapId'])
	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']
	newGame = Game(data['gameName'], descr, map_)
	dbi.addUnique(newGame, 'gameName')
	initRegions(map_, newGame)
	user.game = newGame
	user.priority = 1
	return {'result': 'ok', 'gameId': newGame.id}
	

def act_joinGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if user.game: raise BadFieldException('alreadyInGame')
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	if game.state != GAME_WAITING:
		raise BadFieldException('badGameState')
	maxPlayersNum = game.map.playersNum
	if len(game.players) >= maxPlayersNum:
		raise BadFieldException('tooManyPlayers')
	maxPriority = max(game.players, key=lambda x: x.priority).priority
	user.game = game
	user.priority = maxPriority + 1
	return {'result': 'ok'}
	
def act_leaveGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.game: raise BadFieldException('notInGame')
	game = user.game
	user.game = None
	for region in user.regions:
		region.tokenBadgeId = None
		region.Encapment = 0
		region.holeInTheGround = 0
		region.dragon = False
		region.Fortress = False
		region.Hero = False
	if game.players == []:
		game.state = GAME_ENDED
	return {'result': 'ok'}

def act_doSmtn(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	return {'result': 'ok'}

def act_createDefaultMaps(data):				
##	if not misc.TEST_MODE or not dbi.query(Map).count(): 					
	for map_ in misc.defaultMaps:
		act_uploadMap(map_)
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
	#createDefaultRaces()
	dbi.clear()
	return {'result': 'ok'}

def act_saveGame(data):
#	gameId = extractValues('Games', ['GameId'], data['gameId'])
#	query("""SELECT Actions FROM GameHistory WHERE GameId=%s ORDER BY 
#		GameHistoryId ASC""")
#	row = fetchall()
	result = list()
#	for action in row:
#		result.append(action[0])

	return {'result': 'ok', 'actions': result}

def act_loadGame(data):
	pass
#	for act in data:
#		if 'userId' in act:
#			sid = extractValues('Users', ['Id', 'Sid'], [data['userId']])[1]
#			del act['userId']
#			act['sid'] = sid
#
#	for act in data:
#		doAction(act)

def getMapState(mapId, gameId = None):
	map_ = dbi.getXbyY('Map', 'id', mapId)
	result = dict()
	mapAttrs = ['id', 'name', 'playersNum', 'turnsNum']
	mapAttrNames = ['mapId', 'mapName', 'playersNum', 'turnsNum']
	for i in range(len(mapAttrs)):
		result[mapAttrNames[i]] = getattr(map_, mapAttrs[i])
	result['regions'] = list()
	constRegionAttrs = ['id', 'defTokensNum', 'border', 'coast', 'mountain', 
		'sea', 'mine', 'farmland', 'magic', 'forest', 'hill', 'swamp', 'cavern']
	constRegionAttrNames = ['regionId', 'defaultTokensNum', 'border', 'coast', 
		'mountain', 'sea', 'mine', 'farmland', 'magic', 'forest', 'hill', 
		'swamp', 'cavern']
	curRegionAttrs = ['tokenBadgeId', 'ownerId', 'tokensNum', 
		'holeInTheGround', 'encampment', 'dragon', 'fortress', 'hero', 'inDecline']

	for region in map_.regions:
		curReg = dict()
		for i in range(len(constRegionAttrs)):
			curReg[constRegionAttrNames[i]] = getattr(region, constRegionAttrs[i])
		curReg['adjacentRegions'] = region.getNeighbors()
		if gameId:
			curRegState = region.getState()
			for i in range(len(curRegionAttrs)):
				curReg[curRegionAttrs[i]] = getattr(curRegState, curRegionAttrs[i])
		result['regions'].append(curReg)
	return result

def act_getMapState(data):
	return {'result': 'ok', 'mapState': getMapState(data['mapId'])}

def act_getGameList(data):
	result = {'result': 'ok'}
	games = dbi.query(Game)
	result['games'] = list()

	gameAttrs = [ 'activePlayerId', 'id', 'name', 'descr', 'state', 'turn', 
		'mapId']
	gameAttrNames = [ 'activePlayer', 'gameId', 'gameName', 'gameDescr', 'state', 
		'turn', 'mapId']

	playerAttrs = ['id', 'name', 'isReady']
	playerAttrNames = ['userId', 'username', 'isReady']
	for game in games:
		curGame = dict()

		for i in range(len(gameAttrs)):
			if gameAttrs[i] == 'descr':
				continue
			curGame[gameAttrNames[i]] = getattr(game, gameAttrs[i]) 

		players = game.players
		resPlayers = list()
		priority = 0
		for player in players:
			curPlayer = dict()
			for i in range(len(playerAttrs)):
				curPlayer[playerAttrNames[i]] = getattr(player, playerAttrs[i])
			priority += 1	
			curPlayer['priority'] = priority
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		curGame['playersNum'] = len(players)
		result['games'].append(curGame)
	return result

def act_getGameState(data):
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	gameAttrs = ['id', 'name', 'descr', 'state', 'turn', 'activePlayerId']
	gameNameAttrs = ['gameId', 'gameName', 'gameDescription', 'state', 
		'currentTurn', 'activePlayerId']

	result = dict()
	for i in range(len(gameResFields)):
		result[gameNameAttrs[i]] = getattr(game, gameAttrs[i])
		
	result['map'] = getMapState(game.map.id)

	playerAttrs = ['id', 'name', 'isReady', 'coins', 'tokensInHand']
	playerAttrNames = ['userId', 'username', 'isReady', 'coins', 'tokensInHand']

	players = game.players
	resPlayers = list()
	priority = 0
	for player in players:
		curPlayer = dict()
		for i in range(len(playerAttrs)):
			curPlayer[playerAttrs[i]] = getattr(player, playerAttrs[i])

		priority += 1	
		curPlayer['priority'] = priority
		
		if player.currentTokenBadge:
			curTokenBadge = dict()
			curTokenBadge['race'] =  races.racesList[player.currentTokenBadge.raceId].name
			curTokenBadge['specialPower'] =  races.specialPowerList[player.currentTokenBadge.specialPowerId].name
			curPlayer['currentTokenBadge'] = curTokenBadge
			
		if player.declinedTokenBadge:
			declinedTokenBadge = dict()
			declinedTokenBadge['race'] =  races.racesList[player.declinedTokenBadge.raceId].name
			declinedTokenBadge['specialPower'] =  races.specialPowerList[player.declinedTokenBadge.specialPowerId].name
			curPlayer['declinedTokenBadge'] = declinedTokenBadge
			
		resPlayers.append(curPlayer)
	result['players'] = resPlayers
	
	result['visibleTokenBadges'] = getVisibleTokenBadges(gameId) 
	
	return {'result': ok, 'gameState': result}

def getVisibleTokensBadges(gameId):
	game = dbi.getXbyY('Game', 'id', gameId)
	rows = game.tokenBadges()
	result = list()
	for tokenBadge in filter(lambda x: x.position > 0, rows):
		result.append({
			'raceId': races.racesList[tokenBadge.raceId].name, 
			'specialPowerId': races.specialPowerList[tokenBadge.specPowerId].name,
			'position': tokenBadge.position})
	return result

def act_getVisibleTokenBadges(data):

	return {'result': 'ok', 'visibleTokenBadges': getVisibleTokensBadges(data['gameId'])}

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			raise BadFieldException('badAction')
		checkFieldsCorrectness(data)
		res = globals()[func](data)
		dbi.commit()
		return res
	except Exception, e:			##Temporary
		print e
		dbi.rollback()
		raise e
