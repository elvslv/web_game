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
from checkFields import checkListCorrectness, checkFieldsCorrectness, extractValues, checkRegionCorrectness
from editDb import query, fetchall, fetchone, lastId, commit, rollback
from editDb import getTokenBadgeIdByRaceAndUser, getRaceAndPowerIdByTokenBadge

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
	name = extractValues('Maps', 'MapName', data['mapName'], 'badMapName', False)[0]
	players = int(data['playersNum'])
	query('INSERT INTO Maps(MapName, PlayersNum, TurnsNum) VALUES(%s, %s, %s)', name, 
		players, data['turnsNum'])
	mapId = lastId()
	if 'regions' in data:
		regions = data['regions']
		for region in regions:
			try:
				#add land description
				query(checkRegionCorrectness(region), mapId, region['population'])
				#add links in graph
				id = lastId()
				for n in region['adjacent']:
					query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", id, n)
					query("""INSERT IGNORE INTO AdjacentRegions(FirstRegionId, SecondRegionId) 
						VALUES(%s, %s)""", n, id)
			except KeyError:
				raise BadFieldException('badRegion')
	return {'result': 'ok', 'mapId': mapId}
	
def act_createGame(data):
	userId, gameId = getIdBySid(data['sid'])
	if gameId: raise BadFieldException('alreadyInGame')

	mapId, name = extractValues('Maps', 'MapId', data['mapId'], 'badMapId', True)
	name = extractValues('Games', 'GameName', data['gameName'], 'badGameName', False)[0]

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

	gameId, (playersNum, mapId, state) = extractValues(
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

def getNextRaceAndPowerFromStack(gameId):
	racesInStack = range(0, misc.RACE_NUM)
	specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE GameId=%s', gameId)
	row = fetchall()
	for rec in row:
		racesInStack.remove(rec[0])
		specialPowersInStack.remove(rec[1])
	raceId = racesInStack[1]#random.choice(racesInStack)
	specialPowerId = specialPowersInStack[0]#random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(gameId, lastIndex):
	raceId, specialPowerId = getNextRaceAndPowerFromStack(gameId)
	query("""UPDATE TokenBadges SET Position=Position+1 WHERE Position<%s 
		AND GameId=%s""", lastIndex, gameId)
	query("""INSERT INTO TokenBadges(RaceId, SpecialPowerId, GameId, position, BonusMoney) 
		VALUES(%s, %s, %s, 0, 0)""", raceId, specialPowerId, gameId)
	
def updateRacesOnDesk(gameId, position):
	query('UPDATE TokenBadges SET Position=NULL WHERE GameId=%s AND Position=%s', gameId, position)
	query("""UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE position>%s AND 
		GameId=%s""", position, gameId)
	showNextRace(gameId, position)

def act_setReadinessStatus(data):
	sid, (userId, gameId) = extractValues('Users', 'Sid', data['sid'], 'badSid', True, 
		['Id', 'GameId'])
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
		query('UPDATE Users SET Coins=%s, TokensInHand=0, CurrentTokenBadge=NULL, \
			DeclinedTokenBadge=NULL WHERE GameId=%s', misc.INIT_COINS_NUM, gameId)
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
	sid, (tokenBadgeId, coins, userId, gameId) = extractValues('Users', 'Sid', 
		data['sid'], 'badSid', True, ['CurrentTokenBadge', 'Coins', 'Id', 'GameId'])
	query('SELECT 1 From Games WHERE ActivePlayer=%s  AND GameId=%s', userId, gameId)
	if tokenBadgeId or not fetchone():	
		raise BadFieldException('badStage')
	
	checkForDefendingPlayer(gameId)

	position, (tokenBadgeId, bonusMoney) = extractValues('TokenBadges', 
		'Position', data['position'], 'badChoice', True, ['TokenBadgeId', 'BonusMoney'])
	query('SELECT COUNT(*) From TokenBadges WHERE Position>%s', position)
	price = fetchone()[0]
	if coins < price : 
		raise BadFieldException('badMoneyAmount')

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	tokensNum = races.racesList[raceId].initialNum + races.specialPowerList[specialPowerId].tokensNum
	query('UPDATE Users SET CurrentTokenBadge=%s, Coins=Coins-%s+%s, TokensInHand=%s WHERE Sid=%s', 
		tokenBadgeId, price, bonusMoney, tokensNum, sid)
	query("""UPDATE TokenBadges SET OwnerId=%s, InDecline=False, SpecialPowerBonusNum=%s, RaceBonusNum=%s
	 	WHERE TokenBadgeId=%s""", userId, callSpecialPowerMethod(specialPowerId, 'getInitBonusNum'),
		callRaceMethod(raceId, 'getInitBonusNum'), tokenBadgeId)	
	query('UPDATE Games SET PrevState=%s', misc.gameStates['selectRace'])
	updateRacesOnDesk(gameId, position)
	return {'result': 'ok'}

def callRaceMethod(raceId, methodName, *args):
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
#	if not specialPowerId:			
#		return
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def act_conquer(data):
	sid, (userId, tokenBadgeId, gameId) = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	if not tokenBadgeId: 
		raise BadFieldException('badStage')
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)

	checkForDefendingPlayer(gameId)	

	reqRegionFields = ['OwnerId', 'TokensNum', 'TokenBadgeId']
	reqRegionFields.extend(misc.possibleLandDescription_)	
	reqRegionFields.append('inDecline')						
	regionId, regInfo = extractValues('Regions', 
		'RegionId', data['regionId'], 'badRegionId', True, reqRegionFields)
	ownerId, attackedTokensNum, attackedTokenBadgeId = regInfo[:3]
	regInfo = regInfo[3:]
	query('SELECT MapId From Regions WHERE RegionId=%s', regionId)
	mapId = fetchone()[0]
	query("""SELECT Games.MapId From Games, Users WHERE Users.Sid=%s AND 
		Users.GameId=Games.GameId""", sid)
	rightMapId = fetchone()[0]
	if mapId != rightMapId :
		raise BadFieldException('badRegionId')

	inDecline = 0
	#check the attacking race
	if 'tokenBadgeId' in data:
		tokenBadgeId, raceId, specialPowerId, inDecline = extractValues('TokenBadges', 
		'TokenBadgeId', data['tokenBadgeId'], 'badTokenBadgeId', True, ['RaceId', 'SpecialPowerId',
		'InDecline'])
		if inDecline:
			callRaceMethod(raceId, 'tryToAttackByRaceInDecline')

	if ownerId == userId and not inDecline: 
		raise BadFieldException('badRegion')
	query('SELECT RegionId FROM Regions WHERE TokenBadgeId=%s', tokenBadgeId)
	playerRegions = fetchall()
	playerBorderline = False	
	for plRegion in playerRegions:
		query("""SELECT COUNT(*) FROM AdjacentRegions WHERE FirstRegionId=%s 
			AND SecondRegionId=%s""", plRegion[0], regionId)
		if fetchone():
			playerBorderline = True
			break
	if playerBorderline: #case for flying and seafaring
		if not callSpecialPowerMethod(specialPowerId, 'tryToConquerAdjacentRegion', 
			playerRegions, regInfo[misc.possibleLandDescription['border']], regInfo[misc.possibleLandDescription['coast']], 
			regInfo[misc.possibleLandDescription['sea']]):
			raise BadFieldException('badRegion')

	if not playerBorderline: 
		f1 = callRaceMethod(raceId, 'tryToConquerNotAdjacentRegion', playerRegions, 
				regInfo[misc.possibleLandDescription['border']], regInfo[misc.possibleLandDescription['coast']],
				regionId, tokenBadgeId)
		f2 = callSpecialPowerMethod(specialPowerId, 'tryToConquerNotAdjacentRegion', 
				playerRegions, regInfo[misc.possibleLandDescription['border']], 
				regInfo[misc.possibleLandDescription['coast']], regionId, tokenBadgeId)
		if not (f1 or f2):
			raise BadFieldException('badRegion')

	if (regInfo[misc.possibleLandDescription['holeInTheGround']] or 
		regInfo[misc.possibleLandDescription['dragon']] or regInfo[misc.possibleLandDescription['hero']]):
		raise BadFieldException('badRegion')

	mountain = regInfo[misc.possibleLandDescription['mountain']]
	encampment = regInfo[misc.possibleLandDescription['encampment']]
	fortress = regInfo[misc.possibleLandDescription['fortress']]
	attackedRace = None
	attackedSpecialPower = None
	if attackedTokenBadgeId:
		attackedRace, attackedSpecialPower = getRaceAndPowerIdByTokenBadge(attackedTokenBadgeId)
	additionalTokensNum = 0
	if attackedRace:
		additionalTokensNum = callRaceMethod(attackedRace, 'countAdditionalConquerPrice')
	unitPrice = max(misc.BASIC_CONQUER_COST + attackedTokensNum + mountain + encampment + fortress +
		additionalTokensNum + 
		callRaceMethod(raceId, 'countConquerBonus', userId, regionId, regInfo, tokenBadgeId) + 
		callSpecialPowerMethod(raceId, 'countConquerBonus', userId, regionId, regInfo, tokenBadgeId), 1)
	query('SELECT TokensInHand FROM Users WHERE Id=%s', userId)
	unitsNum = fetchone()[0]
	if unitsNum < unitPrice : 
		dice = random.randint(1, 6)
		if dice > 3:
			dice = 0
		unitPrice -= dice
		if unitsNum < unitPrice:
			raise BadFieldException('badTokensNum')
	query('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE Id=%s', unitPrice, userId)
	query("""UPDATE Regions SET OwnerId=%s, TokensNum=%s, InDecline=%s, TokenBadgeId=%s 
		WHERE RegionId=%s""", userId, unitPrice, inDecline, tokenBadgeId, regionId) 
	query("""UPDATE Games SET DefendingPlayer=%s, CounqueredRegionsNum=CounqueredRegionsNum+1,
		NonEmptyCounqueredRegionsNum=NonEmptyCounqueredRegionsNum+%s, PrevState=%s, 
		ConqueredRegion=%s, AttackedTokenBadgeId=%s, AttackedTokensNum=%s""", ownerId, 
		1 if attackedTokensNum else 0, misc.gameStates['conquer'], regionId, 
		attackedTokenBadgeId, attackedTokensNum)
	callRaceMethod(raceId, 'useBonus', 'conquered', data, tokenBadgeId, regionId)
	callSpecialPowerMethod(specialPowerId, 'useBonus', 'conquered', data, tokenBadgeId, regionId)
	return {'result': 'ok'}
		
