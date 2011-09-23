import editDb
import re
import time
import misc
import MySQLdb
import sys
from gameExceptions import BadFieldException

VISIBLE_RACES_NUM = 6
from editDb import query, fetchall, fetchone, lastId, commit, rollback

def checkFieldsCorrectness(data):
	fields = misc.actionFields[data['action']]
	if not fields:
		raise BadFieldException('actionDoesntExist')
	for field in fields:
		if not field['name'] in data:
			if field['mandatory']:
				raise BadFieldException('badJson')
			continue

	for field in fields:
		if not field['name'] in data:
			continue
		msg = 'bad' + field['name'][0].upper() + field['name'][1:]
		if not isinstance(data[field['name']], field['type']):
			raise BadFieldException(msg)

		minValue = field['min'] if 'min' in field else 0
		maxValue = field['max'] if 'max' in field else sys.maxint
		value = data[field['name']] if field['type'] is int else len(data[field['name']])
		if not minValue <= value <= maxValue:
			raise BadFieldException(msg)

def checkParamPresence(tableName, tableField, param, msg, pres, selectFields = ['1']):
	queryStr = 'SELECT '
	for field in selectFields:
		queryStr += field + (', ' if field != selectFields[len(selectFields) - 1] else ' ')
	queryStr += 'FROM %s WHERE %s=%%s' % (tableName, tableField)
	if query(queryStr, param) != pres:
		raise BadFieldException(msg)
	return [param, fetchone()]

def getIdBySid(sid):
	if not query('SELECT Id, GameId FROM Users WHERE Sid=%s', sid):
		raise BadFieldException('badSid')
	return fetchone()

def createDefaultRaces(): 
	racesOnDesk = 0 #rename
	nextRacePosition = 0
	for race in misc.defaultRaces:
		if racesOnDesk < VISIBLE_RACES_NUM:
			racesOnDesk += 1
			nextRacePosition += 1
		else:
			nextRacePosition = -1
		query("""INSERT INTO Races(RaceName, InitialNum, FarFromStack, BonusMoney)
			VALUES(%s, %s, %s, 0)""", race['raceName'], race['initialNum'], 
			nextRacePosition)
		
def act_register(data):
	username = data['username']
	passwd = data['password']
	if  not re.match(misc.usrnameRegexp, username, re.I):
		raise BadFieldException('badUsername')
	if  not re.match(misc.pwdRegexp, passwd, re.I):
		print data
		raise BadFieldException('badPassword')

	if query('SELECT 1 FROM Users WHERE Username=%s', username):
		raise BadFieldException('usernameTaken')
	query('INSERT INTO Users(Username, Password, Stage) VALUES (%s, %s, %s)',
		username, passwd, misc.userStages['notPlaying'])
	return {'result': 'ok'}

def act_login(data):
	username = data['username']
	passwd = data['password']
	if not query('SELECT 1 FROM Users WHERE Username=%s AND Password=%s', username, passwd):
		raise BadFieldException('badUsernameOrPassword')

	while 1:
		sid = misc.generateSidForTest()
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

	message = data['text']
	mesTime = time.time()
	
	query('INSERT INTO Chat(UserId, Message, Time) VALUES (%s, %s, %s)', 
		userId, message, mesTime) 
	if 'noTime' in data:
		return {'result': 'ok'}
	return {'result': 'ok', 'time': mesTime}

def act_getMessages(data):
	since = data['since']
	query('SELECT UserId, Message, Time FROM Chat WHERE Time > %s ORDER BY Time', since)
	records =  fetchall()
	records = records[-100:]
	messages = []
	for rec in records:
		userId, message, mesTime = rec
		if 'noTime' in data:
			messages.append({'userId': userId, 'text': message})
		else:
			messages.append({'userId': userId, 'text': message, 'time': mesTime})
                
	return {'result': 'ok', 'messages': messages}

def act_createDefaultMaps(data):
	for map in misc.defaultMaps:
		act_uploadMap(map)
	return {'result': 'ok'}
	
