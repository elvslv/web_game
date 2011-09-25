import editDb
import re
import time
import math
import misc
import MySQLdb
import sys
import random
import races

from gameExceptions import BadFieldException
from checkFields import checkListCorrectness, checkFieldsCorrectness, checkParamPresence, checkRegionCorrectness
from editDb import query, fetchall, fetchone, lastId, commit, rollback

def getIdBySid(sid):
	if not query('SELECT Id, GameId FROM Users WHERE Sid=%s', sid):
		raise BadFieldException('badSid')
	return fetchone()

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
	if 'simpletime' in data:
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
	name = checkParamPresence('Maps', 'MapName', data['mapName'], 'badMapName', False)[0]
	players = int(data['playersNum'])
	query('INSERT INTO Maps(MapName, PlayersNum, TurnsNum) VALUES(%s, %s, %s)', name, 
		players, data['turnsNum'])
	mapId = lastId()
	if 'regions' in data:
		regions = data['regions']
		for region in regions:
			try:
				#add land description
				query(checkRegionCorrectness(data), mapId, region['population'])	
				#add links in graph
				id = lastId()
				for n in region['adjacent']:
					query("""INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", id, n)
					query("""INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", n, id)
			except KeyError:
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
		print map
		curGame['map'] = dict()
		for i in range(len(mapRowNames)):
			curGame['map'][mapRowNames[i]] = map[i]

		query('SELECT Id, Username, IsReady, Sid FROM Users WHERE GameId=%s ORDER BY Priority ASC', 
			gameId)
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

def act_joinGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')

	gameId, (playersNum, mapId, state) = checkParamPresence(
		'Games', 'GameId', data['gameId'], 'badGameId', True, ['PlayersNum', 'MapId', 
		'State'])
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

def getNextRaceFromStack(gameId):
	racesInStack = range(0, misc.RACE_NUM)
	query('SELECT RaceId FROM TokenBadges WHERE GameId=%s', gameId)
	row = fetchall()
	for race in row:
		racesInStack.remove(race[0])
	raceId = random.choice(racesInStack)
	return raceId

def showNextRace(gameId, lastIndex):
	raceId = getNextRaceFromStack(gameId)
	query("""UPDATE TokenBadges SET FarFromStack=FarFromStack+1 WHERE FarFromStack<%s AND GameId=%s""", lastIndex, gameId)
	query("""INSERT INTO TokenBadges(RaceId, GameId, FarFromStack, BonusMoney) 
		VALUES(%s, %s, 0, 0)""", raceId, gameId)
	
def updateRacesOnDesk(gameId, farFromStack):
	query('UPDATE TokenBadges SET FarFromStack=NULL WHERE GameId=%s AND FarFromStack=%s', gameId, farFromStack)
	query('UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE FarFromStack>%s AND GameId=%s', farFromStack, gameId)
	showNextRace(gameId, farFromStack)

def act_setReadinessStatus(data):
	sid, (userId, gameId) = checkParamPresence('Users', 'Sid', data['sid'], 'badSid', True, ['Id', 'GameId'])
	if not query('SELECT State FROM Games WHERE GameId=%s', gameId):
		raise BadFieldException('notInGame')
	gameState = fetchone()[0]
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
		# Starting
		query('UPDATE Users SET Coins=%s, TokensInHand=0, CurrentRace=NULL, \
			DeclineRace=NULL, Bonus=NULL WHERE GameId=%s', misc.INIT_COINS_NUM, gameId)
		query('SELECT Id FROM Users WHERE GameId=%s ORDER BY Priority', gameId)
		actPlayer = fetchone()[0]
		query("""UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s, PrevState=%s WHERE 
			GameId=%s""", misc.gameStates['processing'], actPlayer, misc.gameStates['finishTurn'], 
			gameId)

		#generate first 6 races
		for i in range(misc.VISIBLE_RACES):
			showNextRace(gameId, misc.VISIBLE_RACES - 1)
	return {'result': 'ok'}
	
def checkForDefendingPlayer(gameId):
	query('SELECT DefendingPlayer FROM Games WHERE gameId=%s', gameId)
	if fetchone()[0]:
		raise BadFieldException('badStage') ##better message?

def act_selectRace(data):
	sid, tokenBadgeId, coins, userId, gameId = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['CurrentRace', 'Coins', 'Id', 'GameId'])
	query('SELECT 1 From Games WHERE ActivePlayer=%s  AND GameId=%s', userId, gameId)
	if tokenBadgeId or not fetchone():	
		raise BadFieldException('badStage')
	
	checkForDefendingPlayer(gameId)

	farFromStack, raceId, tokenBadgeId, bonusMoney = checkParamPresence('TokenBadges', 
		'FarFromStack', data['farFromStack'], 'badChoice', True, ['RaceId', 
		'TokenBadgeId', 'BonusMoney'])

	query('SELECT COUNT(*) From TokenBadges WHERE FarFromStack>%s', farFromStack)
	price = fetchone()[0]
	if coins < price : 
		raise BadFieldException('badMoneyAmount')

	tokensNum = races.raceDescription[raceId]['initialNum']
	query('UPDATE Users SET CurrentRace=%s, Coins=Coins-%s+%s, TokensInHand=%s WHERE Sid=%s', 
		tokenBadgeId, price, bonusMoney, tokensNum, sid)
	query('UPDATE TokenBadges SET OwnerId=%s, Declined=False WHERE TokenBadgeId=%s', 
		userId, tokenBadgeId)	
	query('UPDATE Games SET PrevState=%s', misc.gameStates['selectRace'])
	updateRacesOnDesk(gameId, farFromStack)
	return {'result': 'ok'}

