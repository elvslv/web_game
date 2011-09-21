import MySQLdb
import editDb
import re
import time
import misc

from misc import MAX_USERNAME_LEN
from misc import MAX_PASSWORD_LEN
from misc import MIN_USERNAME_LEN
from misc import MIN_PASSWORD_LEN
from misc import DEFAULT_PLAYERS_NUM
from misc import MIN_PLAYERS_NUM
from misc import MAX_PLAYERS_NUM
from misc import MIN_GAMENAME_LEN
from misc import MAX_GAMENAME_LEN
from misc import MAX_GAMEDESCR_LEN

cursor = editDb.cursor
db = editDb.db

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
			return {'result': 'ok'}
		if not isinstance(data[field['name']], field['type']):
			return {'result': 'bad' + field['name'].title()}
		
	return {'result': 'ok'}
			
def act_register(data):
	username = data['username']
	passwd = data['password']
	if  not re.match(usrnameRegexp, username, re.I):
		return {"result": "badUsername"}
	if  not re.match(pwdRegexp, passwd, re.I):
		return {"result": "badPassword"}

	if int(cursor.execute("SELECT 1 FROM Users WHERE Username=%s", username)):
		return {"result": "usernameTaken"}
	cursor.execute("INSERT INTO Users(Username, Password, Stage) VALUES (%s, %s, %s)",(username, passwd, 
			misc.userStages['notPlaying']))
	return {"result": "ok"}

def act_login(data):
	username = data['username']
	passwd = data['password']
	if not int(cursor.execute("SELECT 1 FROM Users WHERE Username=%s AND Password=%s",
			(username, passwd))):
		return {'result': 'badUsernameOrPassword'}

	while 1:
		sid = misc.generateSidForTest()
		if not int(cursor.execute("SELECT 1 FROM Users WHERE Sid=%s", sid)):
				break
			
	cursor.execute("UPDATE Users SET Sid=%s WHERE Username=%s", (sid, username))
	return {"result": "ok", "sid": long(sid)}

def act_logout(data):
	sid = data['sid']
	if not int(cursor.execute("UPDATE Users SET Sid=NULL WHERE Sid=%s", sid)):
		return {"result": "badSid"}
	return {"result": "ok"}

def act_doSmth(data):
	sid = data['sid']
	if not int(cursor.execute("SELECT id FROM Users WHERE Sid=%s", sid)):
		return {"result": "badSid"}
	return {"result": "ok"}

def act_sendMessage(data):
	userId = data['userId']
	message = data['message']
	mesTime = time.time();
	if not int(cursor.execute("SELECT 1 FROM Users WHERE UserId=%s", userId)):
		return {"result": "badUserId"}
	
	cursor.execute("INSERT INTO Chat(UserId, Message, Time) VALUES (%s, %s, %s)",(userId, message, mesTime)) 
	return {"result": "ok", "mesTime": mesTime}

def act_getMessages(data):
	cursor.execute("SELECT UserId, Message, Time FROM Chat WHERE Time > %s ORDER BY Time", since)
	records =  cursor.fetchall()
	records = records[-100:]
	mesArray = []
	for rec in records:
		userId, message, mesTime = rec
		mesArray.append({"userId": userId, "message": message, "mesTime": mesTime})
                
	return {"result": "ok", "mesArray": mesArray}

def act_createDefaultMaps(data):
	for map in misc.defaultMaps:
		act_uploadMap(map)
	return {'result': 'ok'}
	
def act_uploadMap(data):
	name = data['mapName']
	if int(cursor.execute('SELECT 1 FROM Maps WHERE MapName=%s', name)):
		return {'result': 'badMapName'}
	
	players = int(data['playersNum'])
	if not ((players >= MIN_PLAYERS_NUM) and (players <= MAX_PLAYERS_NUM)):
		return {'result': 'badPlayersNum'}
	cursor.execute('INSERT INTO Maps(MapName, PlayersNum) VALUES(%s, %s)', (name, players))
	mapId = db.insert_id()
	return {'result': 'ok', 'mapId': mapId}
	
