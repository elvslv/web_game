import editDb
import re
import time
import misc
import MySQLdb

from misc import MAX_USERNAME_LEN, MAX_PASSWORD_LEN, MIN_USERNAME_LEN, MIN_PASSWORD_LEN
from misc import MAX_PLAYERS_NUM, MIN_PLAYERS_NUM
from misc import MIN_GAMENAME_LEN, MAX_GAMENAME_LEN
from misc import MAX_GAMEDESCR_LEN, MAX_MAPNAME_LEN
from misc import BASIC_CONQUER_COST, INIT_COINS_NUM, MAX_VISIBLE_RACES

from editDb import query, fetchall, fetchone, lastId, commit, rollback

usrnameRegexp = r'^[a-z]+[\w_-]{%s,%s}$' % (MIN_USERNAME_LEN - 1, MAX_USERNAME_LEN - 1)
pwdRegexp = r'^.{%s,%s}$' % (MIN_PASSWORD_LEN, MAX_PASSWORD_LEN)

def checkFieldsCorrectness(data):
	fields = misc.actionFields[data['action']]
	if not fields:
		return {'result': 'actionDoesntExist'}
	for field in fields:
		if not field['name'] in data:
			if field['mandatory']:
				return {'result': 'badJson'}
			continue
		if not isinstance(data[field['name']], field['type']):
			return {'result': 'bad' + field['name'][0].upper() + field['name'][1:]}
		
	return {'result': 'ok'}
	
def createDefaultRaces(): 
	for race in misc.defaultRaces:
		query('INSERT INTO Races(RaceName, InitialNum) VALUES(%s, %s)', race['raceName'], race['initialNum'])
		
def act_register(data):
	username = data['username']
	passwd = data['password']
	if  not re.match(usrnameRegexp, username, re.I):
		return {"result": "badUsername"}
	if  not re.match(pwdRegexp, passwd, re.I):
		return {"result": "badPassword"}

	if query("SELECT 1 FROM Users WHERE Username=%s", username):
		return {"result": "usernameTaken"}
	query("INSERT INTO Users(Username, Password) VALUES (%s, %s)", username, passwd)
	return {"result": "ok"}

def act_login(data):
	username = data['username']
	passwd = data['password']
	if not query("SELECT 1 FROM Users WHERE Username=%s AND Password=%s", username, passwd):
		return {'result': 'badUsernameOrPassword'}

	while 1:
		sid = misc.generateSidForTest()
		if not query("SELECT 1 FROM Users WHERE Sid=%s", sid):
				break
			
	query("UPDATE Users SET Sid=%s WHERE Username=%s", sid, username)
	return {"result": "ok", "sid": long(sid)}

def act_logout(data):
	sid = data['sid']
	if not query("UPDATE Users SET Sid=NULL WHERE Sid=%s", sid):
		return {"result": "badSid"}
	return {"result": "ok"}

def act_doSmth(data):
	sid = data['sid']
	if not query("SELECT id FROM Users WHERE Sid=%s", sid):
		return {"result": "badSid"}
	return {"result": "ok"}

def act_sendMessage(data):
	userId = data['userId']
	message = data['message']
	mesTime = time.time();

	if not query("SELECT 1 FROM Users WHERE Id=%s", userId):
		return {"result": "badUserId"}
	
	query("INSERT INTO Chat(UserId, Message, Time) VALUES (%s, %s, %s)", userId, message, mesTime) 
	if 'noTime' in data:
                return {"result": "ok"}
	return {"result": "ok", "mesTime": mesTime}

def act_getMessages(data):
	since = data['since']
	query("SELECT UserId, Message, Time FROM Chat WHERE Time > %s ORDER BY Time", since)
	records =  fetchall()
	records = records[-100:]
	mesArray = []
	for rec in records:
		userId, message, mesTime = rec
		if 'noTime' in data:
                        mesArray.append({"userId": userId, "message": message})
                else:
                        mesArray.append({"userId": userId, "message": message, "mesTime": mesTime})
                
	return {"result": "ok", "mesArray": mesArray}

def act_createDefaultMaps(data):
	for map in misc.defaultMaps:
		act_uploadMap(map)
	return {'result': 'ok'}
	