def callRaceMethod(race, methodName, *args):
	raceClass = 'races.Race%s' % possibleLandDescription[race]
	return raceClass().methodName(args) if args else raceClass().methodName()

def getRaceIdByTokenBadge(tokenBadge):
	query('SELECT RaceId FROM TokenBadges WHERE TokenBadgeId=%s', tokenBadge)
	return fetchone()[0]
	
def act_conquer(data):
	sid, userId, tokenBadgeId, gameId = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentRace', 'GameId'])
	race = getRaceIdByTokenBadge(tokenBadgeId)
	checkForDefendingPlayer(gameId)	
	query('SELECT Games.MapId From Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId',
		sid)
	rightMapId = fetchone()[0]
	if mapId != rightMapId :
		raise BadFieldException('badRegionId')

	#check the attacking race
	if 'raceId' in data:
		race = data['raceId']
		if not query('SELECT Declined FROM TokenBadges WHERE OwnerId=%s AND RaceId=%s', 
			userId, raceId):
			raise BadFieldException('badRaceId')
		declined = fetchone()
		if declined:
			callRaceMethod(race, 'tryToAttackByDeclinedRace')

	if not race:
		raise BadFieldException('badStage')

	reqRegionFields = ['OwnerId', 'TokenNum', 'RaceId'].extend(possibleLandDescription).append(
		'inDecline')
	regionId, ownerId, tokenNum, attackedRace, regInfo = checkParamPresence('Regions', 
		'RegionId', data['regionId'], True, 'badRegionId', reqRegionFields)

	if ownerId == userId and not inDecline: 
		raise BadFieldException('badRegion')

	query('SELECT RegionId FROM Regions WHERE OwnerId=%s', userId)
	playerRegions = fetchall()
	playerBorderline = False	
	for plRegion in playerRegions:
		query("""SELECT COUNT(*) FROM AdjacentRegions WHERE FirstRegionId=%s 
			AND SecondRegionId=%s""", plRegion[0], regionId)
		if fetchone():
			playerBorderline = True
			break
	#need case fo flying!!!
	if not playerBorderline: 
		callRaceMethodcallRaceMethod('tryToConquerNotAdjacentRegion', playerRegions, 
			regInfo[0], regInfo[1])

	unitPrice = max(BASIC_CONQUER_COST + tokenNum + mountain + 
		raceClass().countAdditionalConquerPrice(userId, regionId, regInfo, raceId), 1)
	query('SELECT TokensInHand FROM Users WHERE UserId=%s', usersId)
	unitsNum = fetchone()[0]
	if unitsNum < unitPrice : 
		dice = random.randint(1, 6)
		if dice > 3:
			dice = 0
		if unitsNum + dice < unitPrice:
			raise BadFieldException('badTokensNum')

	query('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE userId=%s', unitPrice, userId)
	query('UPDATE Regions SET OwnerId=%s, TokensNum=%s, InDecline=0, RaceId=%s WHERE RegionId=%s', 
		userId, unitPrice, regionId, race) 
	query("""UPDATE Games SET DefendingPlayer=%s, CounqueredRegionsNum=CounqueredRegionsNum+1,
		NonEmptyCounqueredRegionsNum=NonEmptyCounqueredRegionsNum+%s, PrevState=%s, 
		ConqueredRegion=%s, AttackedRace=%s""", ownerId, 1 if tokenNum else 0, 
		misc.gameStates['conquer'], regionId, attackedRace)
	return {'result': 'ok'}
		