def act_createGame(data):
	#validate sid
	sid = data['sid']
	if not int(cursor.execute("SELECT GameId, Id FROM Users WHERE Sid=%s", sid)):
		return {'result': 'badSid'}
	row = cursor.fetchone()
	if row[0]:
		return {'result': 'alreadyInGame'}
	userId = row[1]
		
	#validate mapId
	mapId = data['mapId']
	if not int(cursor.execute("SELECT PlayersNum FROM Maps WHERE MapId=%s", mapId)):
		return {'result': 'badMapId'}
		
	mapPlayersNum = int(cursor.fetchone()[0])
	if 'playersNum' in data:
		playersNum = data['playersNum']
		if playersNum != mapPlayersNum:
			return {'result': 'badPlayersNum'}
		
	#validate name and description
	name = data['gameName']
	if len(name) < MIN_GAMENAME_LEN or len(name) > MAX_GAMENAME_LEN:
		return {'result': 'badGameName'}
	if int(cursor.execute("SELECT 1 FROM Games WHERE GameName=%s", name)):
		return {'result': 'badGameName'}

	descr = None
	if 'gameDescr' in data:
		descr = data['gameDescr']
	if descr and len(descr) > MAX_GAMEDESCR_LEN:
		return {'result': 'badGameDescription'}
	cursor.execute("INSERT INTO Games(GameName, GameDescr, MapId, PlayersNum, State) VALUES(%s, %s, %s, %s, %s)", 
		(name, descr, mapId, 1, misc.gameStates['waiting']))
	gameId = db.insert_id()
	cursor.execute("UPDATE Users SET GameId=%s, Readiness=0, Priority=1 WHERE Id=%s", (gameId, userId))
	return {'result': 'ok', 'gameId': gameId}
	
def act_getGameList(data):
	result = {'result': 'ok'}
	cursor.execute('SELECT * FROM Games')
	games = cursor.fetchall()
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

		cursor.execute('SELECT * FROM Maps WHERE MapId=%s', mapId)
		map = cursor.fetchone()
		curGame['map'] = dict()
		for i in range(len(mapRowNames)):
			curGame['map'][mapRowNames[i]] = map[i]

		cursor.execute('SELECT Id, Username, Readiness, Sid, Priority FROM Users WHERE GameId=%s', gameId)
		players = cursor.fetchall()
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
	if not int(cursor.execute('SELECT GameId, Id FROM Users WHERE sid=%s', sid)):
		return {'result': 'badSid'}
	row = cursor.fetchone()
	userId = row[1]
	if row[0]:
		return {'result': 'alreadyInGame'}
	
	gameId = data['gameId']
	if not int(cursor.execute('SELECT PlayersNum, MapId, State FROM Games WHERE GameId=%s', gameId)):
		return {'result': 'badGameId'}
	row = cursor.fetchone()
	if row[2] != misc.gameStates['waiting']:
		return{'result': 'badGameState'}
	cursor.execute('SELECT PlayersNum From Maps WHERE MapId=%s', row[1])
	maxPlayersNum = cursor.fetchone()[0]
	if row[0] >= maxPlayersNum:
		return {'result': 'tooManyPlayers'}

	cursor.execute('SELECT MAX(Priority) FROM Users WHERE GameId=%s', gameId)
	priority = cursor.fetchone()[0] + 1
	cursor.execute('UPDATE Users SET GameId=%s, Readiness=0, Priority=%s WHERE Id=%s', (gameId, priority, userId))
	cursor.execute('UPDATE Games SET PlayersNum=PlayersNum+1 WHERE GameId=%s', gameId)
	return {'result': 'ok'}
	