def act_uploadMap(data):
	name = checkParamPresence('Maps', 'MapName', data['mapName'], 'badMapName', False)[0]
	players = int(data['playersNum'])
	query('INSERT INTO Maps(MapName, PlayersNum) VALUES(%s, %s)', name, players)
	mapId = lastId()
	if 'regions' in data:
		regions = data['regions']
		for region in regions:
			try:
				query("""INSERT INTO Regions(MapId, TokenNum, Borderline,
					Highland, Coastal, Seaside) VALUES(%s, %s, %s, %s, %s, %s)""", 
					mapId, region['population'], region['borderline'], region['highland'],
						region['coastal'], region['seaside'])	
				id = lastId()
				adjacent = region['adjacent']
				for n in adjacent:
					query("""INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", id, n)
					query("""INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", n, id)
			except KeyError, e:
				raise BadFieldException('badRegion')
	return {'result': 'ok', 'mapId': mapId}
	
def act_createGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')

	mapId, name = checkParamPresence('Maps', 'MapId', data['mapId'], 'badMapId', True)
	name = checkParamPresence('Games', 'GameName', data['gameName'], 'badGameName', False)[0]

	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']

	query("""INSERT INTO Games(GameName, GameDescr, MapId, PlayersNum, State) 
		VALUES(%s, %s, %s, %s, %s)""", name, descr, mapId, 1, misc.gameStates['waiting'])
	gameId = lastId()
	query('UPDATE Users SET GameId=%s, isReady=0, Priority=1 WHERE Id=%s', gameId, userId)
	return {'result': 'ok', 'gameId': gameId}
	
def act_getGameList(data):
	result = {'result': 'ok'}
	query('SELECT * FROM Games')
	games = fetchall()
	result['games'] = list()

	gameRowNames = ['gameId', 'gameName', 'gameDescr', 'playersNum', 'state', 'turn', 
		'activePlayer']
	mapRowNames = ['mapId', 'mapName', 'playersNum']
	playerRowNames = ['userId', 'username', 'state', 'sid', 'priority']

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

		query('SELECT Id, Username, IsReady, Sid, Priority FROM Users WHERE GameId=%s', 
			gameId)
		players = fetchall()
		resPlayers = list()
		for player in players:
			curPlayer = dict()
			for i in range(len(playerRowNames)):
				curPlayer[playerRowNames[i]] = player[i]
			resPlayers.append(curPlayer)
		curGame['players'] = resPlayers
		result['games'].append(curGame)
	return result

def act_joinGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')

	gameId, (playersNum, mapId, state) = checkParamPresence(
		'Games', 'GameId', data['gameId'], 'badGameId', True, ['PlayersNum', 'MapId', 'State'])
	if state != misc.gameStates['waiting']:
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
	return {'result': 'ok'}
	
def act_leaveGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if not gameId: raise BadFieldException('notInGame')

	query('SELECT PlayersNum FROM Games WHERE GameId=%s', gameId)
	curPlayersNum = fetchone()[0]
	query('UPDATE Users SET GameId=NULL, IsReady=NULL, Priority=NULL WHERE Id=%s', userId)
	query('UPDATE Regions SET OwnerId=NULL WHERE OwnerId=%s', userId)
	if curPlayersNum > 1: 
		query('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
	else:
		query('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', 
			misc.gameStates['ended'], gameId)
	return {'result': 'ok'}

def act_setReadinessStatus(data):
	sid = checkParamPresence('Users', 'Sid', data['sid'], 'badSid', True)[0]
	query('SELECT Users.GameId, Games.State FROM Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId', sid)
	row = fetchone()
	if not (row and row[0]):
		raise BadFieldException('notInGame')

	gameId, gameState = row
	if gameState != misc.gameStates['waiting']:
		raise BadFieldException('badGameState')

	status = data['isReady']
	query('UPDATE Users SET IsReady=%s WHERE sid=%s', status, sid)
	query("""SELECT Maps.PlayersNum, Games.MapId FROM Games, Maps WHERE Games.GameId=%s AND 
		Games.MapId=Maps.MapId""", gameId)
	maxPlayersNum = fetchone()[0]
	query('SELECT COUNT(*) FROM Users WHERE GameId=%s AND IsReady=1', gameId)
	readyPlayersNum = fetchone()[0]
	if maxPlayersNum == readyPlayersNum:
		query("""UPDATE Users SET Coins=5, Stage=%s, TokensInHand=0, CurrentRace=NULL, 
			DeclineRace=NULL, Bonus=NULL WHERE GameId=%s""",
			misc.userStages['waitingTurn'], gameId)
		query("""SELECT Id FROM Users WHERE Priority=(SELECT MIN(Priority) FROM 
			Users WHERE gameId=%s) AND GameId=%s""", gameId, gameId)
		actPlayer = fetchone()[0]
		query('UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s WHERE GameId=%s', 
			misc.gameStates['processing'], actPlayer, gameId)
		query('UPDATE Users SET Stage=%s WHERE Id=%s', misc.userStages['choosingRace'], 
			actPlayer) 
	return {'result': 'ok'}
	
def act_selectRace(data):
	sid, stage, coins, userId = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['Stage', 'Coins', 'Id'])
	if stage != misc.userStages['choosingRace']:	
		raise BadFieldException('badStage')
	
	raceId, num, farFromStack, bonusId, bonusMoney = checkParamPresence('Races', 'RaceId', 
		data['raceId'], 'badRaceId', True, ['InitialNum', 'FarFromStack', 'BonusId', 'BonusMoney'])
	if farFromStack == -1 : 
		raise BadFieldException('badChoice')
	query('SELECT COUNT(*) From Races WHERE FarFromStack>%s', farFromStack)
	price = fetchone()[0]
	if coins < price : 
		raise BadFieldException('badMoneyAmount')
	query("""UPDATE Users SET CurrentRace=%s, Coins=Coins-%s+%s, Bonus=%s, Stage=%s, 
		TokensInHand=%s WHERE Sid=%s""", raceId, price, bonusMoney, bonusId, 
		misc.userStages['invading'], num, sid)
	query('UPDATE Races SET FarFromStack=-1, BonusMoney=0 WHERE RaceId=%s', raceId)
	query("""UPDATE Races SET FarFromStack=FarFromStack+1 WHERE FarFromStack >-1 
		AND FarFromStack<%s""", farFromStack)
	query('UPDATE Races SET BonusMoney=BonusMoney+1 WHERE FarFromStack > %s', farFromStack)
	query('SELECT RaceId FROM Races WHERE FarFromStack=-1')
	newRaceId = fetchone()[0];
	query('UPDATE Races SET FarFromStack=0 WHERE RaceId=%s', newRaceId)
	return {'result': 'ok'}
	
def act_conquer(data):
	sid, userId, stage, unitsNum = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'Stage', 'TokensInHand'])
	if not (stage == misc.userStages['invading'] or stage == misc.userStages['attacking']):
		raise BadFieldException('badStage')
	
	regionId, mapId, ownerId, raceId, tokenNum, borderline, highland, coastal, 
	seaside, inDecline = checkParamPresence('Regions', 'RegionId', data['regionId'], True, 'badRegionId', ['MapId', 'OwnerId', 'RaceId', 'TokenNum', 'Borderline', 'Highland',
		'Coastal', 'Seaside', 'inDecline'])
	query("""SELECT Games.MapId From Games WHERE Users.Sid=%s AND Users.GameId=
		Games.GameId""", sid)
	rightMapId = fetchone()[0]
	if mapId != rightMapId :
		raise BadFieldException('badRegionId')
	if ownerId == userId and not inDecline: 
		raise BadFieldException('badRegion')
	if stage == misc.userStages['invading']:
		if not (borderline or coastal): 
			raise BadFieldException('badRegion')
	else:
		query('SELECT RegionId FROM Regions WHERE OwnerId=%s', userId)
		playerRegions = fetchall()
		playerBorderline = False
		for plRegion in playerRegions:
			query("""SELECT Adjacent FROM AdjacentRegions WHERE FirstRegionId=%s 
				AND SecondRegionId=%s""", plRegion[0], regionId)
			if fetchone():
				playerBorderline = True
				break
		
		if playerBorderline == False or  seaside: 
			raise BadFieldException('badRegion')
	
	unitPrice = 2 + tokenNum + highland
	#tossing the dice?
	if unitsNum < unitPrice : 
		raise BadFieldException('badTokensNum')
	query('UPDATE Users SET TokensInHand=TokensInHand-%s, stage=%s WHERE sid=%s', 
		unitPrice, misc.userStages['attacking'], sid)
	query('UPDATE Regions SET OwnerId=%s, TokenNum=%s, InDecline=0 WHERE RegionId=%s', 
		userId, unitPrice, regionId) 
	return {'result': 'ok'}
		