def act_decline(data):
	sid, (userId, freeUnits, tokenBadgeId, gameId) = extractValues('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'TokensInHand', 'CurrentTokenBadge', 'GameId'])
	
	checkForDefendingPlayer(gameId)
	if not tokenBadgeId:
		raise BadFieldException('badStage')

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'tryToGoInDecline', gameId)
	query("""UPDATE Regions SET OwnerId=NULL, InDecline=0, TokenBadgeId=NULL WHERE OwnerId=%s 
		AND InDecline=1""", userId)
	
	callRaceMethod(raceId, 'setRegionsInDecline', userId)	
	query("""UPDATE Users SET DeclinedTokenBadge=%s, CurrentTokenBadge=NULL, TokensInHand=0 WHERE Sid=%s""", 
		tokenBadgeId, sid)
	query('UPDATE TokenBadges SET SpecialPowerId=NULL WHERE TokenBadgeId=%s', tokenBadgeId)
	query('UPDATE Games SET PrevState=%s', misc.gameStates['decline'])

	return {'result': 'ok'}

def act_redeploy(data):
	sid, (userId, tokenBadgeId, gameId) = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	checkForDefendingPlayer(gameId)
	if not tokenBadgeId:
		raise('badStage')

	inDecline = False
	if 'tokenBadgeId' in data:
		tokenBadgeId, inDecline = extractValues('TokenBadges', 'TokenBadgeId', 
			data['tokenBadgeId'], 'badTokenBadgeId', ['InDecline'])

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	if inDecline:
		callRaceMethod(raceId, 'tryToRedeploymentInDeclineRace')

	callRaceMethod(raceId, 'countAdditionalRedeploymentUnits', userId, gameId)
	query('SELECT TotalTokensNum FROM TokenBadges WHERE TokenBadgeId=%s', tokenBadgeId)
	unitsNum = fetchone()[0]
	query('UPDATE Regions SET TokensNum=0 WHERE TokenBadgeId=%s', tokenBadgeId)
	if not unitsNum:
		raise BadFieldException('noTokensForRedeployment')

	if not query('SELECT RegionId, COUNT(*) FROM Regions WHERE TokenBadgeId=%s', tokenBadgeId):
		raise BadFieldException('userHasNotRegions') ##better comment?
	regionId, regionsNum = fetchone()

	for region in data['regions']:
		if not ('regionId' in region and 'tokensNum' in region):
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')

		regionId = region['regionId']
		tokensNum = region['tokensNum']
		if not query('SELECT 1 FROM Regions WHERE RegionId=%s and TokenBadgeId=%s', 
			regionId, tokenBadgeId):
			raise BadFieldException('badRegion')
		if tokensNum > unitsNum:
			raise BadFieldException('notEnoughTokensForredeploy')

		query('UPDATE Regions SET TokensNum=%s WHERE RegionId=%s', tokensNum, regionId)
		unitsNum -= tokensNum

	if unitsNum:
		query('UPDATE Regions SET TokensNum=TokensNum+%s WHERE RegionId=%s', tokensNum, regionId)
	
	query('SELECT RegionId FROM Regions WHERE TokenBadgeId=%s AND TokensNum=0', tokenBadgeId)
	regions = fetchall()
	for region in regions:
		callRaceMethod(raceId, 'declineRegion', region[0])
		callSpecialPowerMethod(specialPower, 'declineRegion', region[0])

	query('UPDATE Games SET PrevState=%s', misc.gameStates['redeployment'])
	return {'result': 'ok'}
		
