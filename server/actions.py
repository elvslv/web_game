import MySQLdb
import editDb
import re
import time
import misc
import actions

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

usrnameRegexp = r'^[a-z]+[\w_-]{%d,%d}$' % (MIN_USERNAME_LEN - 1, MAX_USERNAME_LEN - 1)
pwdRegexp = r'^\w{%d,%d}$' % (MIN_PASSWORD_LEN, MAX_PASSWORD_LEN)

def act_register(data):
	if not(('username' in data) and ('password' in data)):
		return {"result": "badJson"}

	username = data['username']
	passwd = data['password']
	try:
		if  not re.match(usrnameRegexp, username, re.I):
			return {"result": "badUsername"}
	except(TypeError, ValueError):
		return {"result": "badUsername"}
	try:
		if  not re.match(pwdRegexp, passwd, re.I):
			return {"result": "badPassword"}
	except(TypeError, ValueError):
		return {"result": "badPassword"}

	num = int(cursor.execute("SELECT 1 FROM Users WHERE Username=%s", username))
	if num:
		return {"result": "usernameTaken"}
	cursor.execute("INSERT INTO Users(username, password) VALUES (%s, %s)",(username, passwd))
	return {"result": "ok"}

def act_login(data):
	if not(('username' in data) and ('password' in data)):
		return {"result": "badJson"}
	username = data['username']
	passwd = data['password']
	try:
			if not int(cursor.execute("SELECT 1 FROM Users WHERE Username=%s AND Password=%s",
					(username, passwd))):
					return {'result': 'badUsernameOrPassword'}
	except(TypeError, ValueError), e:
			return {'result': 'badUsernameOrPassword'}

	while 1:
			sid = misc.generateSidForTest()
			if not int(cursor.execute("SELECT 1 FROM Users WHERE Sid=%s", sid)):
					break
			
	cursor.execute("UPDATE Users SET Sid=%s WHERE Username=%s", (sid, username))
	return {"result": "ok", "sid": long(sid)}

def act_logout(data):
	if not('sid' in data):
		return {"result": "badJson"}

	sid = data['sid']
	try:
		if not int(cursor.execute("UPDATE Users SET Sid=NULL WHERE Sid=%s", sid)):
			return {"result": "badSid"}
		return {"result": "ok"}
	except(TypeError, ValueError):
		return {"result": "badSid"}

def act_doSmth(data):
	if not('sid' in data):
		return {"result": "badJson"}

	sid = data['sid']
	try:
		if not int(cursor.execute("SELECT id FROM Users WHERE Sid=%s", sid)):
			return {"result": "badSid"}
		return {"result": "ok"}
	except(TypeError, ValueError):
		return {"result": "badSid"}

def act_sendMessage(data):
	if not(('userid' in data) and ('message' in data)):
			return {"result": "badJson"}
		
	userId = data['userid']
	message = data['message']
	mesTime = time.time();
	try:
		if not int(cursor.execute("SELECT 1 FROM Users WHERE UserId=%s", userId)):
			return {"result": "badUserId"}
	except (TypeError, ValueError):
		return {"result": "badUserId"}
	
	cursor.execute("INSERT INTO Chat(userid, message, time) VALUES (%s, %s, %s)",(userId, message, mesTime)) 
	return {"result": "ok", "mesTime": mesTime}

def act_getMessages(data):
	if not('since' in data):
		return {"result": "badJson"}
	try:
		cursor.execute("SELECT UserId, Message, Time FROM Chat WHERE Time > %s ORDER BY Time", since)
	except (TypeError, ValueError), e:
		return {"result": "badTime"}
	records =  cursor.fetchall()
	records = records[-100:]
	mesArray = []
	for rec in records:
		user_id, message, mes_time = rec
		mesArray.append({"userid": userId, "message": message, "mesTime": mesTime})
                
	return {"result": "ok", "mesArray": mesArray}