def act_decline(data):
	sid, userId, freeUnits, race = checkParamPresence('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'TokensInHand', 'CurrentRace'])

	checkForDefendingPlayer(gameId)

	if not race:
		raise BadFieldException('badStage')

	query('UPDATE Regions SET OwnerId=NULL, InDecline=0, RaceId=NULL WHERE OwnerId=%s AND InDecline=1', 
		userId)
	callRaceMethod('setRegionsDeclined', userId)	
	query("""UPDATE Users SET DeclineRace=%s, CurrentRace=NULL, TokensInHand=0
		WHERE Sid=%s""", race, sid)
	query('UPDATE Games SET PrevState=%s', misc.gameStates['decline'])
	return {'result': 'ok'}

def act_redeployment(data):
	sid, userId, tokensBadgeId, gameId = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentRace', 'GameId'])
	race = getRaceByTokenBadge(tokenBadgeId)
	checkForDefendingPlayer(gameId)
	declined = False
	if 'raceId' in data:
		race = data['raceId']
		if not query('SELECT Declined FROM TokenBadges WHERE OwnerId=%s AND RaceId=%s', 
			userId, raceId):
			raise BadFieldException('badRaceId')
		declined = fetchone()[0]
		if declined:
			callRaceMethod(race, 'tryToRedeploymentDeclinedRace')

	if not race:
		raise BadFieldException('badStage')
	
	callRaceMethod(race, 'countAdditionalRedeploymentUnits', userId, gameId)
	query('SELECT TotalTokensNum FROM TokensBadges WHERE OwnerId=%s AND RaceId=%s', userId, race)
	unitsNum = fetchone()[0]
	if not unitsNum:
		raise BadFieldException('noTokensForRedeployment')

	if not data['regions']:
		if not query('SELECT RegionId FROM Regions WHERE OwnerId=%s AND RaceId=%s', 
			userId, race):
			raise BadFieldException('userHasNotRegions') ##better comment?
		regionId = fetchone()[0]

	for region in data['regions']:
		if not ('regionId' in region and 'tokensNum' in region):
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')

		regionId = region['regionId']
		tokensNum = region['tokensNum']
		if not query('SELECT 1 FROM Regions WHERE RegionId=%s and OwnerId=%s', 
			regiondId, tokensNum):
			raise BadFieldException('badRegion')
		if tokensNum > unitsNum:
			raise BadFieldException('notEnoughTokensForRedeployment')

		query('UPDATE Regions SET TokensNum=%s WHERE RegionId=%s', tokensNum, regionId)
		unitsNum -= tokensNum

	if unitsNum:
		query('UPDATE Regions SET TokensNum=%s WHERE RegionId=%s', tokensNum, regionId)
	
	query('UPDATE Games SET PrevState=%s', misc.gameStates['redeployment'])
	return {'result': 'ok'}
		
def act_finishTurn(data):
	sid, userId, gameId, freeUnits, priority = checkParamPresence('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'GameId', 'TokensInHand', 'Priority'])

	checkForDefendingPlayer(gameId)
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	if not income:
		raise BadFieldException('badStage')

	additionalCoins = 0
	query('SELECT RaceId FROM TokenBadges WHERE OwnerId=%s', userId)
	races = fetchall()
	for race in races:
		income += callRaceMethod(race[0], 'countAdditionalCoins', userId, gameId)
	
	query('UPDATE Users SET Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s',  income, sid)

	#check for the end of game		
	query("""SELECT Maps.TurnsNum, Games.Turn FROM Maps, Games WHERE Games.GameId=%s AND 
			Maps.MapId=Games.MapId""", gameId)
	turnsNum, curTurn = fetchone()
	if turnsNum == curTurn + 1:
		return endOfGame()

	#select the next player
	query('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s',
		priority, gameId)
	row = fetchone()
	if not row:
		query("""SELECT Id, CurrentRace, TokensInHand FROM Users WHERE GameId=%s 
			ORDER BY Priority""", gameId)
		row = fetchone()
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)

	newActPlayer, race, tokensInHand = row
	query('UPDATE Games SET ActivePlayer=%s WHERE GameId=%s', newActPlayer, gameId)
	query("""SELECT TokenBadges.TotalTokensNum, COUNT(*) FROM Regions, TokenBadges 
		WHERE Regions.OwnerId=%s""", newActPlayer)
	unitsNum, regionsNum = fetchone()
	if not unitsNum: unitsNum = 0

	#	Gathering troops
	query('UPDATE Users SET TokensInHand=%s WHERE Id=%s', unitsNum - regionsNum,  
		newActPlayer)
	query('UPDATE Regions SET TokensNum=1 WHERE OwnerId=%s', newActPlayer)

	query('UPDATE Games SET PrevState=%s', misc.gameStates['finishTurn'])
	return {'result': 'ok', 'nextPlayer' : newActPlayer}

def act_defend(data):
	sid, userId, tokensBadgeId, gameId = checkParamPresence('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentRace', 'GameId'])
	if not query("""SELECT AttackedRace, CounquredRegion, AttackedTokensNum 
		FROM Games WHERE GameId=%s AND DefendingPlayer=%s""", gameId, userId):
		raise BadFieldException('badStage') ##better comment?
	
	raceId, regionId, tokensNum = fetchone()[0]
	tokensNum += callRaceMethod(raceId, 'countAdditionalDefendingTokens', tokensBadgeId)
	if not 'regions' in data:
		raise BadFieldException('badJson')

	#find not adjacent regions
	query("""SELECT b.RegionId FROM Regions a, Regions b 
		WHERE a.RegionId=%s AND a.OwnerId=b.OwnerId	AND a.RaceId=b.RaceId AND NOT 
		EXISTS(SELECT 1 FROM AdjacentUsers WHERE FirstRegionId=a.RegionId AND SecondRegionId=b.RegionId)""", 
		regionId)
	notAdjacentRegions = fetchall()
	for region in data['regions']:
		if not 'regionId' in region:
			raise BadFieldException('badJson')
		if not 'tokensNum' in region:
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badRegionId')

		if tokensNum < region['tokensNum']:
			raise BadFieldException('notEnoughTokens')
		if not query('SELECT 1 FROM Regions WHERE RegionId=%s AND OwnerId=%s', 
			region['regionId'], userId):
			raise BadFieldException('badRegion')
		if query("""SELECT 1 FROM AdjacentRegions WHERE FirstRegionId=%s AND 
			SecondRegionId=%s""", regionId, region['regionId']) and notAdjacentRegions:
			raise BadFieldException('badRegion')
		
		query('UPDATE Regions SET TokensNum=TokensNum+%s WHERE RegionId=%s', 
			region['tokensNum'], region['regionId'])
		tokensNum -= region['tokensNum']

	canDefend = query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s', 
		userId, raceId)
	if tokensNum and canDefend:
		raise BadFieldException('thereAreTokensInHand')

def act_doSmth(data):
	userId = getIdBySid(data['sid'])[0]
	return {'result': 'ok'}

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
