from db import Database, User
import re
import time
import math
import MySQLdb
import sys
import random
import races

from gameExceptions import BadFieldException
from sqlalchemy import func 
from sqlalchemy.exc import SQLAlchemyError
from checkFields import *
from actions_game import *
from misc_game import *
from misc import *

dbi = Database()

def createDefaultRaces(): 
	pass
		
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
	if not user:
		raise BadFieldException('badUsernameOrPassword')

	while 1:
		sid = misc.generateSidForTest() if misc.TEST_MODE else random.getrandbits(30)
		if not dbi.getUserBySid(sid): break
	user.sid = sid
	dbi.commit()
	return {'result': 'ok', 'sid': sid}

def act_logout(data):
	user = dbi.getUserBySid(data['sid'])
	if not user: raise BadFieldException('badSid')
	user.sid = None
	return {'result': 'ok'}

def act_sendMessage(data):
	userId = dbi.getUserBySid(data['sid']).id
	msgTime = misc.generateTimeForTest() if misc.TEST_MODE else math.trunc(time.time())
	text = data['text']
	dbi.add(Message(userId, text, msgTime))
	return {'result': 'ok', 'time': msgTime}

def act_getMessages(data):
	since = data['since']
	records =  dbi.query(Message).filter_by(Message.time > since).order_by(Message.time).all()[-100:]
	messages = []
	for rec in records:
		messages.append({'userId': rec.sender, 'text': rec.text, 'time': rec.time})
	return {'result': 'ok', 'messages': messages}

def act_createDefaultMaps(data):
	for map in misc.defaultMaps:
		act_uploadMap(map)
	return {'result': 'ok'}

def act_uploadMap(data):
	name = data['mapName']
	players = int(data['playersNum'])
	newMap = Map(name, playersNum, data['turnsNum'])
	dbi.addUnique(newMap, 'mapName')
	mapId = newMap.id
	result = list()
	if 'regions' in data:
		regions = data['regions']
	#	maxId = dbi.query(func.max(Region.id)) 
	#	if not maxId: maxId = 0
	#	curRegion = maxId
		for region in regions:
			try:	
				dbi.addRegion(region)
				#add links in graph
				##	Cryptic writings Have to decipher later 
			#	for n in region['adjacent']:
			#		query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
			#			VALUES(%s, %s)""", curRegion, n + maxId)
			#		query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
			#			VALUES(%s, %s)""", n + maxId, curRegion)
			#	result.append(curRegion)
			#	curRegion += 1
			except KeyError:
				raise BadFieldException('badRegion')
	return {'result': 'ok', 'mapId': mapId, 'regions': result} if len(result) else {'result': 'ok', 'mapId': mapId}
	

def initRegions(mapId, gameId):
	regions = dbi.getMapById(mapId)
	result = list()
	for region in regions:
		regState = RegionState(region.id, gameId, region.defTokensNum)
		dbi.add(regState)
		result.append(regState.id)
	return result

def act_createGame(data):
	user = dbi.getUserBySid(data['sid'])
	if user.gameId: raise BadFieldException('alreadyInGame')

	map_ = dbi.getMapById(data['mapId'])
	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']

	newGame = Game(data['mapName'], descr, map_.id)
	regionIds = addNewRegions(map_.id, newGame.id)
	user.game = newGame
	user.isReady = True
	userPriority = 1
	return {'result': 'ok', 'gameId': newGame.id, 'regions': regionIds}
	
def act_getGameList(data):
	result = {'result': 'ok'}
	games = dbi.query(Game)
	result['games'] = list()

	gameAttrs = ['id', 'name', 'descr', 'state', 'turn',  'activePlayer']
	mapAttrs = ['id', 'name', 'playersNum', 'turnsNum']
	playerAttrs = ['id', 'name', 'state', 'sid']

	for game in games:
		curGame = dict()

		for i in range(len(gameAttrs)):
			if gameAttrs[i] == 'gameDescr' or not getattr(game, gameAttrs[i]):
				continue
			curGame[gameAttrs[i]] = getattr(game, gameAttrs[i]) 

		map_ = game.map
		curGame['map'] = dict()
		for i in range(len(mapAttrs)):
			curGame['map'][mapAttrs[i]] = getattr(map_, mapAttrs[i])

		players = game.players
		resPlayers = list()
		priority = 0
		for player in players:
			curPlayer = dict()
			for i in range(len(playerAttrs)):
				curPlayer[playerAttrs[i]] = getattr(player, playerAttrs)
			priority += 1	
			curPlayer['priority'] = priority
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		result['games'].append(curGame)
	return result

def act_joinGame(data):
	user = dbi.getUserBySid(data['sid'])
	if user.gameId: raise BadFieldException('alreadyInGame')
	game = dbi.getGameById(data['gameId'])
	if game.state != GAME_WAITING:
		raise BadFieldException('badGameState')
	maxPlayersNum = game.map.playersNum
	if playersNum >= maxPlayersNum:
		raise BadFieldException('tooManyPlayers')

	maxPriority = dbi.query(func.max(game.players.priority))
	user.game = game
	user.priority = maxPriority + 1

#	query('UPDATE Games SET PlayersNum=PlayersNum+1 WHERE GameId=%s', gameId)
#	I hope this would happen by itself. Have to read more about sqlalchemy ``relationship'' 
	return {'result': 'ok'}
	
def act_leaveGame(data):
	user = dbi.getUserBySid(data['sid'])
	if user.gameId: raise BadFieldException('notInGame')

	curPlayersNum = len(dbi.getGameById(data['gameId']).players)
	game = user.game
	user.game = None
	for region in player.regions:
		region.tokenBadgeId = None
		region.Encapment = 0
		region.holeInTheGround = 0
		region.dragon = False
		region.Fortress = False
		region.Hero = False
#	if curPlayersNum > 1: 
#		query('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
#	else:
#		query('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', 
#			GAME_ENDED, gameId)
##	Have to happen automatically.
	if game.players == None:
		game.state = GAME_ENDED
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
	db.clearDb()
	createDefaultRaces()
	return {'result': 'ok'}

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			raise BadFieldException('badAction')
		checkFieldsCorrectness(data);
		res = globals()[func](data)
		return res
	except SQLAlchemyError, e:
		dbi.rollback()
		return e
