from db import Database, User, Message, Game, Map, Adjacency, RegionState
import re
import time
import math
import MySQLdb
import sys
import random
import json

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
	return {'result': 'ok', 'sid': sid, 'userId': user.id}

def act_logout(data):
	leave(dbi.getXbyY('User', 'sid', data['sid']))
	return {'result': 'ok'}

def act_sendMessage(data):
	userId = dbi.getXbyY('User', 'sid', data['sid']).id
	msgTime = misc.generateTimeForTest() if misc.TEST_MODE else math.trunc(time.time())
	text = data['text']
	dbi.add(Message(userId, text, msgTime))
	return {'result': 'ok'}

def act_getMessages(data):
	since = data['since']
	records =  dbi.query(Message).filter(Message.id > since).order_by(Message.id).all()[-100:]
	messages = []
	for rec in records:
		messages.append({'id': rec.id , 'text': rec.text, 'time': rec.time, 
			'username': dbi.getXbyY('User', 'id', rec.sender).name})
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
	user.inGame = True
	dbi.updateGameHistory(user.game, data)
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
	user.inGame = True
	user.priority = maxPriority + 1
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}

def act_leaveGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	if not user.inGame: raise BadFieldException('notInGame')
	leave(user)
	dbi.updateGameHistory(game, data)
	return {'result': 'ok'}

def act_doSmth(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	return {'result': 'ok'}

def createDefaultMaps():
	for map_ in misc.defaultMaps:
		act_uploadMap(map_)

def act_resetServer(data):
	misc.LAST_SID = 0
	misc.LAST_TIME = 0
	misc.TEST_MODE = True
	if 'randseed' in data:
		misc.TEST_RANDSEED = data['randseed']
	else:
		misc.TEST_RANDSEED = 21425364547
	random.seed(misc.TEST_RANDSEED)
	dbi.clear()
	createDefaultMaps()
	return {'result': 'ok'}

def act_saveGame(data):
	result = list()
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	row = filter(lambda x: x.gameId == game.id, game.gameHistory)
	for action in row:
		result.append(json.loads(action.action))
	return {'result': 'ok', 'actions': result}

def act_loadGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	for player in game.players:
		player.game = None
	game.clear()
	for act in data['actions']:
		if act['action'] in ('register', 'uploadMap', 'login', 'logout', 'saveGame'
, 'loadGame', 'resetServer', 'createDefaultMaps'):
			raise BadFieldException('illegalAction')
		if 'userId' in act:
			user = dbi.getXbyY('User', 'id', act['userId'])
			del act['userId']
			act['sid'] = user.sid
			
	for act in data['actions']:
		res = doAction(act, False)
	return {'result': 'ok'}

def act_getMapState(data):
	return {'result': 'ok', 'mapState': getMapState(data['mapId'])}

def act_getGameList(data):
	result = {'result': 'ok'}
	games = dbi.query(Game)
	games = filter(lambda x: x.state != GAME_ENDED, games)
	result['games'] = list()

	gameAttrs = [ 'activePlayerId', 'id', 'name', 'descr', 'state', 'turn', 
		'mapId']
	gameAttrNames = [ 'activePlayerId', 'gameId', 'gameName', 'gameDescr', 'state', 
		'turn', 'mapId']

	playerAttrs = ['id', 'name', 'isReady', 'inGame']
	playerAttrNames = ['userId', 'username', 'isReady', 'inGame']
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
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		curGame['maxPlayersNum'] = game.map.playersNum
		curGame['turnsNum'] = game.map.turnsNum
		result['games'].append(curGame)
	return result

def act_getGameState(data):
	return {'result': ok, 'gameState': getGameState(dbi.getXbyY('Game', 'id', 
		data['gameId']))}

def act_getVisibleTokenBadges(data):
	return {'result': 'ok', 'visibleTokenBadges': getVisibleTokensBadges(data['gameId'])}

def doAction(data, check = True):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			raise BadFieldException('badAction')
		if check: checkFieldsCorrectness(data)
		res = globals()[func](data)
		dbi.commit()
		return res
	except Exception, e:			##Temporary
		dbi.rollback()
		raise e
