from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, TokenBadge, dbi
import races
import misc_const
from gameExceptions import BadFieldException
import sys
import db
from sqlalchemy import and_
from sqlalchemy.sql.expression import asc
import random
import math
import time
import json

def startGame(game, user, data):
	game.activePlayerId = min(game.players, key=lambda x: x.priority).id
	game.state = misc_const.GAME_START
	dbi.flush(game)
	#generate first 6 races
	if misc_const.TEST_MODE and 'visibleRaces' in data and 'visibleSpecialPowers' in data:
		vRaces = data['visibleRaces']
		vSpecialPowers = data['visibleSpecialPowers']
		for i in range(min(len(vRaces), len(vSpecialPowers))):
			showNextRace(game, 0, vRaces[i], vSpecialPowers[i])
	else:
		for i in range(misc_const.VISIBLE_RACES):
			showNextRace(game, 0)
			
	dbi.updateHistory(user, misc_const.GAME_START, None)

def getSid():
	if not misc_const.TEST_MODE:
		random.seed(math.trunc(time.time()))
	sid = None
	while 1:
		sid = misc_const.generateSidForTest() if misc_const.TEST_MODE else random.getrandbits(30)
		if not dbi.getXbyY('User', 'sid', sid, False): break
	return sid

def generateNextNum(game):
	game.prevGeneratedNum = (misc_const.A * game.prevGeneratedNum) % misc_const.M
	dbi.flush(game)
	return game.prevGeneratedNum

def clearFromRace(reg):
	ans = 0
	if reg.tokenBadge:
		ans = callRaceMethod(reg.tokenBadge.raceId, 'clearRegion', reg.tokenBadge, reg)
		callSpecialPowerMethod(reg.tokenBadge.specPowId, 'clearRegion', reg.tokenBadge, reg)
	return ans

def throwDice(game, dice = None):
	if misc_const.TEST_MODE: 
		return dice if dice is not None else 0
	dice = generateNextNum(game) % 6
	if dice > 2: dice = 0
	return dice

def prepareForNextTurn(game, newActPlayer):
	game.activePlayerId = newActPlayer.id
	if newActPlayer.currentTokenBadge:
		addUnits =  callRaceMethod(newActPlayer.currentTokenBadge.raceId, 'turnStartReinforcements')
		newActPlayer.tokensInHand = addUnits - len(newActPlayer.regions) + newActPlayer.currentTokenBadge.totalTokensNum
		for region in newActPlayer.currentTokenBadge.regions:
			region.tokensNum = 1
		
def getNextRaceAndPowerFromStack(game, vRace, vSpecialPower):
	if vRace != None and vSpecialPower !=None:
		race = filter(lambda x: x.name == vRace, races.racesList) 
		if not race: 
			raise BadFieldException('badRace')
		raceId = races.racesList.index(race[0])
		specialPower = filter(lambda x: x.name == vSpecialPower, races.specialPowerList) 
		if not specialPower: 
			raise BadFieldException('badStage')
		specialPowerId = races.specialPowerList.index(specialPower[0])
	else:
		racesInStack = range(0, misc_const.RACE_NUM)
		specialPowersInStack = range(0, misc_const.SPECIAL_POWER_NUM)
		tokenBadges = dbi.query(TokenBadge).filter(TokenBadge.gameId == game.id).all()
		for tokenBadge in tokenBadges:
			racesInStack.remove(tokenBadge.raceId)
			specialPowersInStack.remove(tokenBadge.specPowId)
		if misc_const.TEST_MODE:
			raceId = random.choice(racesInStack)
			specialPowerId = random.choice(specialPowersInStack)
		else:
			raceId = racesInStack[generateNextNum(game) % len(racesInStack)]
			specialPowerId = specialPowersInStack[generateNextNum(game) % len(specialPowersInStack)]
	return raceId, specialPowerId

def showNextRace(game, lastIndex, vRace = None, vSpecialPower = None):
	raceId, specPowerId = getNextRaceAndPowerFromStack(game, vRace, vSpecialPower)
	tokenBadges = dbi.query(TokenBadge).filter(TokenBadge.gameId == game.id).all()
	tokenBadgesInStack = filter(lambda x: not x.Owner() and not x.inDecline and x.pos > lastIndex, tokenBadges) 
	for tokenBadge in tokenBadgesInStack: 
		tokenBadge.pos -= 1
		dbi.flush(tokenBadge)
	tokBadge = TokenBadge(raceId, specPowerId, game.id)
	dbi.add(tokBadge)
	dbi.flush(tokBadge)
	return races.racesList[raceId].name, races.specialPowerList[specPowerId].name, 
	