def act_finishTurn(data):
	sid, (userId, gameId, freeUnits, priority) = extractValues('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'GameId', 'TokensInHand', 'Priority'])
	checkForDefendingPlayer(gameId)
	
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	if not income:
		raise BadFieldException('badStage')

	additionalCoins = 0
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE OwnerId=%s', userId)
	races = fetchall()
	for rec in races:
		income += callRaceMethod(rec[0], 'countAdditionalCoins', userId, gameId)
		income += callSpecialPowerMethod(rec[1], 'countAdditionalCoins', userId, gameId, rec[0])

	query('UPDATE Users SET Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s',  income, sid)

	#check for the end of game		
	query("""SELECT Maps.TurnsNum, Games.Turn FROM Maps, Games WHERE Games.GameId=%s AND 
			Maps.MapId=Games.MapId""", gameId)
	turnsNum, curTurn = fetchone()
	if turnsNum == curTurn + 1:
		return endOfGame()

	#select the next player
	query('SELECT Id, CurrentTokenBadge, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s',
		priority, gameId)
	row = fetchone()
	if not row:
		query("""SELECT Id, CurrentTokenBadge, TokensInHand FROM Users WHERE GameId=%s 
			ORDER BY Priority""", gameId)
		row = fetchone()
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)

	newActPlayer, raceId, tokensInHand = row
	query('UPDATE Games SET ActivePlayer=%s WHERE GameId=%s', newActPlayer, gameId)
	query("""SELECT TokenBadges.TotalTokensNum, COUNT(*) FROM Regions, TokenBadges 
		WHERE Regions.OwnerId=%s""", newActPlayer)
	unitsNum, regionsNum = fetchone()
	if not unitsNum: unitsNum = 0

	#	Gathering troops
	query('UPDATE Users SET TokensInHand=%s WHERE Id=%s', unitsNum - regionsNum,  
		newActPlayer)
	query('UPDATE Regions SET TokensNum=1 WHERE OwnerId=%s', newActPlayer)