def act_uploadMap(data):
	if not(('mapName' in data) and ('playersNum' in data)):
		return {'result': 'badJson'}
	
	name = data['mapName']
	try:
		if int(cursor.execute('SELECT 1 FROM Maps WHERE MapName=%s', name)):
			return {'result': 'badMapName'}
	except (TypeError, ValueError):
		return {'result': 'badMapName'}
	
	try:
		players = int(data['playersNum'])
		if not ((players >= 2) and (players <= 5)):
			return {'result': 'badPlayersNum'}
		cursor.execute('INSERT INTO Maps(MapName, PlayersNum) VALUES(%s, %s)', (name, players))
		mapId = db.insert_id()
		return {'result': 'ok', 'mapId': mapId}
	except(TypeError, ValueError):
		return {'result': 'badPlayersNum'}
	
gameStates = {'waiting': 1, 'processing': 2, 'ended': 3}
	
def act_createGame(data):
	if not(('sid' in data) and ('gameName' in data) and ('mapId' in data)):
		return {'result': 'badJson'}
	#validate sid
	sid = data['sid']
	try:
		if not int(cursor.execute("SELECT GameId FROM Users WHERE Sid=%s", sid)):
			return {'result': 'badSid'}
		if cursor.fetchone()[0]:
			return {'result': 'alreadyInGame'}
	except (TypeError, ValueError), e:
		return {"result": "badSid"}
		
	#validate mapId
	mapId = data['mapId']
	try:
		if not int(cursor.execute("SELECT PlayersNum FROM Maps WHERE MapId=%s", mapId)):
			return {'result': 'badMap'}
	except (TypeError, ValueError), e:
		return {'result': 'badMap'}
		
	mapPlayersNum = int(cursor.fetchone()[0])
	if 'playersNum' in data:
		playersNum = data['playersNum']
		if playersNum != mapPlayersNum:
			return {'result': 'badNumberOfPlayers'}
		
	#validate name and description
	name = data['gameName']
	if len(name) < MIN_GAMENAME_LEN or len(name) > MAX_GAMENAME_LEN:
		return {'result': 'badGameName'}
	try:
		if int(cursor.execute("SELECT 1 FROM Games WHERE GameName=%s", name)):
			return {'result': 'badGameName'}
	except(TypeError, ValueError), e:
		return {'result': 'badGameName'}

	descr = 'Default description'
	if 'gameDescr' in data:
		descr = data['gameDescr']
	if len(descr) > MAX_GAMEDESCR_LEN:
		return {'result': 'badGameDescription'}
	
	try:
		cursor.execute("INSERT INTO Games(GameName, GameDescr, MapId, PlayersNum, State) VALUES(%s, %s, %s, %s, %s)", 
			(name, descr, mapId, 1, gameStates['waiting']))
		gameId = db.insert_id()
		cursor.execute("UPDATE Users SET GameId=%s, Readiness=0 WHERE sid=%s", (gameId, sid))
		return {'result': 'ok', 'gameId': gameId}
	except(TypeError, ValueError), e:
		return {'result': 'badGameDescription'}
	
def act_getGameList(data):
	try:
		result = {'result': 'ok'}
		cursor.execute('SELECT * FROM Games')
		games = cursor.fetchall()
		result['games'] = list()
		gameRowNames = ['gameId', 'gameName', 'gameDescr', 'playersNum', 'state']
		mapRowNames = ['mapId', 'mapName', 'playersNum']
		playerRowNames = ['userId', 'username', 'state', 'sid']
		for game in games:
			curGame = dict()
			for i in range(len(gameRowNames)):
				if not (gameRowNames[i] == 'gameDescr' and game[i] == 'Default description'):
					curGame[gameRowNames[i]] = game[i]
			gameId = game[0]
			mapId = game[len(game) - 1]
			cursor.execute('SELECT * FROM Maps WHERE MapId=%s', mapId)
			map = cursor.fetchone()
			curGame['map'] = dict()
			for i in range(len(mapRowNames)):
				curGame['map'][mapRowNames[i]] = map[i]
			cursor.execute('SELECT Id, UserName, Readiness, Sid FROM Users WHERE GameId=%s', gameId)
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
	except BaseException, e:
		return {'result': 'unknown'}

