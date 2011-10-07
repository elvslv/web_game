import races
import misc
from gameExceptions import BadFieldException
import random
import sys
import db

dbi = db.Database()

def getNextRaceAndPowerFromStack(gameId, vRace, vSpecialPower):
        if vRace != None and vSpecialPower !=None:
                raceId = -1
                for i in range(len(races.racesList)):
                        if vRace == races.racesList[i].name:
                                raceId = i
                                break
                if raceId == -1:
                        raise BadFieldException('badRace')
                specialPowerId = -1
                for i in range(len(races.specialPowerList)):
                        if vSpecialPower == races.specialPowerList[i].name:
                                specialPowerId = i
                                break
                if specialPowerId == -1:
                        raise BadFieldException('badSpecialPower')
        else:
                racesInStack = range(0, misc.RACE_NUM)
                specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
                row = game.tokenBadges
                for rec in row:
                        racesInStack.remove(rec.raceId)
                        specialPowersInStack.remove(rec.specPowerId)
                raceId = random.choice(racesInStack)
                specialPowerId = random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(gameId, lastIndex, vRace = None, vSpecialPower = None):
	raceId, specialPowerId = getNextRaceAndPowerFromStack(gameId, vRace, vSpecialPower)
	tokenBadgesInStack = dbi.query(TokenBadge).filter(TokenBadge.gameId==gameId).\
										      filter(TokenBadge.position< lastIndex).\
										      all()
	for tokenBadge in tokenBadgesInStack: tokenBadge.pos += 1
	dbi.add(TokenBadge(raceId, specPowerId, gameId))
	return races.racesList[raceId].name, races.specialPowerList[specialPowerId].name, 
	
def updateRacesOnDesk(game, position):
	dbi.getTokenBadgeByPosition(position).position = None
	for tokenBadge in filter(lambda x: x.position > position, game.tokenBadges):
		tokenBadge.bonusMoney += 1
	return showNextRace(gameId, position)

def callRaceMethod(raceId, methodName, *args):					##is there a way to put them in tokenBadges methods?
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def throwDice():
	if misc.TEST_MODE:
		dice = 0
	else:
		dice = random.randint(1, 6)
		if dice > 3:
			dice = 0
	return dice

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