def updateRacesOnDesk(game, position):
	for tokenBadge in filter(lambda x: x.pos < position, game.tokenBadges):
		tokenBadge.bonusMoney += 1
	if len(filter(lambda x: x.pos is not None, game.tokenBadges)) < 6:
		showNextRace(game, position)
	else:
		tokenBadges = dbi.query(TokenBadge).filter(TokenBadge.gameId == game.id).all()
		tokenBadgesInStack = filter(lambda x: not x.Owner() and not x.inDecline and x.pos > position, tokenBadges) 
		for tokenBadge in tokenBadgesInStack: 
			tokenBadge.pos -= 1
			dbi.flush(tokenBadge)


def callRaceMethod(raceId, methodName, *args):			
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def countCoins(user):
	statistics = list()
	income = len(user.regions)
	statistics.append(['Regions', income])
	tokenBadges = filter (lambda x: x, (user.currentTokenBadge, user.declinedTokenBadge))
	for race in tokenBadges:
		m = callRaceMethod(race.raceId, 'incomeBonus', race)
		statistics.append([races.racesList[race.raceId].name, m])
		income += m
		m = callSpecialPowerMethod(race.specPowId, 'incomeBonus', race)
		statistics.append([races.specialPowerList[race.specPowId].name, m])
		income += m
	return {'totalCoinsNum': income, 'statistics': statistics}

def getDefendingInfo(game):
	if not (len(game.history) and game.history[-1].warHistory and game.history[-1].warHistory.victimBadge):
		return 
	result = dict()
	lastAttack = game.history[-1].warHistory
	if lastAttack.attackType == misc_const.ATTACK_ENCHANT or lastAttack.victimBadge.inDecline:
		return
	tokensNum = lastAttack.victimTokensNum - callRaceMethod(lastAttack.victimBadge.raceId, 'getCasualties')
	if not (tokensNum and len(lastAttack.victimBadge.regions)):
		return
	result['playerId'] = lastAttack.victimBadge.Owner().id
	#result['tokensNum'] = tokensNum
	result['regionId'] = lastAttack.conqRegion.id
	return result

def hasDragonAttacked(game):
	histEntry = filter(lambda x : x.turn == game.turn and x.state == misc_const.GAME_CONQUER and 
		x.warHistory.attackType == misc_const.ATTACK_DRAGON, game.history)
	return True if len(histEntry) > 0 else False 

def hasEnchanted(game):
	histEntry = filter(lambda x : x.turn == game.turn and x.state == misc_const.GAME_CONQUER and 
		x.warHistory.attackType == misc_const.ATTACK_ENCHANT, game.history)
	return True if len(histEntry) > 0 else False 

def countHolesNum(game):
	if not game.activePlayer() or not game.activePlayer().currentTokenBadge or\
		game.activePlayer().currentTokenBadge.raceId != 5:
		return None
	return min(len(filter(lambda x : x.state == misc_const.GAME_CONQUER and\
		x.warHistory.agressorBadgeId == game.activePlayer().currentTokenBadgeId, 
		game.history)), 2)

def getBerserkDice(game):
	if not game.activePlayer() or not game.activePlayer().currentTokenBadge or\
		game.activePlayer().currentTokenBadge.specPowId != 1:
		return None
	return game.getLastState() == misc_const.GAME_THROW_DICE and game.history[-1].dice

def usedStout(game):
	if not game.activePlayer() or not game.activePlayer().currentTokenBadge or\
		game.activePlayer().currentTokenBadge.specPowId != 15:
		return None
	return True if len(filter(lambda x : x.turn == game.turn and x.state == misc_const.GAME_DECLINE and\
		x.userId == game.activePlayerId, game.history)) else False

def gotWealth(game):
	if not game.activePlayer() or not game.activePlayer().currentTokenBadge or\
		game.activePlayer().currentTokenBadge.specPowId != 18:
		return None
	return True if len(filter(lambda x : x.tokenBadgeId == game.activePlayer().currentTokenBadge.id and\
		x.state == misc_const.GAME_FINISH_TURN, game.history)) else False

def getFriendsInfo(game):
	turn = game.turn
	histEntry = filter(lambda x : x.turn == turn and x.state == misc_const.GAME_CHOOSE_FRIEND,
		game.history)
	if histEntry:
		return {'diplomatId': histEntry[0].userId, 'friendId': histEntry[0].friend}
	histEntry = filter(lambda x : x.turn == turn - 1 and x.state == misc_const.GAME_CHOOSE_FRIEND,
		game.history)
	if histEntry:
		attackedUser = dbi.getXbyY('User', 'id', histEntry[0].friend)
		if histEntry[0].user.priority > attackedUser.priority:
			return {'diplomatId': histEntry[0].userId, 'friendId': histEntry[0].friend} 
	