#	callRaceMethod(raceId, 'useBonus', 'finishTurn', data, tokenBadgeId, regionId)
#	callSpecialPowerMethod(specialPowerId, 'useBonus', 'finishTurn', data, tokenBadgeId, regionId)
	query('UPDATE Games SET PrevState=%s', misc.gameStates['finishTurn'])
	return {'result': 'ok', 'nextPlayer' : newActPlayer}

def act_defend(data):
	sid, userId, tokenBadgeId, gameId = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	if not query("""SELECT AttackedRace, CounquredRegion, AttackedTokensNum 
		FROM Games WHERE GameId=%s AND DefendingPlayer=%s""", gameId, userId):
		raise BadFieldException('badStage') ##better comment?
	raceId, regionId, tokensNum = fetchone()[0]
	tokensNum += callRaceMethod(raceId, 'updateAttackedTokensNum', tokenBadgeId)
	if not 'regions' in data:
		raise BadFieldException('badJson')

	#find not adjacent regions
	query("""SELECT b.RegionId FROM Regions a, Regions b 
		WHERE a.RegionId=%s AND a.TokenBadgeId=b.TokenBadgeId AND NOT 
		EXISTS(SELECT 1 FROM AdjacentUsers WHERE FirstRegionId=a.RegionId AND 
		SecondRegionId=b.RegionId)""", regionId)
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

	canDefend = query('SELECT COUNT(*) FROM Regions WHERE TokenBadgeId=%s', 
		userId, tokenBadgeId)
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