def act_uploadMap(data):
	name = data['mapName']
	if len(name) > MAX_MAPNAME_LEN:
		return {'result': 'badMapName'}
	if query('SELECT 1 FROM Maps WHERE MapName=%s', name):
		return {'result': 'badMapName'}
	
	players = int(data['playersNum'])
	if not ((players >= MIN_PLAYERS_NUM) and (players <= MAX_PLAYERS_NUM)):
		return {'result': 'badPlayersNum'}
	query('INSERT INTO Maps(MapName, PlayersNum) VALUES(%s, %s)', name, players)
	mapId = lastId()
	if 'regions' in data:
		regions = data['regions']
		for region in regions:
			try:
				query('INSERT INTO Regions(MapId, TokensNum, Borderline,\
					Highland, Coastal, Seaside) VALUES(%s, %s, %s, %s, %s, %s)', 
					mapId, region['population'], region['borderline'], region['highland'],
						region['coastal'], region['seaside'])	
				id = lastId()
				adjacent = region['adjacent']
				for n in adjacent:
					query('INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) VALUES(%s, %s)', 
						id, n)
					query('INSERT INTO AdjacentRegions(FirstRegionId, SecondRegionId) VALUES(%s, %s)', 
						n, id)
			except KeyError:
				return {'result': 'badRegion'}
	return {'result': 'ok', 'mapId': mapId}
	
def act_createGame(data):
	#validate sid
	sid = data['sid']
	if not query("SELECT GameId, Id FROM Users WHERE Sid=%s", sid):
		return {'result': 'badSid'}
	row = fetchone()
	if row[0]:
		return {'result': 'alreadyInGame'}
	userId = row[1]
		
	#validate mapId
	mapId = data['mapId']
	if not query("SELECT PlayersNum FROM Maps WHERE MapId=%s", mapId):
		return {'result': 'badMapId'}
		
	mapPlayersNum = int(fetchone()[0])
	if 'playersNum' in data:
		playersNum = data['playersNum']
		if playersNum != mapPlayersNum:
			return {'result': 'badPlayersNum'}
		
	#validate name and description
	name = data['gameName']
	if len(name) < MIN_GAMENAME_LEN or len(name) > MAX_GAMENAME_LEN:
		return {'result': 'badGameName'}
	if query("SELECT 1 FROM Games WHERE GameName=%s", name):
		return {'result': 'badGameName'}

	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']
	if descr and len(descr) > MAX_GAMEDESCR_LEN:
		return {'result': 'badGameDescription'}
	query("INSERT INTO Games(GameName, GameDescr, MapId, PlayersNum, State) VALUES(%s, %s, %s, %s, %s)", 
		name, descr, mapId, 1, misc.gameStates['waiting'])
	gameId = lastId()
	query("UPDATE Users SET GameId=%s, Readiness=0, Priority=1 WHERE Id=%s", gameId, userId)
	return {'result': 'ok', 'gameId': gameId}
	
def act_getGameList(data):
	result = {'result': 'ok'}
	query('SELECT * FROM Games')
	games = fetchall()
	result['games'] = list()

	gameRowNames = ['gameId', 'gameName', 'gameDescr', 'playersNum', 'state', 'turn', 'activePlayer']
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

		query('SELECT Id, Username, Readiness, Sid, Priority FROM Users WHERE GameId=%s', gameId)
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
	sid = data['sid']
	if not query('SELECT GameId, Id FROM Users WHERE sid=%s', sid):
		return {'result': 'badSid'}
	row = fetchone()
	userId = row[1]
	if row[0]:
		return {'result': 'alreadyInGame'}
	
	gameId = data['gameId']
	if not query('SELECT PlayersNum, MapId, State FROM Games WHERE GameId=%s', gameId):
		return {'result': 'badGameId'}
	row = fetchone()
	if row[2] != misc.gameStates['waiting']:
		return{'result': 'badGameState'}
	query('SELECT PlayersNum From Maps WHERE MapId=%s', row[1])
	maxPlayersNum = fetchone()[0]
	if row[0] >= maxPlayersNum:
		return {'result': 'tooManyPlayers'}

	query('SELECT MAX(Priority) FROM Users WHERE GameId=%s', gameId)
	priority = fetchone()[0] + 1
	query('UPDATE Users SET GameId=%s, Readiness=0, Priority=%s WHERE Id=%s', gameId, priority, userId)
	query('UPDATE Games SET PlayersNum=PlayersNum+1 WHERE GameId=%s', gameId)
	return {'result': 'ok'}
	