def act_leaveGame(data):
	sid = data['sid']
	if not int(cursor.execute('SELECT GameId, Id FROM Users WHERE Sid=%s', sid)):
		return {'result': 'badSid'}

	gameId, userId = cursor.fetchone()
	if not gameId:
		return {'result': 'notInGame'}
	cursor.execute('SELECT PlayersNum FROM Games WHERE GameId=%s', gameId)
	curPlayersNum = cursor.fetchone()[0]
	cursor.execute('UPDATE Users SET GameId=NULL, Readiness=NULL, Priority=NULL WHERE Id=%s', userId)
	cursor.execute('UPDATE Regions SET OwnerId=NULL WHERE OwnerId=%s', userId)
	if curPlayersNum > 1: 
		cursor.execute('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
	else:
		cursor.execute('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', 
			(misc.gameStates['ended'], gameId))
	return {'result': 'ok'}

def act_setReadinessStatus(data):
	sid = data['sid']
	if not cursor.execute('SELECT 1 FROM Users WHERE Sid=%s', sid):
		return {'result': 'badSid'}

	cursor.execute("SELECT Users.GameId, Games.State FROM Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId", sid)
	row = cursor.fetchone()
	if not (row and row[0]):
		return {'result': 'notInGame'}
	gameId, gameState = row
	if gameState != misc.gameStates['waiting']:
		return {'result': 'badGameState'}
		
	status = data['readinessStatus']
	if not(status == 0 or status == 1):
		return {'result': 'badReadinessStatus'}
	cursor.execute('UPDATE Users SET Readiness=%s WHERE sid=%s', (status, sid))
	cursor.execute('SELECT Maps.PlayersNum FROM Games, Maps WHERE Games.GameId=%s AND Games.MapId=Maps.MapId', 
		gameId)
	maxPlayersNum = cursor.fetchone()[0]
	cursor.execute('SELECT COUNT(*) FROM Users WHERE GameId=%s AND Readiness=1', gameId)
	readyPlayersNum = cursor.fetchone()[0]
	if maxPlayersNum == readyPlayersNum:
		cursor.execute('UPDATE Users SET Coins=5, Stage=%s, TokensInHand=0, CurrentRace=NULL, \
			DeclineRace=NULL, Bonus=NULL WHERE GameId=%s', (misc.userStages['waitingTurn'], gameId))
		cursor.execute('SELECT Id FROM Users WHERE Priority=(SELECT MIN(Priority) FROM Users WHERE gameId = %s)', gameId)
		actPlayer = cursor.fetchone()[0]
		cursor.execute('UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s WHERE GameId=%s', 
			(misc.gameStates['processing'], actPlayer, gameId))
		cursor.execute('UPDATE Users SET Stage=%s WHERE Id=%s', (misc.userStages['choosingRace'], actPlayer)) 
	return {'result': 'ok'}
	
def act_selectRace(data):
	sid = data['sid']
	raceId = data['raceId']
	cursor.execute('SELECT Stage, Coins, Id FROM Users WHERE Sid=%s', sid)
	row = cursor.fetchone()
	if not row: 
		return {'result': 'badSid'}
	stage, coins, userId = row
	if stage != misc.userStages['choosingRace']:	
		return {'result': 'badStage'}
	cursor.execute('SELECT InitialNum, FarFromStack, BonusId, BonusMoney FROM Races WHERE RaceId=%s', raceId)
	row = cursor.fetchone()
	if row[1] == -1 : 
		return {'result': 'badChoice'}
	num, farFromStack, bonusId, bonusMoney = row
	cursor.execute('SELECT COUNT(*) From Races WHERE FarFromStack>%s', farFromStack)
	price = cursor.fetchone()[0]
	if coins < price : 
		return {'result' : 'badMoneyAmount'}
	cursor.execute('UPDATE Users SET CurrentRace=%s, Coins=Coins-%s+%s, Bonus=%s, Stage=%s, TokensInHand=%s WHERE Sid=%s', 
		(raceId, price, bonusMoney, bonusId, misc.userStages['firstAttack'], num, sid))
	cursor.execute('UPDATE Races SET FarFromStack=-1, BonusMoney=0 WHERE RaceId=%s', raceId)
	cursor.execute('UPDATE Races SET FarFromStack=FarFromStack+1 WHERE FarFromStack >-1 AND FarFromStack<%s', farFromStack)
	cursor.execute('UPDATE Races SET BonusMoney=BonusMoney+1 WHERE FarFromStack > %s', farFromStack)
	cursor.execute('SELECT RaceId FROM Races WHERE FarFromStack=-1')
	newRaceId = cursor.fetchone()[0];
	cursor.execute('UPDATE Races SET FarFromStack=0 WHERE RaceId=%s', newRaceId)
	return {'result': 'ok'}
	
def act_conquer(data):
	regionId = data['regionId']
	sid = data['sid']
	cursor.execute('SELECT Id, Stage, TokensInHand FROM Users WHERE Sid=%s', sid)
	row = cursor.fetchone()
	if not row: 
		return {'result': 'badSid'}
	userId, stage, unitsNum = row
	if not stage in misc.userStages['firstAtack' : 'notFirstAttack']:
		return {'result': 'badStage'}
	cursor.execute('SELECT MapId, OwnerId, RaceId, TokenNum, Bordeline, Highland, \
		Coastal, Seaside, inDecline FROM Regions WHERE RegionId=%s', regionId)
	regInfo = cursor.fetchone()
	if not regInfo:
		return {'result': 'badRegion'}
	mapId = regInfo[0]
	cursor.execute('SELECT Users.GameId, Games.MapId From Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId', sid)
	rightMapId = cursor.fetchone()[1]
	if mapId != rightMapId :  ###?!!!
		return {'result': 'badRegionId'}
	ownerId = regInfo[1]
	inDecline = regInfo[8]
	if ownerId == userId and not inDecline: 
		return {'result': 'badRegion'}
	if stage == misc.userStages['firstAttack']:
		borderline, coastal = regInfo[4], regInfo[6]
		if not (borderline or coastal) : 
			return  {'result': 'badRegion'}
	else:
		cursor.execute('SELECT RegionId FROM Regions WHERE OwnerId=%s', userId)
		playerRegions = cursor.fetchall()
		playerBorderline = 0
		for plRegion in playerRegions:
			cursor.execute('SELECT Adjacent FROM AdjacentRegions WHERE FirstRegionId=%s AND SecondRegionId=%s', 
				plRegion[0], regionId)
			if row and row[0] == 1: 
				playerBorderline = 1
				break
		
		if playerBorderline == 0: 
			return {'result': 'badRegion'}
	
	unitPrice = 2 + regInfo[3] + regInfo[5]
	if unitsNum < unitsPrice : 
		return  {'result': 'notEnoughTokensInTheHand'}
	cursor.execute('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE sid=%s', (unitPrice, sid))
	cursor.execute('UPDATE Regions SET OwnerId=%s, TokenNum=%s, InDecline=0 WHERE RegionId=%s', 
		(userId, unitPrice, regionId)) 
	return {'result': 'ok'}
		
def act_decline(data):
	sid = data['sid']
	cursor.execute('SELECT Id, Stage, TokensInHand, race FROM Users WHERE Sid=%s', sid)
	row = cursor.fetchone()
	if not row: 
		return {'result': 'badSid'}
	id, stage, freeUnits, race = row
	if stage != misc.userStages['notFirstAttack']: ##
		return {'result': 'badStage'}
	cursor.execute('UPDATE Regions SET OwnerId=NULL, InDecline=0 WHERE OwnerId=%s AND InDecline=1', id)
	cursor.execute('UPDATE Regions SET InDecline=1 WHERE OwnerId=%s', id) ###
	cursor.execute('UPDATE Users SET DeclineRace=%s, CurrentRace=NULL, Stage=%s WHERE Sid=%s', 
		(race, misc.userStages['choosingRace'], sid))
	return {'result': 'ok'}
		
def act_finishTurn(data):
	sid = data['sid']
	cursor.execute('SELECT Id, GameId, Stage, TokensInHand, Priority FROM Users WHERE Sid=%s', sid)
	row = cursor.fetchone()
	if not row: 
		return {'result': 'badSid'}
	userId, gameId, stage, freeUnits, priority = row
	if not stage in misc.userStages['firstAtack' : 'declining']:
		return {'result': 'badStage'}
	cursor.execute('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s', userId)
	income = cursor.fetchone()[0]
	cursor.execute('UPDATE Users SET Stage=%s, Coins=Conis+%s WHERE Sid=%s', 
		(misc.userStages['waitingTurn'], income, sid))
	cursor.execute('SELECT Id, CurrentRace, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s FROM Users)',
			(priority, gameId))
	row = cursor.fetchone()
	if not row:
		cursor.execute('SELECT Id, CurrentRace,  FROM \
			Users WHERE Priority=(SELECT MIN(Priority) FROM Users WHERE GameId=%s) WHERE GameId=%s', gameId, gameId)
		cursor.execute('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)
		# Last Turn?
		row = cursor.fetchone()
	newActPlayer, race, tokensInHand = row
	newPlayerStage = misc.userStages['choosingRace'] if not race else (misc.userStages['firstAttack'] if 
		tokensInHand == 0 else misc.userStages['notFirstAttack'])
	cursor.execute('UPDATE Games SET ActivePlayer=%s WHERE gameId=%s', (newActPlayer, gameId))
	cursor.execute('UPDATE Users SET Stage=%s WHERE UserId=%s', (newPlayerStage, newActPlayer))
	return {'result': 'ok'}

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			return {'result': 'badAction'}
		correctness = checkFieldsCorrectness(data);
		if correctness['result'] != 'ok':
			return correctness
		res = globals()[func](data)
		db.commit()
		return res
	except MySQLdb.Error, e:
		db.rollback()
		return e