def act_joinGame(data):
	if not(('sid' in data) and('gameId' in data)):
		return {'result': 'badJson'}
	
	sid = data['sid']
	try:
		cursor.execute('SELECT GameId FROM Users WHERE sid=%s', sid)
		if cursor.fetchone()[0]:
			return {'result': 'alreadyInGame'}
	except (TypeError, ValueError):
		return {'result': 'badSid'}
	
	gameId = data['gameId']
	try:
		num = int(cursor.execute('SELECT PlayersNum, MapId, State FROM Games WHERE GameId=%s', gameId))
		if num == 0:
			return {'result': 'badGameId'}
		row = cursor.fetchone()
		if row[2] != gameStates['waiting']:
			return{'result': 'badGameState'}
		cursor.execute('SELECT PlayersNum From Maps WHERE MapId=%s', row[1])
		maxPlayersNum = cursor.fetchone()[0]
		if row[0] >= maxPlayersNum:
			return {'result': 'tooManyPlayers'}
	except(TypeError, ValueError), e:
		return {'result': 'badGameId'}
	
	cursor.execute('UPDATE Users SET GameId=%s, Readiness=0 WHERE Sid=%s', (gameId, sid))
	cursor.execute('UPDATE Games SET PlayersNum=PlayersNum+1 WHERE GameId=%s', gameId)
	return {'result': 'ok'}
	
def act_leaveGame(data):
	if not ('sid' in data):
		return {'result': 'badJson'}
	
	sid = data['sid']
	try:
		cursor.execute('SELECT GameId FROM Users WHERE Sid=%s', sid)
		gameId = cursor.fetchone()[0]
		if not gameId:
			return {'result': 'notInGame'}
		cursor.execute('SELECT PlayersNum FROM Games WHERE GameId=%s', gameId)
		curPlayersNum = cursor.fetchone()[0]
		cursor.execute('UPDATE Users SET GameId=NULL, Readiness=NULL WHERE Sid=%s', sid)
		if curPlayersNum > 1: 
			cursor.execute('UPDATE Games SET PlayersNum=PlayersNum-1 WHERE GameId=%s', gameId)
		else:
			cursor.execute('UPDATE Games SET PlayersNum=0, State=%s WHERE GameId=%s', 
				(gameStates['ended'], gameId))
		return {'result': 'ok'}
	except(TypeError, ValueError):
		return {'result': 'badSid'}

def act_setReadinessStatus(data):
	if not(('sid' in data) and ('status' in data)):
		return {'result': 'badJson'}
	
	sid = data['sid']
	try:
		cursor.execute("SELECT Users.GameId, Games.State FROM Users, Games WHERE Users.Sid=%s AND Users.GameId=Games.GameId", sid)
		row = cursor.fetchone()
		if not row:
			return {'result': 'notInGame'}
		gameId = row[0]
		if not gameId:
			return {'result': 'notInGame'}
			
		gameState = row[1]
		if gameState != gameStates['waiting']:
			return {'result': 'badGameState'}
			
		status = data['status']
		if not(status == 0 or status == 1):
			return {'result': 'badReadinessStatus'}
		cursor.execute('UPDATE Users SET Readiness=%s WHERE sid=%s', (status, sid))
		cursor.execute('SELECT Maps.PlayersNum FROM Games, Maps WHERE Games.GameId=%s AND Games.MapId=Maps.MapId', 
			gameId)
		maxPlayersNum = cursor.fetchone()[0]
		cursor.execute('SELECT COUNT(*) FROM Users WHERE GameId=%s and Readiness=1', gameId)
		readyPlayersNum = cursor.fetchone()[0]
		if maxPlayersNum == readyPlayersNum:
			cursor.execute('UPDATE Games SET State=%s WHERE gameId=%s', (gameStates['processing'], gameId))
		return {'result': 'ok'}
	except(TypeError, ValueError), e:
		return {'result': 'badSid'}
	

def doAction(data):
	try:
		func = 'act_%s' % data['action'] 
		if not(func in globals()):
			return {'result': 'badAction'}
		res = globals()[func](data)
		db.commit()
		return res
	except MySQLdb.Error, e:
		db.rollback()
		return e
