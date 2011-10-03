import races
import misc
from editDb import query, fetchall, fetchone, lastId
from gameExceptions import BadFieldException
import random
import sys

def extractValues(tableName, tableField, param, msg, pres, selectFields = ['1']):
	queryStr = 'SELECT '
	for field in selectFields:
		queryStr += field + (', ' if field != selectFields[len(selectFields) - 1] else ' ')
	queryStr += 'FROM %s WHERE %s=%%s' % (tableName, tableField)
	if query(queryStr, param) != pres:
		raise BadFieldException(msg)
	return [param, fetchone()]

def getTokenBadgeIdByRaceAndUser(raceId, userId):
	query('SELECT TokenBadgeId From TokenBadges WHERE RaceId=%s AND OwnerId=%s', 
		raceId, userId)
	row = fetchone()
	return int(row[0])
	
def getRaceAndPowerIdByTokenBadge(tokenBadge):
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE TokenBadgeId=%s', 
		tokenBadge)
	return fetchone()

def clearRegionFromRace(currentRegionId, tokenBadgeId):
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callRaceMethod(raceId, 'clearRegion', tokenBadgeId, currentRegionId)
	callSpecialPowerMethod(specialPowerId, 'clearRegion', tokenBadgeId, currentRegionId)
	
def getIdBySid(sid):
	if not query('SELECT Id, GameId FROM Users WHERE Sid=%s', sid):
		raise BadFieldException('badSid')
	return fetchone()

def getNextRaceAndPowerFromStack(gameId, vRace, vSpecialPower):
        if vRace != '' and vSpecialPower != '':
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
                query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE GameId=%s', gameId)
                row = fetchall()
                for rec in row:
                        racesInStack.remove(rec[0])
                        specialPowersInStack.remove(rec[1])
                raceId = random.choice(racesInStack)
                specialPowerId = random.choice(specialPowersInStack)
	return raceId, specialPowerId

def showNextRace(gameId, lastIndex, vRace = '', vSpecialPower = ''):
	raceId, specialPowerId = getNextRaceAndPowerFromStack(gameId, vRace, vSpecialPower)
	query("""UPDATE TokenBadges SET Position=Position+1 WHERE Position<%s 
		AND GameId=%s""", lastIndex, gameId)
	query("""INSERT INTO TokenBadges(RaceId, SpecialPowerId, GameId, Position, BonusMoney) 
		VALUES(%s, %s, %s, 0, 0)""", raceId, specialPowerId, gameId)
	return races.racesList[raceId].name, races.specialPowerList[specialPowerId].name, 
	
def updateRacesOnDesk(gameId, position):
	query('UPDATE TokenBadges SET Position=NULL WHERE GameId=%s AND Position=%s', gameId, position)
	query("""UPDATE TokenBadges SET BonusMoney=BonusMoney+1 WHERE Position>%s AND 
		GameId=%s""", position, gameId)
	return showNextRace(gameId, position)

def callRaceMethod(raceId, methodName, *args):
	race = races.racesList[raceId]
	return getattr(race, methodName)(*args)

def callSpecialPowerMethod(specialPowerId, methodName, *args):
	specialPower = races.specialPowerList[specialPowerId]
	return getattr(specialPower, methodName)(*args) ##join these 2 functions?

def checkDefendingPlayerNotExists(gameId):
	query("""SELECT AttackedTokenBadgeId FROM AttackingHistory WHERE 
		HistoryId=(SELECT MAX(HistoryId) FROM History WHERE GameId=%s)""", gameId)
	row = fetchone()
	if not row:
		return
	if row[0]:
		query('SELECT InDecline FROM TokenBadges WHERE TokenBadgeId=%s', row[0])
		if not fetchone()[0]:
			raise BadFieldException('badStage')

def getNonEmptyConqueredRegions(tokenBadgeId, gameId):
	query("""SELECT COUNT(*) FROM AttackingHistory a, History b, Games c WHERE 
		a.AttackingTokenBadgeId=%s AND a.AttackedTokensNum>0 AND a.HistoryId=b.HistoryId
		AND b.Turn=c.Turn AND b.GameId=c.GameId AND c.GameId=%s""", 
		tokenBadgeId, gameId)
	row = fetchone()
	return row[0] if row else 0

def checkForDefendingPlayer(gameId, tokenBadgeId):
	query("""SELECT ConqueredRegion, AttackedTokensNum FROM AttackingHistory 
		WHERE HistoryId=(SELECT MAX(HistoryId) FROM History WHERE GameId=%s) AND 
		AttackedTokenBadgeId=%s""", gameId, tokenBadgeId)
	row = fetchone()
	if not row:
		raise BadFieldException('badStage')
	return row

def getPrevState(gameId):
	query("""SELECT State FROM History WHERE HistoryId=(SELECT MAX(HistoryId) 
		FROM History WHERE GameId=%s)""", gameId)
	return fetchone()[0]

def checkActivePlayer(gameId, userId):
	if not query("""SELECT 1 FROM Games, Users WHERE Games.GameId=%s AND 
		Games.ActivePlayer=Users.Id AND Users.Id=%s""", gameId, userId):
		raise BadFieldException('badStage') ##better message?

def checkRegionIsImmune(currentRegionId):
	query("""SELECT HoleInTheGround, Dragon, Hero FROM CurrentRegionState WHERE 
		CurrentRegionId=%s""", currentRegionId)
	row = fetchone()
	if row[0] or row[1] or row[2]:
		raise BadFieldException('regionIsImmune')

def checkRegionIsCorrect(currentRegionId, tokenBadgeId):
	if not query("""SELECT 1 FROM Users, Games, Regions, CurrentRegionState 
		WHERE Users.TokenBadgeId=%s AND Users.GameId=Games.GameId AND 
		Games.MapId=Regions.MapId AND Regions.RegionId=CurrentRegionState.RegionId 
		AND CurrentRegionState.CurrentRegionId=%s""", tokenBadgeId, currentRegionState):
		return BadFieldException('badRegion')

def throwDice():
	if misc.TEST_MODE:
		dice = 0
	else:
		dice = random.randint(1, 6)
		if dice > 3:
			dice = 0
	return dice

def getRegionInfoById(currentRegionId):
	queryStr = 'SELECT '
	for regParam in misc.possibleLandDescription:
		queryStr += (', %s' if regParam != misc.possibleLandDescription else '%s') % regParam

	queryStr += ' FROM CurrentRegionState WHERE CurrentRegionId=%%s'
	query(queryStr, currentRegionId)
	return fetchone()

def getRegionInfo(currentRegionId):
	if not query("""SELECT RegionId FROM CurrentRegionState WHERE CurrentRegionId=%s""",
		currentRegionId):
		raise BadFieldException('badRegionId')
	regInfo = list(extractValues('Regions', 'RegionId', fetchone()[0], 'badRegionId', 
		True, misc.possibleLandDescription[:11])[1])

	queryStr = 'SELECT OwnerId, TokenBadgeId, TokensNum, InDecline'
	for regParam in misc.possibleLandDescription[11:]:
		queryStr += ', %s' % regParam
	queryStr += ' FROM CurrentRegionState WHERE currentRegionId=%s'
	query(queryStr, currentRegionId)
	row = list(fetchone())
	ownerId, tokenBadgeId, tokensNum, inDecline = row[:4]
	regInfo[len(regInfo):] = row[4:]
	result = dict()
	for i in range(len(misc.possibleLandDescription)):
		result[misc.possibleLandDescription[i]] = regInfo[i]

	return ownerId, tokenBadgeId, tokensNum, inDecline, result

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
