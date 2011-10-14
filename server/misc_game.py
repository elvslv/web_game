from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, TokenBadge
import races
import misc

#def updateGameHistory(gameId, data):
#	if 'sid' in data:
#		userId = getIdBySid(data['sid'])
#		del data['sid']
#		data['userId'] = userId
#	query('INSERT INTO GameHistory(GameId, Action) VALUES(%s, %s)', gameId, 
#		json.dumps(data))

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

def clearGameStateAtTheEndOfTurn(gameId):
	pass

if __name__=='__main__':
	print generateTokenBadges(int(sys.argv[1]), int(sys.argv[2]))
