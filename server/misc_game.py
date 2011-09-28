import races
import misc
from editDb import query, fetchall, fetchone, lastId
from gameExceptions import BadFieldException

def getTokenBadgeIdByRaceAndUser(raceId, userId):
	query('SELECT TokenBadgeId From TokenBadges WHERE RaceId=%s AND OwnerId=%s', 
		raceId, userId)
	return fetchone()[0]
	
def getRaceAndPowerIdByTokenBadge(tokenBadge):
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE TokenBadgeId=%s', 
		tokenBadge)
	return fetchone()

def clearRegionFromRace(regionId, tokenBadgeId):
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'clearRegion', tokenBadgeId, regionId)
	query("""UPDATE Regions SET Encampment = 0, Fortress=FALSE, Dragon=FALSE, 
	HoleInTheGround=FALSE, Hero = FALSE WHERE RegionId=%s""", 
		regionId)

def getIdBySid(sid):
	if not query('SELECT Id, GameId FROM Users WHERE Sid=%s', sid):
		raise BadFieldException('badSid')
	return fetchone()

def getNextRaceAndPowerFromStack(gameId):
	racesInStack = range(0, misc.RACE_NUM)
	specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE GameId=%s', gameId)
	row = fetchall()
	for rec in row:
		racesInStack.remove(rec[0])
		specialPowersInStack.remove(rec[1])
	raceId = racesInStack[0]#random.choice(racesInStack)
	specialPowerId = specialPowersInStack[0]#random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(gameId, lastIndex):
	raceId, specialPowerId = getNextRaceAndPowerFromStack(gameId)
	query("""UPDATE TokenBadges SET Position=Position+1 WHERE Position<%s 
		AND GameId=%s""", lastIndex, gameId)
	query("""INSERT INTO TokenBadges(RaceId, SpecialPowerId, GameId, Position, BonusMoney) 
		VALUES(%s, %s, %s, 0, 0)""", raceId, specialPowerId, gameId)
	
def updateRacesOnDesk(gameId, position):
	query('UPDATE TokenBadges SET Position=NULL WHERE GameId=%s AND Position=%s', gameId, position)
	query("""UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE Position>%s AND 
		GameId=%s""", position, gameId)
	showNextRace(gameId, position)

def getNextRaceAndPowerFromStack(gameId):
	racesInStack = range(0, misc.RACE_NUM)
	specialPowersInStack = range(0, misc.SPECIAL_POWER_NUM)
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE GameId=%s', gameId)
	row = fetchall()
	for rec in row:
		racesInStack.remove(rec[0])
		specialPowersInStack.remove(rec[1])
	raceId = racesInStack[0]#random.choice(racesInStack)
	specialPowerId = specialPowersInStack[0]#random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(gameId, lastIndex):
	raceId, specialPowerId = getNextRaceAndPowerFromStack(gameId)
	query("""UPDATE TokenBadges SET Position=Position+1 WHERE Position<%s 
		AND GameId=%s""", lastIndex, gameId)
	query("""INSERT INTO TokenBadges(RaceId, SpecialPowerId, GameId, Position, BonusMoney) 
		VALUES(%s, %s, %s, 0, 0)""", raceId, specialPowerId, gameId)
	
def updateRacesOnDesk(gameId, position):
	query('UPDATE TokenBadges SET Position=NULL WHERE GameId=%s AND Position=%s', gameId, position)
	query("""UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE Position>%s AND 
		GameId=%s""", position, gameId)
	showNextRace(gameId, position)

def callRaceMethod(raceId, methodName, *args):
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
	if not specialPowerId:
		return
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def checkForDefendingPlayer(gameId):
	query('SELECT DefendingPlayer FROM Games WHERE GameId=%s', gameId)
	if fetchone()[0]:
		raise BadFieldException('badStage') ##better message?

def checkActivePlayer(gameId, userId):
	if not query("""SELECT 1 FROM Games, Users WHERE Games.GameId=%s AND 
		Games.ActivePlayer=Users.Id AND Users.Id=%s""", gameId, userId):
		raise BadFieldException('badStage') ##better message?

def checkRegionIsImmune(regionId):
	query('SELECT HoleInTheGround, Dragon, Hero FROM Regions WHERE RegionId=%s', regionId)
	row = fetchone()
	if row[0] or row[1] or row[2]:
		raise BadFieldException('regionIsImmune')

def checkRegionIsCorrect(regionId, tokenBadgeId):
	if not query("""SELECT 1 FROM Users, Games, Regions WHERE Users.TokenBadgeId=%s 
		AND Users.GameId=Games.GameId AND Games.MapId=Regions.MapId AND 
		Regions.RegionId=%s""", tokenBadgeId, regionId):
		return BadFieldException('badRegion')