def act_decline(data):
	sid, userId, stage, tokensInHand, currentRace = checkParamPresence('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'Stage', 'TokensInHand', 'CurrentRace'])
	if stage != misc.userStages['attacking']:
		raise BadFieldException('badStage')
	query('UPDATE Regions SET OwnerId=NULL, InDecline=0 WHERE OwnerId=%s AND InDecline=1', userId)##
	query('UPDATE Regions SET InDecline=1, TokensNum=1 WHERE OwnerId=%s', userId)
	query("""UPDATE Users SET DeclineRace=%s, CurrentRace=NULL, TokensInHand=0, Stage=%s 
		WHERE Sid=%s""", race, misc.userStages['choosingRace'], sid)
	return {'result': 'ok'}
		
def act_finishTurn(data):
	sid, userId, gameId, tokensInHand, priority = checkParamPresence('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'GameId', 'TokensInHand', 'Priority'])
	if not (stage == misc.userStages['invading'] or 
			stage == misc.userStages['attacking'] or stage == misc.userStages['declined']):
		raise BadFieldException('badStage')
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	query('UPDATE Users SET Stage=%s, Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s', 
		(misc.userStages['waitingTurn'], income, sid))
	query('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s',
			priority, gameId)
	row = fetchone()
	if not row:
		query('SELECT Id, CurrentRace  FROM Users WHERE GameId=%s ORDER BY Priority ASC', 
			gameId)
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)
		# Last Turn?
		row = fetchone()
	newActPlayer, race, tokensInHand = row
	newPlayerStage = misc.userStages['choosingRace'] if not race else (misc.userStages['invading'] if 
		tokensInHand == 0 else misc.userStages['attacking'])
	query('UPDATE Games SET ActivePlayer=%s WHERE gameId=%s', newActPlayer, gameId)
	query('UPDATE Users SET Stage=%s WHERE Id=%s', newPlayerStage, newActPlayer)
	return {'result': 'ok', 'nextPlayer' : newActPlayer}

def act_doSmth(data):
	userId = getIdBySid(data['sid'])[0]
	return {"result": "ok"}

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
