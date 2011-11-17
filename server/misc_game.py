from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, TokenBadge, dbi
import races
import misc
from gameExceptions import BadFieldException
import sys
import db
from sqlalchemy import and_
from sqlalchemy.sql.expression import asc

def generateNextNum(game):
	game.prevGeneratedNum = (misc.A * game.prevGeneratedNum) % misc.M
	dbi.commit()
	return game.prevGeneratedNum

def clearFromRace(reg):
	ans = 0
	if reg.tokenBadge:
		ans = callRaceMethod(reg.tokenBadge.raceId, 'clearRegion', reg.tokenBadge, reg)
		callSpecialPowerMethod(reg.tokenBadge.specPowId, 'clearRegion', reg.tokenBadge, reg)
	return ans

def throwDice(game):
	if misc.TEST_MODE: return 0
	dice = generateNextNum(game) % 6
	if dice > 2: dice = 0
	return dice

def prepareForNextTurn(game, newActPlayer):
	game.activePlayerId = newActPlayer.id
	if newActPlayer.currentTokenBadge:
		addUnits =  callRaceMethod(newActPlayer.currentTokenBadge.raceId,
			'turnStartReinforcements', newActPlayer)
		newActPlayer.tokensInHand += addUnits -len(newActPlayer.regions) + newActPlayer.currentTokenBadge.totalTokensNum
		for region in newActPlayer.currentTokenBadge.regions:
			region.tokensNum = 1
		
def getNextRaceAndPowerFromStack(game, vRace, vSpecialPower):
	if vRace != None and vSpecialPower !=None:
		race = filter(lambda x: x.name == vRace, races.racesList) 
		if not race: raise BadFieldException('badRace')
		raceId = races.racesList.index(race[0])
		specialPower = filter(lambda x: x.name == vSpecialPower, races.specialPowerList) 
		if not specialPower: 
			raise BadFieldException('badSpecialPower')
		specialPowerId = races.specialPowerList.index(specialPower[0])
	else:
		racesInStack = range(0, misc.RACE_NUM)
		specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
		for tokenBadge in game.tokenBadges:
			racesInStack.remove(tokenBadge.raceId)
			specialPowersInStack.remove(tokenBadge.specPowId)
		raceId = racesInStack[generateNextNum(game) % len(racesInStack)]
		specialPowerId = specialPowersInStack[generateNextNum(game) % len(specialPowersInStack)]
	return raceId, specialPowerId

def showNextRace(game, lastIndex, vRace = None, vSpecialPower = None):
	raceId, specPowerId = getNextRaceAndPowerFromStack(game, vRace, vSpecialPower)
	tokenBadgesInStack = filter(lambda x: not x.owner and not x.inDecline and x.pos < lastIndex, game.tokenBadges) 
	for tokenBadge in tokenBadgesInStack: tokenBadge.pos += 1
	dbi.add(TokenBadge(raceId, specPowerId, game.id))
	dbi.commit()
	return races.racesList[raceId].name, races.specialPowerList[specPowerId].name, 
	
def updateRacesOnDesk(game, position):
	for tokenBadge in filter(lambda x: x.pos > position, game.tokenBadges):
		tokenBadge.bonusMoney += 1
	return showNextRace(game, position)

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
	tokensNum = lastAttack.victimTokensNum + callRaceMethod(lastAttack.victimBadge.raceId, 
		'sufferCasualties_', lastAttack.victimBadge)
	if not tokensNum:
		return
	result['playerId'] = lastAttack.victimBadge.owner.id
	result['tokensNum'] = tokensNum
	result['regionId'] = lastAttack.conqRegion.id
	return result

def hasDragonAttacked(game):
	histEntry = filter(lambda x : x.turn == game.turn and x.state == misc.GAME_CONQUER and 
		x.warHistory.attackType == misc.ATTACK_DRAGON, game.history)
	return True if len(histEntry) > 0 else False 
	
	

def getFriendsInfo(game):
	turn = game.turn
	histEntry = filter(lambda x : x.turn == turn and x.state == misc.GAME_CHOOSE_FRIEND,
		game.history)
	if histEntry:
		return {'masterId': histEntry[0].userId, 'slaveId': histEntry[0].friend}
	histEntry = filter(lambda x : x.turn == turn - 1 and x.state == misc.GAME_CHOOSE_FRIEND,
		game.history)
	if histEntry:
		attackedUser = dbi.getXbyY('User', 'id', histEntry[0].friend)
		if histEntry[0].user.priority > attackedUser.priority:
			return {'masterId': histEntry[0].userId, 'slaveId': histEntry[0].friend} 
	
def getGameState(game):
	gameAttrs = ['id', 'name', 'descr', 'state', 'turn', 'activePlayerId']
	gameNameAttrs = ['gameId', 'gameName', 'gameDescription', 'state', 
		'currentTurn', 'activePlayerId']
	result = dict()
	if game.history:
		result['lastEvent'] = game.getLastState()
	result['dragonAttacked'] = hasDragonAttacked(game)
	for i in range(len(gameNameAttrs)):
		result[gameNameAttrs[i]] = getattr(game, gameAttrs[i])

	defendingInfo = getDefendingInfo(game)
	if defendingInfo:
		result['defendingInfo'] = defendingInfo

	friendsInfo = getFriendsInfo(game)
	if friendsInfo:
		result['friendsInfo'] = friendsInfo
		
	result['map'] = getMapState(game.map.id, game.id)
	playerAttrs = ['id', 'name', 'isReady', 'inGame', 'coins', 'tokensInHand']
	playerAttrNames = ['userId', 'username', 'isReady', 'inGame' 'coins', 
		'tokensInHand']
	players = game.players
	resPlayers = list()
	priority = 0
	for player in players:
		curPlayer = dict()
		for i in range(len(playerAttrs)):
			curPlayer[playerAttrs[i]] = getattr(player, playerAttrs[i])

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
	if misc.TEST_MODE:
		return {'result': 'ok', 'coins': coins}
	else:
		gameState = getGameState(game)
		game.resetPlayersState()
		dbi.delete(game)
		dbi.commit()
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
		'holeInTheGround', 'encampment', 'dragon', 'fortress', 'hero', 'inDecline']
	for region in map_.regions:
		curReg = dict()
		curReg['raceCoords'] = region.raceCoords
		curReg['powerCoords'] = region.powerCoords
		curReg['coordinates'] = region.coordinates
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
		if user.game.state == misc.GAME_WAITING:
			if len(user.game.playersInGame()) == 0:
				user.game.state = misc.GAME_ENDED
			user.game = None
		else:
			if user.currentTokenBadge or user.declinedTokenBadge:
				makeDecline(user, True)
			if len(user.game.playersInGame()) == 0 and user.game.state == misc.GAME_PROCESSING:
					endOfGame(user.game)

def getVisibleTokenBadges(gameId):
	rows = dbi.query(TokenBadge).filter(and_(TokenBadge.gameId == gameId, TokenBadge.pos >= 0)).order_by(asc(TokenBadge.pos))
	result = list()
	for tokenBadge in rows:
		result.append({
			'raceName': races.racesList[tokenBadge.raceId].name, 
			'specialPowerName': races.specialPowerList[tokenBadge.specPowId].name,
			'position': tokenBadge.pos,
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