def getGameState(game):
	if game.state == misc_const.GAME_ENDED:
		return {'result': 'ok', 'statistics': json.loads(game.gameHistory[-2].action),'ended': True}
		
	gameAttrs = ['id', 'name', 'descr', 'state', 'turn', 'activePlayerId']
	gameNameAttrs = ['gameId', 'gameName', 'gameDescription', 'state', 
		'currentTurn', 'activePlayerId']
	result = dict()
	if game.history:
		result['lastEvent'] = game.getLastState()
		
	f = hasDragonAttacked(game)
	if f is not None:
		result['dragonAttacked'] = f

	f = hasEnchanted(game)
	if f is not None:
		result['enchanted'] = f

	f = countHolesNum(game)
	if f is not None:
		result['holesNum'] = f

	f = getBerserkDice(game)
	if f is not None:
		result['berserkDice'] = f

	f = usedStout(game)
	if f is not None:
		result['usedStout'] = f

	f = gotWealth(game)
	if f is not None:
		result['gotWealth'] = f

	for i in range(len(gameNameAttrs)):
		result[gameNameAttrs[i]] = getattr(game, gameAttrs[i])
	if not game.descr:
		result['gameDescription'] = ''
	defendingInfo = getDefendingInfo(game)
	if defendingInfo:
		result['defendingInfo'] = defendingInfo

	friendsInfo = getFriendsInfo(game)
	if friendsInfo:
		result['friendsInfo'] = friendsInfo
		
	result['map'] = getMapState(game.map.id, game.id)
	playerAttrs = ['id', 'name', 'isReady', 'inGame', 'coins', 'tokensInHand']
	playerAttrNames = ['userId', 'username', 'isReady', 'inGame', 'coins', 
		'tokensInHand']
	players = game.players
	resPlayers = list()
	priority = 0
	for player in players:
		curPlayer = dict()
		for i in range(len(playerAttrs)):
			curPlayer[playerAttrNames[i]] = getattr(player, playerAttrs[i])
		priority += 1	
		curPlayer['priority'] = priority
		
		if player.currentTokenBadge:
			curTokenBadge = dict()
			curTokenBadge['raceName'] =  races.racesList[player.currentTokenBadge.raceId].name
			curTokenBadge['specialPowerName'] =  races.specialPowerList[player.currentTokenBadge.specPowId].name
			curTokenBadge['tokenBadgeId'] = player.currentTokenBadge.id
			curTokenBadge['totalTokensNum'] = player.currentTokenBadge.totalTokensNum
			curPlayer['currentTokenBadge'] = curTokenBadge
			
		if player.declinedTokenBadge:
			declinedTokenBadge = dict()
			declinedTokenBadge['raceName'] =  races.racesList[player.declinedTokenBadge.raceId].name
			declinedTokenBadge['specialPowerName'] =  races.specialPowerList[player.declinedTokenBadge.specPowId].name
			declinedTokenBadge['tokenBadgeId'] = player.declinedTokenBadge.id
			declinedTokenBadge['totalTokensNum'] = player.declinedTokenBadge.totalTokensNum
			curPlayer['declinedTokenBadge'] = declinedTokenBadge
			
		resPlayers.append(curPlayer)
	result['players'] = resPlayers
	result['visibleTokenBadges'] = getVisibleTokenBadges(game.id)
	return result


def endOfGame(game, coins = None): 
	game.state = GAME_ENDED
	if misc_const.TEST_MODE:
		return {'result': 'ok', 'coins': coins}
	else:
		gameState = getGameState(game)
		game.resetPlayersState()
		dbi.delete(game)
		dbi.flush(game)
		return {'result': 'ok', 'gameState': gameState}

def getShortMapState(map_):
	result = dict()
	mapAttrs = ['id', 'name', 'playersNum', 'turnsNum', 'thumbSrc', 'pictureSrc']
	mapAttrNames = ['mapId', 'mapName', 'playersNum', 'turnsNum', 'thumbnail', 
		'picture']
	for i in range(len(mapAttrs)):
		result[mapAttrNames[i]] = getattr(map_, mapAttrs[i])
	return result

