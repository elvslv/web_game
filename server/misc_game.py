import races
import misc
from misc import GAME_DEFEND, GAME_CONQUER, possiblePrevCmd, GAME_CHOOSE_FRIEND, ATTACK_ENCHANT
from editDb import query, queryt, fetchall, fetchone, lastId
from gameExceptions import BadFieldException
import random
import sys


def checkForFriends(userId, attackedUserId):
	query("""SELECT a.Priority, b.Priority FROM Users a, Users b WHERE 
		a.Id=%s AND b.Id=%s""", userId, attackedUserId)

	attackingPriority, attackedPriority = fetchone()

	if query("""SELECT 1 FROM History a, Games b WHERE a.GameId=b.GameId AND 
		a.Turn=b.Turn-%s AND a.State=%s AND a.UserId=%s AND a.Friend=%s""", 
		1 if attackingPriority < attackedPriority else 0, GAME_CHOOSE_FRIEND, 
		attackedUserId, userId):
			raise BadFieldException('UsersAreFriends')

def updateHistory(userId, gameId, state, tokenBadgeId, dice = None):
	query("""INSERT INTO History(UserId, GameId, State, TokenBadgeId, Turn, Dice) 
		SELECT %s, %s, %s, %s, Turn, %s FROM Games WHERE GameId=%s""", userId, 
		gameId, state, tokenBadgeId, dice, gameId)

def updateConquerHistory(historyId, attackingTokenBadgeId, counqueredRegion, 
	attackedTokenBadgeId, attackedTokensNum, dice, attackType):
	query("""INSERT INTO AttackingHistory(HistoryId, AttackingTokenBadgeId, 
		ConqueredRegion, AttackedTokenBadgeId, AttackedTokensNum, Dice, AttackType) 
		VALUES(%s, %s, %s, %s, %s, %s, %s)""", historyId, attackingTokenBadgeId, 
		counqueredRegion, attackedTokenBadgeId, attackedTokensNum, 
		dice if dice != -1 else None, attackType)

def checkStage(state, gameId):
	query("""SELECT State FROM History WHERE HistoryId=(SELECT MAX(HistoryId) 
		FROM History WHERE GameId=%s)""", gameId)
	row = fetchone()
	prevState = row[0]
	badStage = (not prevState in possiblePrevCmd[state])

	if prevState == GAME_CONQUER:
		query("""SELECT AttackType, AttackedTokensNum FROM AttackingHistory WHERE HistoryId=
			(SELECT MAX(HistoryId) FROM History WHERE GameId=%s)""", gameId)
		attackType, attackedTokensNum = fetchone()
		if state == GAME_DEFEND:
			if attackType == ATTACK_ENCHANT:
				badStage = True
		elif attackedTokensNum > 1:
			badStage = True
			
	if badStage: 
		raise BadFieldException('badStage')

def isRegionAdjacent(regionId, tokenBadgeId):
	query("""SELECT RegionId FROM CurrentRegionState WHERE TokenBadgeId=%s""", 
		tokenBadgeId)
	playerRegions = fetchall()
	playerBorderline = False	
	for plRegion in playerRegions:
		query("""SELECT COUNT(*) FROM AdjacentRegions a, Regions b,
			Regions c WHERE b.RegionId=a.FirstRegionId AND a.MapId=b.MapId AND
			a.MapId=c.MapId AND a.MapId=%s AND c.RegionId=a.SecondRegionId AND
			b.RegionId=%s AND c.RegionId=%s""", getMapIdByTokenBadge(tokenBadgeId), 
			plRegion[0], regionId)
		if fetchone():
			playerBorderline = True
			break

	return playerBorderline, playerRegions

def extractValues(tableName, selectFields, params):
	queryStr = 'SELECT '
	for field in selectFields:
		queryStr += field + (', ' if field != selectFields[len(selectFields) - 1] else ' ')
	queryStr += 'FROM %s WHERE' % tableName
	for i in range(len(params)):
		queryStr += (' %s=%%s' if i == 0 else ' AND %s=%%s') % selectFields[i]
	if not queryt(queryStr, tuple(params)):
		raise BadFieldException('bad%s' % selectFields[0])
	res = fetchone()
	return res if len(res) > 1 else res[0]

