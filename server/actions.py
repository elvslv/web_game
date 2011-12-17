from db import Database, User, Message, Game, Map, Adjacency, RegionState, dbi
from sqlalchemy.exc import DatabaseError, DBAPIError, OperationalError
import re
import time
import math
import MySQLdb
import sys
import random
import json
import misc_game
import misc 

from gameExceptions import BadFieldException
from sqlalchemy import func 
from sqlalchemy.exc import SQLAlchemyError
from checkFields import *
from actions_game import *
from misc import *
from ai import AI

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
	user.sid = misc_game.getSid()
	return {'result': 'ok', 'sid': user.sid, 'userId': user.id}

def act_logout(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	leave(user)
	user.sid = None
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
		messages.append({'id': rec.id , 'text': rec.text, 'time': rec.time, 'username': rec.senderUser.name})
	return {'result': 'ok', 'messages': messages}

def act_uploadMap(data):
	name = data['mapName']
	playersNum = int(data['playersNum'])
	result = list()
			
	#checkFiles(data['thumbnail'], data['picture'])
	data['thumbnail'] = data['thumbnail']if 'thumbnail' in data else  misc.DEFAULT_THUMB
	data['picture'] = data['picture']if 'picture' in data else  misc.DEFAULT_MAP_PICTURE

	newMap = Map(name, playersNum, data['turnsNum'], data['thumbnail'], 
		data['picture'])
	dbi.addUnique(newMap, 'mapName')
	mapId = newMap.id
	if 'regions' in data:
		regions = data['regions']
		curId = 1
		for regInfo in regions:
			try:	
				dbi.addRegion(curId, newMap, regInfo)
			except KeyError, e:
				raise BadFieldException('badRegions')
			curId += 1
		i = 0
		for reg in newMap.regions:			
			regInfo = data['regions'][i]
			if reg.id in regInfo['adjacent']:
				raise BadFieldException('badRegions')
			dbi.addAll(map(lambda x: Adjacency(reg.id, x, mapId), regInfo['adjacent']))
			i += 1
	return {'result': 'ok', 'mapId': mapId, 'regions': result} if len(result) else {'result': 'ok', 'mapId': mapId}
	

def act_createGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if user.gameId: raise BadFieldException('alreadyInGame')
	map_ = dbi.getXbyY('Map', 'id', data['mapId'])
	descr = None
	if 'gameDescription' in data:
		descr = data['gameDescription']
	randseed = math.trunc(time.time())
	if 'randseed' in data:
		randseed = data['randseed']
	ai = data['ai'] if 'ai' in data else 0
	if ai > map_.playersNum:
		raise BadFieldException('tooManyPlayersForMap')
	newGame = Game(data['gameName'], descr, map_, randseed, data['ai'] if 'ai' in\
		data else None)
	dbi.addUnique(newGame, 'gameName')
	initRegions(map_, newGame)
	
	if ai < map_.playersNum:
		user.game = newGame
		user.priority = 1
		user.inGame = True
		dbi.flush(user)
		if not misc.TEST_MODE:
			data['randseed'] = randseed
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
	if not (game and user.inGame): raise BadFieldException('notInGame')
	misc_game.leave(user)
	dbi.updateGameHistory(game, data)
	return {'result': 'ok'}

def act_doSmth(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	return {'result': 'ok'}

def createDefaultMaps():
	if misc.TEST_MODE:
		for map_ in misc.defaultMaps:
			act_uploadMap(map_)
	else:
		act_uploadMap(misc.defaultMaps[7])

def act_createDefaultMaps(data):
	createDefaultMaps()
	return {'result': 'ok'}

def act_resetServer(data):
	misc.LAST_SID = 0
	misc.LAST_TIME = 0
	if 'randseed' in data:
		misc.TEST_RANDSEED = data['randseed']
	else:
		misc.TEST_RANDSEED = 21425364547
	random.seed(misc.TEST_RANDSEED)
	dbi.clear()
	if not misc.TEST_MODE: createDefaultMaps()
	#user = User('user', '123456')
	#dbi.add(user)
	return {'result': 'ok'}

def act_saveGame(data):
	result = list()
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	for action in game.gameHistory:
		result.append(json.loads(action.action))
	return {'result': 'ok', 'actions': result}

def act_loadGame(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	if game: dbi.clearGame(game)
	for act in data['actions']:
		if act['action'] in ('register', 'uploadMap', 'login', 'logout', 'saveGame', 
							'loadGame', 'resetServer', 'createDefaultMaps'):
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

def act_getMapList(data):
	result = {'result': 'ok'}
	result['maps'] = list()
	maps = dbi.query(Map).all()
	for map_ in maps:
		result['maps'].append(getMapState(map_.id))
	return result

def act_getGameList(data):
	result = {'result': 'ok'}
	games = dbi.query(Game).filter(Game.state != GAME_ENDED).all()
	result['games'] = list()
	gameAttrs = ['id', 'name', 'descr', 'state', 'turn', 'activePlayerId', 'mapId']
	gameAttrNames = ['gameId', 'gameName', 'gameDescription', 'state', 
		'turn', 'activePlayerId', 'mapId']
		
	if not misc.TEST_MODE:
		gameAttrs.append('aiRequiredNum')
		gameAttrNames.append('aiRequiredNum')
		
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
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		curGame['maxPlayersNum'] = game.map.playersNum
		curGame['turnsNum'] = game.map.turnsNum
		result['games'].append(curGame)
	return result

def act_getGameState(data):
	return {'result': 'ok', 'gameState': getGameState(dbi.getXbyY('Game', 'id', 
		data['gameId']))}

def act_getVisibleTokenBadges(data):
	return {'result': 'ok', 'visibleTokenBadges': getVisibleTokenBadges(data['gameId'])}

def act_aiJoin(data):
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	if game.state != GAME_WAITING:
		raise BadFieldException('badGameState')
	maxPlayersNum = game.map.playersNum
	if len(game.players) >= maxPlayersNum:
		raise BadFieldException('tooManyPlayers')
	maxPriority = max(game.players, key=lambda x: x.priority).priority if len(game.players) else 0
	aiCnt = len(filter(lambda x: x.isAI == True, game.players))
	ai = User('AI%d' % aiCnt, None, True)
	ai.sid = getSid()
	ai.gameId = game.id
	ai.isReady = True
	ai.priority = maxPriority + 1
	ai.inGame = True
	dbi.add(ai)
	dbi.flush(ai)
	game.aiRequiredNum -= 1
	readyPlayersNum = dbi.query(User).filter(User.gameId == game.id).filter(User.isReady==True).count()
	if maxPlayersNum == readyPlayersNum:
		misc_game.startGame(game, ai, data)
	return {'result': 'ok', 'sid' : ai.sid, 'id' : ai.id}

def doAction(data, check = True):
	try:
		dbi.session = dbi.Session()
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			raise BadFieldException('badAction')
		if check: checkFieldsCorrectness(data)
		res = globals()[func](data)
		dbi.commit()
		return res
	except BadFieldException, e: 
		print e
		dbi.rollback()
		return {'result': e.value}
	except (DatabaseError, DBAPIError, OperationalError), e:
		print e
		dbi.rollback()
		return {'result': 'databaseError', 'statement': str(e.statement) if ('statement' in e) else None, 
			'params': str(e.params) if ('params' in e) else None, 'orig': str(e.orig) if ('orig' in e) else None}
	except Exception, e:
		print e
		dbi.rollback()
		raise e
	finally:
		dbi.Session.remove()