def act_leaveGame(data):
	sid = data['sid']
	if not query('SELECT GameId, Id FROM Users WHERE Sid=%s', sid):
		return {'result': 'badSid'}

	gameId, userId = fetchone()
	if not gameId:
		return {'result': 'notInGame'}
	query('SELECT PlayersNum FROM Games WHERE GameId=%s', gameId)
	curPlayersNum = fetchone()[0]
	query('UPDATE Users SET GameId=NULL, Readiness=NULL, Priority=NULL WHERE Id=%s', userId)
	query('UPDATE Regions SET OwnerId=NULL WHERE OwnerId=%s', userId)
	if curPlayersNum > 1: 
		query('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
	else:
		query('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', misc.gameStates['ended'], gameId)
	return {'result': 'ok'}

def act_setReadinessStatus(data):
	sid = data['sid']
	if not query('SELECT 1 FROM Users WHERE Sid=%s', sid):
		return {'result': 'badSid'}

	query("SELECT Users.GameId, Games.State FROM Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId", sid)

	row = fetchone()
	if not (row and row[0]):
		return {'result': 'notInGame'}

	gameId, gameState = row
	if gameState != misc.gameStates['waiting']:
		return {'result': 'badGameState'}

	status = data['readinessStatus']
	if not(status == 0 or status == 1):
		return {'result': 'badReadinessStatus'}
	query('UPDATE Users SET Readiness=%s WHERE sid=%s', status, sid)
	query('SELECT Maps.PlayersNum FROM Games, Maps WHERE Games.GameId=%s AND Games.MapId=Maps.MapId', gameId)
	maxPlayersNum = fetchone()[0]
	query('SELECT COUNT(*) FROM Users WHERE GameId=%s AND Readiness=1', gameId)
	readyPlayersNum = fetchone()[0]
	if maxPlayersNum == readyPlayersNum:
		# Starting
		query('UPDATE Users SET Coins=%s, TokensInHand=0, CurrentRace=NULL, \
			DeclineRace=NULL, Bonus=NULL WHERE GameId=%s', INIT_COINS_NUM, gameId)
		query('SELECT Id FROM Users WHERE GameId=%s ORDER BY Priority', gameId)
		actPlayer = fetchone()[0]
		query('UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s WHERE GameId=%s', 
			misc.gameStates['processing'], actPlayer, gameId)

		query('SELECT RaceId FROM Races ORDER BY(RaceId)')		#Don't know how to rephrase it
		races = fetchall()
		currRacesNum = 1
		for race in races:
			currRacesNum += 1
			query('INSERT INTO TokenBadges(RaceId, FarFromStack, BonusMoney) VALUES(%s, %s, 0)', 
				race[0], (-1 if currRacesNum > MAX_VISIBLE_RACES else currRacesNum))
	return {'result': 'ok'}
	
def act_selectRace(data):
	sid = data['sid']
	raceId = data['raceId']
	query('SELECT CurrentRace, Coins, Id FROM Users WHERE Sid=%s', sid)
	row = fetchone()
	if not row: 
		return {'result': 'badSid'}
	curRace, coins, userId = row
	query('SELECT Users.GameId, Games.ActivePlayer From Users, Games\
		 WHERE Users.Sid=%s AND Users.Id=Games.ActivePlayer', sid)
	if curRace or not fetchone():	
		return {'result': 'badStage'}
	query('SELECT FarFromStack, BonusMoney FROM TokenBadges WHERE RaceId=%s', raceId)
	farFromStack, bonusMoney = fetchone()
	if farFromStack == -1 : 				# Token badge is currently located inside of stack
		return {'result': 'badChoice'}
	query('SELECT InitialNum, BonusId FROM Races WHERE RaceId=%s', raceId)
	num,  bonusId = fetchone()
	query('SELECT COUNT(*) From TokenBadges WHERE FarFromStack>%s', farFromStack)
	price = fetchone()[0]
	if coins < price : 
		return {'result' : 'badMoneyAmount'}
	query('UPDATE Users SET CurrentRace=%s, Coins=Coins-%s+%s, Bonus=%s, TokensInHand=%s WHERE Sid=%s', 
		raceId, price, bonusMoney, bonusId, num, sid)
	query('UPDATE TokenBadges SET FarFromStack=-1, BonusMoney=0 WHERE RaceId=%s', raceId)
	query('UPDATE TokenBadges SET FarFromStack=FarFromStack+1 WHERE FarFromStack >-1 AND FarFromStack<%s', farFromStack)
	query('UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE FarFromStack>%s', farFromStack)
	query('SELECT RaceId FROM TokenBadges WHERE FarFromStack=-1')
	newRaceId = fetchone()[0];
	query('UPDATE TokenBadges SET FarFromStack=0 WHERE RaceId=%s', newRaceId)
	return {'result': 'ok'}
	
def act_conquer(data):
	regionId = data['regionId']
	sid = data['sid']
	query('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE Sid=%s', sid)
	row = fetchone()
	if not row: 
		return {'result': 'badSid'}
	userId, race, unitsNum = row
	if not race:
		return {'result' : 'badStage'}
	query('SELECT MapId, OwnerId, RaceId, TokensNum, Borderline, Highland, \
		Coastal, Seaside, inDecline FROM Regions WHERE RegionId=%s', regionId)
	regInfo = fetchone()
	if not regInfo:
		return {'result': 'badRegion'}
	mapId = regInfo[0]
	query('SELECT Users.GameId, Games.MapId From Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId', sid)
	rightMapId = fetchone()[1]
	if mapId != rightMapId :  		#The region player wanted to attack is located on another map
		return {'result': 'badRegionId'}
	ownerId = regInfo[1]
	inDecline = regInfo[8]
	if ownerId == userId and not inDecline: 
		return {'result': 'badRegion'}
	seaside = False
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	if not fetchone()[0]:			#Player doesn't own any territories yet
		borderline, coastal, seaside = regInfo[4], regInfo[6], regInfo[7]
		if not (borderline or coastal) or  seaside: 
			return  {'result': 'badRegion'}
	else:
		query('SELECT RegionId FROM Regions WHERE OwnerId=%s', userId)
		playerRegions = fetchall()
		playerBorderline = False
		for plRegion in playerRegions:
			query('SELECT COUNT(*) FROM AdjacentRegions WHERE FirstRegionId=%s AND SecondRegionId=%s', plRegion[0], regionId)
			if fetchone():
				playerBorderline = True
				break
		
		if playerBorderline == False or  seaside: 
			return {'result': 'badRegion'}
	
	unitPrice = BASIC_CONQUER_COST + regInfo[3] + regInfo[5]
	#	Tossing the dice?
	if unitsNum < unitPrice : 
		return  {'result': 'badTokensNum'}
	query('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE sid=%s', unitPrice, sid)
	query('UPDATE Regions SET OwnerId=%s, TokensNum=%s, InDecline=0 WHERE RegionId=%s', userId, unitPrice, regionId) 
	#	Defending?
	return {'result': 'ok'}
		
def act_decline(data):
	sid = data['sid']
	query('SELECT Id, TokensInHand, CurrentRace FROM Users WHERE Sid=%s', sid)
	row = fetchone()
	if not row: 
		return {'result': 'badSid'}
	userId, freeUnits, race = row
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	if not race or not fetchone()[0]:	#Player doesn't own any territories or has no race to go in decline
		return {'result': 'badStage'}
	query('UPDATE Regions SET OwnerId=NULL, InDecline=0 WHERE OwnerId=%s AND InDecline=1', userId)
	query('UPDATE Regions SET InDecline=1, TokensNum=1 WHERE OwnerId=%s', id) ###
	query('UPDATE Users SET DeclineRace=%s, CurrentRace=NULL, TokensInHand=0 WHERE Sid=%s', race, sid)
	return {'result': 'ok'}
		
def act_finishTurn(data):
	sid = data['sid']
	query('SELECT Id, GameId, CurrentRace, TokensInHand, Priority FROM Users WHERE Sid=%s', sid)
	row = fetchone()
	if not row: 
		return {'result': 'badSid'}
	userId, gameId, race, freeUnits, priority = row
	query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	if not race or not income:
		return {'result': 'badStage'}
	query('UPDATE Users SET Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s',  income, sid)
	query('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s', priority, gameId)
	row = fetchone()
	if not row:
		query('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE GameId=%s ORDER BY Priority', gameId)
		row = fetchone()
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)
	#	Last Turn?
	newActPlayer, race, tokensInHand = row
	query('UPDATE Games SET ActivePlayer=%s WHERE GameId=%s', newActPlayer, gameId)
	query('SELECT SUM(TokensNum), COUNT(*) FROM Regions WHERE OwnerId=%s', newActPlayer)
	unitsNum, regionsNum = fetchone()
	if not unitsNum: unitsNum = 0
	#	Gathering troops
	query('UPDATE Users SET TokensInHand=%s WHERE Id=%s', unitsNum - regionsNum,  newActPlayer)
	query('UPDATE Regions SET TokensNum=1 WHERE OwnerId=%s', newActPlayer)
	return {'result': 'ok', 'nextPlayer' : newActPlayer}

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			return {'result': 'badAction'}
		correctness = checkFieldsCorrectness(data);
		if correctness['result'] != 'ok':
			return correctness
		res = globals()[func](data)
		commit()
		return res
	except MySQLdb.Error, e:
		rollback()
		return e