def checkIsUnique(tableName, tableField, param):
	queryStr = 'SELECT 1 FROM %s WHERE %s=%%s' % (tableName, tableField)
	if query(queryStr, param):
		raise BadFieldException('bad%s' % tableField)
	return param

def getTokenBadgeIdByRaceAndUser(raceId, userId):
	query('SELECT TokenBadgeId From TokenBadges WHERE RaceId=%s AND OwnerId=%s', 
		raceId, userId)
	row = fetchone()
	return int(row[0])
	
def getRaceAndPowerIdByTokenBadge(tokenBadge):
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE TokenBadgeId=%s', 
		tokenBadge)
	return fetchone()

def clearRegionFromRace(regionId, tokenBadgeId):
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callRaceMethod(raceId, 'clearRegion', tokenBadgeId, regionId)
	callSpecialPowerMethod(specialPowerId, 'clearRegion', tokenBadgeId, regionId)
	
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
	query("""SELECT AttackedTokenBadgeId, AttackType FROM AttackingHistory WHERE 
		HistoryId=(SELECT MAX(HistoryId) FROM History WHERE GameId=%s)""", gameId)
	row = fetchone()
	if not row:
		return
	if row[1] == ATTACK_ENCHANT:
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

def checkRegionIsImmune(regionId, gameId):
	query("""SELECT HoleInTheGround, Dragon, Hero FROM CurrentRegionState WHERE 
		RegionId=%s AND GameId=%s""", regionId, gameId)
	row = fetchone()
	if row[0] or row[1] or row[2]:
		raise BadFieldException('regionIsImmune')

def checkRegionIsCorrect(regionId, tokenBadgeId):
	if not query("""SELECT 1 FROM Users a, Games b, Regions c WHERE 
		a.CurrentTokenBadge=%s AND a.GameId=b.GameId AND b.MapId=c.MapId AND 
		c.RegionId=%s""", tokenBadgeId, regionId):
		return BadFieldException('badRegion')

def throwDice():
	if misc.TEST_MODE:
		dice = 0
	else:
		dice = random.randint(1, 6)
		if dice > 3:
			dice = 0
	return dice

def getRegionInfoById(regionId, gameId):
	return getRegionInfo(regionId, gameId)[4]

def getRegionInfo(regionId, gameId):
	if not query("""SELECT 1 FROM CurrentRegionState WHERE RegionId=%s AND 
		GameId=%s""", regionId, gameId):
		raise BadFieldException('badRegionId')
	query('SELECT MapId FROM Games WHERE GameId=%s', gameId)
	mapId = fetchone()[0]
	
	l = list()
	l.append('RegionId')
	l.append('MapId')
	l.extend(misc.possibleLandDescription[:11])
	regInfo = list(extractValues('Regions', l, [regionId, mapId])[2:])
	
	queryStr = 'SELECT OwnerId, TokenBadgeId, TokensNum, InDecline'
	for regParam in misc.possibleLandDescription[11:]:
		queryStr += ', %s' % regParam
	queryStr += ' FROM CurrentRegionState WHERE RegionId=%s AND GameId=%s'
	query(queryStr, regionId, gameId)
	
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

def getGameIdByTokenBadge(tokenBadgeId):
	query("""SELECT a.GameId FROM Users a, TokenBadges b WHERE a.Id=b.OwnerId 
		AND b.TokenBadgeId=%s""", tokenBadgeId)
	return fetchone()[0]

def getMapIdByTokenBadge(tokenBadgeId):
	query("""SELECT MapId FROM Games WHERE GameId=%s""", 
		getGameIdByTokenBadge(tokenBadgeId))
	return fetchone()[0]

if __name__=='__main__':
	print generateTokenBadges(int(sys.argv[1]), int(sys.argv[2]))
