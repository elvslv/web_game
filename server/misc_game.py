from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, TokenBadge
import races
import misc
from gameExceptions import BadFieldException
import random
import sys
import db

dbi = Database()

def clearFromRace(reg):
	ans = 0
	if reg.tokenBadge:
		ans = callRaceMethod(reg.tokenBadge.raceId, 'clearRegion', reg.tokenBadge, reg)
		callSpecialPowerMethod(reg.tokenBadge.specPowId, 'clearRegion', reg.tokenBadge, reg)
	return ans

def throwDice():
	if misc.TEST_MODE: return 0
	dice = random.randint(1, 6)
	if dice > 3: dice = 0
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
		raceId = random.choice(racesInStack)
		specialPowerId = random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(game, lastIndex, vRace = None, vSpecialPower = None):
	raceId, specPowerId = getNextRaceAndPowerFromStack(game, vRace, vSpecialPower)
	tokenBadgesInStack = filter(lambda x: not x.owner and not x.inDecline and x.pos < lastIndex, game.tokenBadges) 
	for tokenBadge in tokenBadgesInStack: tokenBadge.pos += 1
	dbi.add(TokenBadge(raceId, specPowerId, game.id))
	dbi.commit()
	return races.racesList[raceId].name, races.specialPowerList[specPowerId].name, 
	
def updateRacesOnDesk(game, position):
	game.getTokenBadge(position).pos = None
	for tokenBadge in filter(lambda x: x.pos > position, game.tokenBadges):
		tokenBadge.bonusMoney += 1
	return showNextRace(game, position)

def callRaceMethod(raceId, methodName, *args):			
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def generateTokenBadges(randSeed, num):
	random.seed(randSeed)
	racesInStack = range(0, misc.RACE_NUM)
	specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
	result = list()
	for i in range(num):
		raceId = random.choice(racesInStack)
		specialPowerId = random.choice(specialPowersInStack)
		result.append({'race': races.racesList[raceId].name, 
			'specialPower': races.specialPowerList[specialPowerId].name})
		racesInStack.remove(raceId)
		specialPowersInStack.remove(specialPowerId)
	return result

def countCoins(user):
	income = len(user.regions)
	races = filter (lambda x: x, (user.currentTokenBadge, user.declinedTokenBadge))
	for race in races:
		income += callRaceMethod(race.raceId, 'incomeBonus', race)
		income += callSpecialPowerMethod(race.specPowId, 'incomeBonus', race)
	return income

def getGameState(game):
	gameAttrs = ['id', 'name', 'descr', 'state', 'turn', 'activePlayerId']
	gameNameAttrs = ['gameId', 'gameName', 'gameDescription', 'state', 
		'currentTurn', 'activePlayerId']

	result = dict()
	for i in range(len(gameResFields)):
		result[gameNameAttrs[i]] = getattr(game, gameAttrs[i])
		
	result['map'] = getMapState(game.map.id)

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
			curTokenBadge['race'] =  races.racesList[player.currentTokenBadge.raceId].name
			curTokenBadge['specialPower'] =  races.specialPowerList[player.currentTokenBadge.specPowId].name
			curPlayer['currentTokenBadge'] = curTokenBadge
			
		if player.declinedTokenBadge:
			declinedTokenBadge = dict()
			declinedTokenBadge['race'] =  races.racesList[player.declinedTokenBadge.raceId].name
			declinedTokenBadge['specialPower'] =  races.specialPowerList[player.declinedTokenBadge.specPowId].name
			curPlayer['declinedTokenBadge'] = declinedTokenBadge
			
		resPlayers.append(curPlayer)
	result['players'] = resPlayers
	result['visibleTokenBadges'] = getVisibleTokenBadges(gameId)
	return result

def endOfGame(game, coins = None): 
	game.state = GAME_ENDED
	if misc.TEST_MODE:
		return {'result': 'ok', 'coins': coins}
	else:
		gameState = getGameState(game)
		game.resetPlayersState()
		tables = ['CurrentRegionStates', 'TokenBadges']
		for table in tables:
			queryStr = 'DELETE FROM %s WHERE GameId=%%s' % table
			dbi.engine.execute(queryStr, gameId)
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
	constRegionAttrs = ['id', 'defTokensNum', 'border', 'coast', 'mountain', 
		'sea', 'mine', 'farmland', 'magic', 'forest', 'hill', 'swamp', 'cavern']
	constRegionAttrNames = ['regionId', 'defaultTokensNum', 'border', 'coast', 
		'mountain', 'sea', 'mine', 'farmland', 'magic', 'forest', 'hill', 
		'swamp', 'cavern']
	curRegionAttrs = ['tokenBadgeId', 'ownerId', 'tokensNum', 
		'holeInTheGround', 'encampment', 'dragon', 'fortress', 'hero', 'inDecline']

	for region in map_.regions:
		curReg = dict()
		for i in range(len(constRegionAttrs)):
			curReg[constRegionAttrNames[i]] = getattr(region, constRegionAttrs[i])
		curReg['adjacentRegions'] = region.getNeighbors()
		if gameId:
			curRegState = region.getState()
			for i in range(len(curRegionAttrs)):
				curReg[curRegionAttrs[i]] = getattr(curRegState, curRegionAttrs[i])
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
			if user.currentTokenBadge:
				makeDecline(user)
			if len(user.game.playersInGame()) == 0 and user.game.state == misc.GAME_PROCESSING:
					endOfGame(user.game)

def getVisibleTokensBadges(gameId):
	game = dbi.getXbyY('Game', 'id', gameId)
	rows = game.tokenBadges()
	result = list()
	for tokenBadge in filter(lambda x: x.position > 0, rows):
		result.append({
			'raceName': races.racesList[tokenBadge.raceId].name, 
			'specialPowerName': races.specialPowerList[tokenBadge.specPowerId].name,
			'position': tokenBadge.position,
			'bonusMoney': tokenBadge.bonusMoney})
	return result

def initRegions(map, game):
	for region in map.regions:
		regState = RegionState(region, game)
		dbi.add(regState)

def makeDecline(user):
	raceId, specialPowerId = user.currentTokenBadge.raceId, user.currentTokenBadge.specPowId
	if user.declinedTokenBadge:
		user.killRaceInDecline()
		dbi.delete(user.declinedTokenBadge)
	callSpecialPowerMethod(specialPowerId, 'decline', user)	
	callRaceMethod(raceId, 'decline', user)	
	user.currentTokenBadge = None

def clearGameStateAtTheEndOfTurn(gameId):
	pass

if __name__=='__main__':
	print generateTokenBadges(int(sys.argv[1]), int(sys.argv[2]))