def getMapState(mapId, gameId = None):
	map_ = dbi.getXbyY('Map', 'id', mapId)
	result = getShortMapState(map_)
	result['regions'] = list()
	constRegionAttrs = ['border', 'coast', 'mountain', 
		'sea', 'mine', 'farmland', 'magic', 'forest', 'hill', 'swamp', 'cavern']
	curRegionAttrs = ['tokenBadgeId', 'ownerId', 'tokensNum', 
		'holeInTheGround', 'encampment', 'dragon', 'hero', 'fortified', 'inDecline']
	for region in map_.regions:
		curReg = dict()
		toArray = lambda x: json.loads('{ "a" : ' + x + '}')['a']
		curReg['raceCoords'] = toArray(region.raceCoords)
		curReg['powerCoords'] = toArray(region.powerCoords)
		curReg['coordinates'] = toArray(region.coordinates)
		curReg['constRegionState'] = list()
		
		for i in range(len(constRegionAttrs)):
			attr = getattr(region, constRegionAttrs[i])
			if not attr: continue
			if constRegionAttrs[i] in ('mountain', 'forest', 'hill', 'swamp', 'sea', 'farmland'):
				curReg['landscape'] = constRegionAttrs[i]
			elif constRegionAttrs[i] in ('mine', 'cavern', 'magic'):
				curReg['bonus'] = constRegionAttrs[i]
			curReg['constRegionState'].append(constRegionAttrs[i])
			 
				
		curReg['adjacentRegions'] = region.getNeighbors()
		if gameId:
			curRegState = region.getState(gameId)
			curReg['currentRegionState'] = dict()
			for i in range(len(curRegionAttrs)):
				curReg['currentRegionState'][curRegionAttrs[i]] = getattr(curRegState, curRegionAttrs[i])
		result['regions'].append(curReg)
	return result


def leave(user):
	user.inGame = False;
	if user.game:
		if user.game.state == misc_const.GAME_WAITING:
			if len(user.game.playersInGame()) == 0:
				user.game.state = misc_const.GAME_ENDED
			user.game = None
		else:
			if user.currentTokenBadge:
				makeDecline(user, True)
			if len(user.game.playersInGame()) == 0 and user.game.state == misc_const.GAME_PROCESSING:
					user.game.endOfGame()

def getVisibleTokenBadges(gameId):
	rows = dbi.query(TokenBadge).filter(and_(TokenBadge.gameId == gameId, TokenBadge.pos >= 0)).order_by(asc(TokenBadge.pos))
	result = list()
	for tokenBadge in rows[:6]:
		result.append({
			'tokenBadgeId': tokenBadge.id,
			'raceName': races.racesList[tokenBadge.raceId].name, 
			'specialPowerName': races.specialPowerList[tokenBadge.specPowId].name,
			'bonusMoney': tokenBadge.bonusMoney})
	return result

def initRegions(map, game):
	for region in map.regions:
		regState = RegionState(region, game)
		dbi.add(regState)

def makeDecline(user, leaveGame = False):
	raceId, specialPowerId = user.currentTokenBadge.raceId, user.currentTokenBadge.specPowId
	if user.declinedTokenBadge:
		user.killRaceInDecline()
		dbi.delete(user.declinedTokenBadge)
	callSpecialPowerMethod(specialPowerId, 'decline', user, leaveGame)	
	callRaceMethod(raceId, 'decline', user, leaveGame)	
	user.currentTokenBadge = None

def clearGameStateAtTheEndOfTurn(gameId):
	pass

def checkStage(state, user, attackType = None):
	game = user.game
	lastEvent = game.history[-1]
	badStage = not (lastEvent.state in misc_const.possiblePrevCmd[state]) 
	if attackType:
		curTurnHistory = filter(lambda x: x.turn == user.game.turn and 
			x.userId == user.id and x.state == misc_const.GAME_CONQUER, 
			game.history)
		if curTurnHistory:
			if filter(lambda x: x.warHistory.attackType == attackType, curTurnHistory):
				badStage = True
	if lastEvent.state == misc_const.GAME_CONQUER:
		battle = lastEvent.warHistory
		victim = battle.victimBadge
		canDefend = victim != None  and\
			not victim.inDecline and\
			battle.attackType != misc_const.ATTACK_ENCHANT and\
			battle.victimTokensNum > callRaceMethod(victim.raceId, 'getCasualties') and\
			len(victim.regions) > 0 
		badStage |= (canDefend != (state == misc_const.GAME_DEFEND)) or\
			(state == misc_const.GAME_DEFEND and user.currentTokenBadge != victim)
	if badStage or (user.id != game.activePlayerId and state != misc_const.GAME_DEFEND):
		raise BadFieldException('badStage')

