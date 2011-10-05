from editDb import query, fetchall, fetchone
from gameExceptions import BadFieldException
from misc_game import *
from misc import *
from checkFields import *

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id

	def tryToConquerRegion(self, currentRegionId, tokenBadgeId):
		isAdjacent, regions = isRegionAdjacent(currentRegionId, tokenBadgeId)
		regionInfo = getRegionInfo(currentRegionId)[4]
		return (not regions and (regionInfo['coast'] or regionInfo['border'])) or regions
	
	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		return 0
	
	def decline(self, userId): 
		query("""DELETE FROM TokenBadges WHERE TokenBadgeId=(SELECT DeclinedTokenBadge 
			FROM Users WHERE Users.Id=%s)""", userId)
		query("""UPDATE CurrentRegionState SET OwnerId=NULL, InDecline=False, 
			TokenBadgeId=NULL WHERE OwnerId=%s AND InDecline=True""", userId)
		query("""UPDATE CurrentRegionState SET InDecline=True, TokensNum=1 WHERE 
			OwnerId=%s""", userId)
		query("""UPDATE TokenBadges SET InDecline=True, TotalTokensNum=(SELECT 
			COUNT(*) FROM CurrentRegionState WHERE OwnerId=%s) WHERE OwnerId=%s""", 
			userId, userId)
	
	def countAdditionalRedeploymentUnits(self, userId, gameId):
		return 0

	def countAdditionalConquerUnits(self, userId, gameId):
		return 0
	
	def countAdditionalCoins(self, userId, gameId):
		return 0

	def countAddDefendingTokensNum(self):
		return -1

	def countAdditionalConquerPrice(self):
		return 0

	def getInitBonusNum(self):
		return 0

	def declineRegion(self, currentRegionId):
		pass
	
	def updateBonusStateAtTheAndOfTurn(self, tokenBadgeId):
		pass

	def conquered(self, currentRegionId, tokenBadgeId):
		pass

	def enchant(self, tokenBadgeId, currentRegionId):
		return BadFieldException('badRace')

	def clearRegion(self, tokenBadgeId, currentRegionId):
		query("""UPDATE CurrentRegionState SET Encampment = 0, Fortress=FALSE, 
			Dragon=FALSE, HoleInTheGround=FALSE, Hero = FALSE 
			WHERE CurrentRegionId=%s""", currentRegionId) 

	def updateAttackedTokensNum(self, tokenBadgeId):
		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", tokenBadgeId)

class RaceHalflings(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Halflings', 6, 11)
	
	def conquered(self, currentRegionId, tokenBadgeId):
		query("""SELECT COUNT(*) FROM CurrentRegionState WHERE TokenBadgeId=%s AND 
			HoleInTheGround=TRUE""", tokenBadgeId)
		if fetchone()[0] == 2:
			return
		query("""UPDATE CurrentRegionState SET HoleInTheGround=TRUE WHERE 
			TokenBadgeId=%s""", tokenBadgeId)

	def tryToConquerRegion(self, currentRegionId, tokenBadgeId):
		return True

	
	def getInitBonusNum(self):
		return 2

	def decline(self, userId):
		BaseRace.decline(self, userId)
		query("""UPDATE CurrentRegionState SET HoleInTheGround=FALSE WHERE 
			OwnerId=%s""", userId)
		
	def declineRegion(self, currentRegionId):
		query("""UPDATE CurrentRegionState SET HoleInTheGround=FALSE WHERE 
			CurrentRegionId=%s""", currentRegionId)

class RaceGiants(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Giants', 6, 11)

	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		res = 0
		query("""SELECT Regions.RegionId, Regions.Mountain FROM CurrentRegionState, 
			Regions WHERE CurrentRegionState.TokenBadgeId=%s AND 
			CurrentRegionState.RegionId=Regions.RegionId""", tokenBadgeId)
		row = fetchall()
		for region in row:
			if query("""SELECT 1 FROM AdjacentRegions, CurrentRegionState 
				WHERE CurrentRegionState.RegionId=FirstRegionId AND
				CurrentRegionState.CurrentRegionId=%s AND 
				AdjacentRegions.SecondRegionId=%s""", currentRegionId, 
				region[0]) and region[1]:
					res = -1
					break
		return res

class RaceTritons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Tritons', 6, 11)

	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		regionInfo = getRegionInfoById(currentRegionId)
		return -1 if regionInfo['coast'] else 0

class RaceDwarves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Dwarves', 3, 8)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions, CurrentRegionState WHERE 
			CurrentRegionState.TokenBadgeId=%s AND 
			Regions.RegionId=CurrentRegionState.RegionId AND Regions.Mine=1""", 
			getTokenBadgeIdByRaceAndUser(self.raceId, userId))
		res = int(fetchone()[0])
		return res

class RaceHumans(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Humans', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM CurrentRegionState, Regions WHERE 
			CurrentRegionState.TokenBadgeId=%s AND 
			CurrentRegionState.RegionId=Regions.RegionId AND Regions.Farmland=1""", 
			getTokenBadgeIdByRaceAndUser(self.raceId, userId))
		return int(fetchone()[0])

class RaceOrcs(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Orcs', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		tokenBadgeId = getTokenBadgeIdByRaceAndUser(self.raceId, userId)
		query('SELECT InDecline FROM TokenBadges WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		if fetchone()[0]:
			return 0
		return getNonEmptyConqueredRegions(tokenBadgeId, gameId)

class RaceWizards(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Wizards', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM CurrentRegionState, Regions WHERE 
			CurrentRegionState.TokenBadgeId=%s AND 
			CurrentRegionState.RegionId=Regions.RegionId AND Regions.Magic=1""", 
			getTokenBadgeIdByRaceAndUser(self.raceId, userId))
		return int(fetchone()[0])
		
class RaceAmazons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Amazons', 6, 15)

	def countAdditionalRedeploymentUnits(self, userId, gameId):
		return -4 if  getPrevState(gameId) == GAME_CONQUER else 0

	def countAdditionalConquerUnits(self, userId, gameId):
		return 4 if getPrevState(gameId) in (GAME_FINISH_TURN, GAME_SELECT_RACE) else 0

class RaceSkeletons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Skeletons', 5, 18)

	def countAdditionalRedeploymentUnits(self, userId, gameId):
		return getNonEmptyConqueredRegions(tokenBadgeId, gameId) / 2
		
			
class RaceElves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Elves', 6, 11)

	def countAddDefendingTokensNum(self):
		return 0

	def updateAttackedTokensNum(self, tokenBadgeId):
		pass

class RaceRatmen(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Ratmen', 8, 13)

class RaceTrolls(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Trolls', 5, 10)

	def countAdditionalConquerPrice(self):
		return 1

class RaceSorcerers(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Sorcerers', 5, 18)

	def enchant(self, tokenBadgeId, currentRegionId):
		currentRegionId = extractValues('CurrentRegionState', 'CurrentRegionId', 
			currentRegionId, 'badRegionId', True)[0]
			
		checkRegionIsImmune(currentRegionId)
		checkRegionIsCorrect(currentRegionId, tokenBadgeId)

		if not(self.tryToConquerRegion(currentRegionId, tokenBadgeId) 
			and specialPowerList[getRaceAndPowerIdByTokenBadge(tokenBadgeId)[1]].tryToConquerRegion(currentRegionId, tokenBadgeId)):
			raise BadFieldException('badRegion')
		query("""SELECT TokenBadgeId, Encampment, TokensNum, InDecline FROM 
			CurrentRegionState WHERE CurrentRegionId=%s""", currentRegionId)
		row = fetchone()
		if row[0] == tokenBadgeId:
			raise BadFieldException('badAttackedRace')
		if row[1]:
			raise BadFieldException('regionIsImmune')
		if not row[2]:
			raise BadFieldException('nothingToEnchant')
		if row[2] > 1:
			raise BadFieldException('cannotEnchantMoreThanOneToken')
		if row[3]:
			raise BadFieldException('cannotEnchantDeclinedRace')

		query("""SELECT a.TotalTokensNum, a.OwnerId, b.GameId FROM TokenBadges a, 
			Users b WHERE a.TokenBadgeId=%s AND a.OwnerId=b.Id""", 
			tokenBadgeId)
		totalTokensNum, userId, gameId = fetchone()
		if totalTokensNum == self.maxNum:
			raise BadFieldException('noMoreTokensInStorageTray')

		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", row[0])
		raceId, specialPowerId  = getRaceAndPowerIdByTokenBadge(row[0])
		racesList[raceId].clearRegion(row[0], currentRegionId)
		specialPowerList[specialPowerId].clearRegion(row[0], currentRegionId)
		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum+1 WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		query("""UPDATE CurrentRegionState SET TokenBadgeId=%s, OwnerId=%s, 
			TokensNum=1 WHERE CurrentRegionId=%s""", tokenBadgeId, userId, 
			currentRegionId) 

		updateHistory(userId, gameId, GAME_CONQUER, tokenBadgeId)
		updateConquerHistory(lastId(), tokenBadgeId, currentRegionId, row[2], row[1], 
			-1, ATTACK_ENCHANT)


racesList = [
	RaceAmazons(),
	RaceDwarves(),
	RaceElves(),
#	RaceGhouls(),
	RaceGiants(),
	RaceHalflings(),
	RaceHumans(),
	RaceOrcs(),
	RaceRatmen(),
	RaceSkeletons(),
	RaceSorcerers(),
	RaceTritons(),
	RaceTrolls(),
	RaceWizards(),
]

for i in range(len(racesList)):
	racesList[i].setId(i)

class BaseSpecialPower:
	def __init__(self, name, tokensNum):
		self.name = name
		self.tokensNum = tokensNum

	def setId(self, id):
		self.specialPowerId = id

	def tryToConquerRegion(self, currentRegionId, tokenBadgeId):
		isAdjacent, regions = isRegionAdjacent(currentRegionId, tokenBadgeId)
		regionInfo = getRegionInfo(currentRegionId)[4]
		return (isAdjacent or not regions) and not regionInfo['sea']

	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		return 0

	def countAdditionalCoins(self, userId, gameId, raceId):
		return 0

	def tryToGoInDecline(self, gameId): ##rewrite in context of history
		if getPrevState(gameId) != GAME_FINISH_TURN:
			raise BadFieldException('badStage')

	def getInitBonusNum(self):
		return 0

	def updateBonusStateAtTheAndOfTurn(self, tokenBadgeId):
		pass

	def turnFinished(self, tokenBadgeId):
		pass

	def dragonAttack(self, tokenBadgeId, currentRegionId, tokensNum):
		raise BadFieldException('badAction') ###

	def clearRegion(self, tokenBadgeId, currentRegionId):
		pass

	def throwDice(self):
		raise BadFieldException('badAction')

	def declineRegion(self, currentRegionId):
		pass

	def decline(self, userId):
		pass

	def setEncampments(encampments, tokenBadgeId):
		raise BadFieldException('badSpecialPower')

	def setFortifield(fortifield, tokenBadgeId):
		raise BadFieldException('badSpecialPower')
	

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query('SELECT InDecline FROM TokenBadges WHERE TokenBadgeId=%s',
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return 2 if not int(fetchone()[0]) else 0

class SpecialPowerBerserk(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Berserk', 4)

	def throwDice(self):
		return throwDice()


class SpecialPowerBivouacking(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Bivouacking', 5)
	
	def getInitBonusNum(self):
		return 5

	def clearRegion(self, tokenBadgeId, currentRegionId):
		pass

	def decline(self, userId):
		query("""UPDATE CurrentRegionState SET Encampment=0 WHERE OwnerId=%s""",
			userId)

	def setEncampments(self, encampments, tokenBadgeId):
		checkObjectsListCorrection(encampments, 
			[{'name': 'regionId', 'type': int, 'min': 1}, 
			{'name': 'encampmentsNum', 'type': int, 'min': 0}])

		query('UPDATE CurrentRegionState SET Encampment=0 WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		freeEncampments = 5
		for encampment in encampments:
			currentRegionId = encampment['regionId']
			encampmentsNum = encampment['encampmentsNum']
			if not query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s 
				AND TokenBadgeId=%s""", currentRegionId, tokenBadgeId):
				raise BadFieldException('badRegion')
			if encampmentsNum > freeEncampments:
				raise BadFieldException('notEnoughEncampentsForRedeployment')
			query("""UPDATE CurrentRegionState SET Encampment=%s WHERE 
				CurrentRegionId=%s""", encampmentsNum, currentRegionId )

			freeEncampments -= encampmentsNum

class SpecialPowerCommando(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Commando', 4)

	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		return -1

class SpecialPowerDiplomat(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Diplomat', 5)
		
	def getInitBonusNum(self):
			return 1
			
	def decline(self, userId):
		pass

	def selectFriend(data, userId, tokenBadgeId, gameId):
		if not('friendId' in data and isinstance(data['friendId'], int)):
			raise BadFieldException('badFriendId')

		friendId, friendBadgeId = extractValues('Users', 'Id', data['friendId'], 'badUserId', 
			True, ['CurrentTokenBadge'])

		if friendId == userId:
			raise BadFieldException('badFriend')
			
		if not query("""SELECT 1 FROM Users a, Users b WHERE a.Id=%s AND b.Id=%s
			AND a.GameId=b.GameId"""):
			raise BadFieldException('badFriend')
			
		if query("""SELECT 1 FROM AttackingHistory a, History b, Games c, 
			TokenBadges d WHERE a.AttackingTokenBadgeId=%s AND 
			a.AttackedTokenBadgeId=%s AND a.HistoryId=b.HistoryId AND 
			b.GameId=c.GameId AND b.Turn=c.Turn	AND c.GameId=d.GameId AND 
			d.TokenBadgeId=%s AND d.InDecline=False""", tokenBadgeId, 
			friendBadgeId, friendBadgeId):
			raise BadFieldException('badFriend')

		query("""INSERT INTO History(UserId, GameId, State, TokenBadgeId, Turn, 
			Friend) SELECT %s, %s, %s, %s, Turn FROM Games WHERE GameId=%s""", 
			userId, gameId, GAME_CHOOSE_FRIEND, tokenBadgeId, gameId, friendId)


class SpecialPowerDragonMaster(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Dragon master', 5)
	
	def getInitBonusNum(self):
		return 1

	def dragonAttack(self, tokenBadgeId, currentRegionId, tokensNum):
		currentRegionId = extractValues('CurrentRegionState', 'CurrentRegionId', 
			currentRegionId, 'badRegionId')[0]
		checkRegionIsImmune(currentRegionId)
		checkRegionIsCorrect(currentRegionId, tokenBadgeId)
		raceId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)[0]
		
		if not(racesList[raceId].tryToConquerRegion(currentRegionId, tokenBadgeId) 
			and self.tryToConquerRegion(currentRegionId, tokenBadgeId)):
			raise BadFieldException('badRegion')
			
		if query("""SELECT 1 FROM History a, AttackingHistory b, TokenBadges c, 
			Users d, Games e WHERE b.AttackingTokenBadgeId=%s AND 
			c.TokenBadgeId=b.AttackingTokenBadgeId AND c.UserId=d.Id AND 
			d.GameId=a.GameId AND e.GameId = a.GameId AND a.Turn=e.Turn AND 
			a.HistoryId=b.HistoryId AND b.AttackType=%s""", tokenBadgeId, 
			ATTACK_DRAGON):
			raise BadFieldException('dragonAlreadyAttackedOnThisTurn')
			
		query("""SELECT a.TokenBadgeId, b.TokenBadgeId, a.TokensNum FROM 
			CurrentRegionState a, CurrentRegionState b WHERE a.CurrentRegionId=%s 
			AND b.TokenBadgeId=%s""", currentRegionId, tokenBadgeId)
		row = fetchone()
		if row[0] == row[1]:
			raise BadFieldException('badRegion')
		##check anything else?
		query('UPDATE CurrentRegionState SET Dragon=FALSE WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		query("""UPDATE CurrentRegionState SET TokenBadgeId=%s, Dragon=TRUE, 
			TokensNum=%s WHERE CurrentRegionId=%s""", tokenBadgeId, tokensNum, 
			currentRegionId)

		updateHistory(userId, gameId, GAME_CONQUER, tokenBadgeId)
		updateConquerHistory(lastId(), tokenBadgeId, regionId, row[0], row[2], 
			-1, ATTACK_DRAGON)

	def decline(self, userId):
 		query("""UPDATE CurrentRegionState SET Dragon=FALSE WHERE OwnerId=%s""", 
 			userId)

class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def tryToConquerRegion(self, currentRegionId, tokenBadgeId):
		isAdjacent, regions = isRegionAdjacent(currentRegionId, tokenBadgeId)
		regionInfo = getRegionInfo(currentRegionId)[4]
		return ((not isAdjacent and regions) or not regions) and not regionInfo['sea']


class SpecialPowerForest(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Forest', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query("""SELECT COUNT(*) FROM CurrentRegionState, Regions WHERE 
			CurrentRegionState.TokenBadgeId=%s AND Regions.Forest=1 AND 
			Regions.RegionId=CurrentRegionState.RegionId""", 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return int(fetchone()[0])

class SpecialPowerFortifield(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Fortifield', 3)
		self.maxNum = 6

	def getInitBonusNum(self):
		return 1

	def countAdditionalCoins(self, userId, gameId, raceId):
		query("""SELECT InDecline FROM TokenBadges WHERE OwnerId=%s AND 
			RaceId=%s""", userId, raceId)
		query("""SELECT COUNT(*) FROM CurrentRegionState, Regions WHERE 
			CurrentRegionState.TokenBadgeId=%s AND 
			CurrentRegionState.RegionId=Regions.RegionId AND 
			CurrentRegionState.Fortifield=TRUE""", 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return int(fetchone()[0])

	def clearRegion(self, tokenBadgeId, currentRegionId):
		query("""SELECT TotalSpecialPowerBonusNum FROM TokenBadges WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		query("""UPDATE TokenBadges SET TotalSpecialPowerBonusNum=GREATEST(%s-1,
			0) WHERE TokenBadgeId=%s""", fetchone()[0], tokenBadgeId)

	def setFortifield(fortifield, tokenBadgeId):
		if not('regionId' in fortifield and isinstance(fortifield['regionId'])):
			raise BadFieldException('badRegionId')

		currentRegionId, ownerBadgeId, hasFortifield = extractValues('CurrentRegionState', 
			'CurrentRegionId', fortifield['regionId'], 'badRegionId', True, 
			['TokenBadgeId', 'Fortifield'])

		if ownerBadgeId != tokenBadgeId:
			raise BadFieldException('badRegion')

		if hasFortifield:
			raise BadFieldException('tooManyFortifieldsInRegion')

		query("""SELECT COUNT(*) FROM CurrentRegionState WHERE Fortifield=True 
			AND TokenBadgeId=%s""", tokenBadgeId)
		fortifieldsOnMap = fetchone()[0]
		if fortifieldsOnMap >= self.maxNum:
			raise BadFieldException('tooManyFortifieldsOnMap')
		query("""SELECT TotalSpecialPowerBonusNum FROM TokenBadges WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		if fortifieldsOnMap == fetchone()[0]:
			raise BadFieldException('tooManyFortifields')
		query("""UPDATE CurrentRegionState SET Fortifield=True WHERE 
			CurrentRegionId=%s""", currentRegionId)
	

class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5)
		
	def getInitBonusNum(self):
		return 2

	def decline(self, userId):
 		query("""UPDATE CurrentRegionState SET Hero=FALSE WHERE OwnerId=%s""", 
 			userId)

 	def setHero(heroes, tokenBadgeId):
		checkObjectsListCorrection(heroes, 
			[{'name': 'regionId', 'type': int, 'min': 1}])

		if len(heroes) > 2:
			raise BadFieldException('badSetHeroCommand')

		query('UPDATE CurrentRegionState SET Hero=False WHERE TokenBadgeId=%s',
			tokenBadgeId)
		for hero in heroes:
			currentRegionId, ownerBadgeId = extractValues('CurrentRegionState', 
			'CurrentRegionId', heroe['regionId'], 'badRegionId', True, 
			['TokenBadgeId'])

			if ownerBadgeId != tokenBadgeId:
				raise BadFieldException('badRegion')

			query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s 
				AND TokenBadgeId=%s""", currentRegionId, tokenBadgeId)
			if not fetchone():
				raise BadFieldException('badRegion')

			query('UPDATE CurrentRegionState SET Hero=True WHERE TokenBadgeId=%s',
				tokenBadgeId)
		

class SpecialPowerHill(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Hill', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query("""SELECT COUNT(*) FROM Regions, CurrentRegionState WHERE 
			CurrentRegionState.TokeBadgeId=%s AND Regions.Hill=1 AND 
			Regions.RegionId=CurrentRegionState.RegionId""", 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return int(fetchone()[0])

class SpecialPowerMerchant(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Merchant', 2) 

	def countAdditionalCoins(self, userId, gameId, raceId):
		query('SELECT COUNT(*) FROM CurrentRegionState WHERE TokenBadgeId=%s', 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return int(fetchone()[0])

class SpecialPowerMounted(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Mounted', 5) 

	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		regionInfo = getRegionInfoById(currentRegionId)
		return -1 if regionInfo['farmland'] or regionInfo['hill'] else 0


class SpecialPowerPillaging(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Pillaging', 5)
	
	def countAdditionalCoins(self, userId, gameId, raceId): ###
		return getNonEmptyConqueredRegions(getTokenBadgeIdByRaceAndUser(raceId, 
			userId), gameId)

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 
	
	def tryToConquerRegion(self, currentRegionId, tokenBadgeId):
		isAdjacent, regions = isRegionAdjacent(currentRegionId, tokenBadgeId)
		return (isAdjacent and regions) or not regions 


class SpecialPowerStout(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Stout', 4) 

	def tryToGoInDecline(self, gameId):
		pass

class SpecialPowerSwamp(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Swamp', 4) 
	
	def countAdditionalCoins(self, userId, gameId, raceId): ###
		query("""SELECT COUNT(*) FROM Regions, CurrentRegionState WHERE 
			CurrentRegionState.TokenBadgeId=%s 
			CurrentRegionState.RegionId=Regions.RegionId AND Regions.Swamp=1""", 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return int(fetchone()[0]) 

class SpecialPowerUnderworld(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Underworld', 5) 

	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, tokenBadgeId):
		query("""SELECT a.Cavern, b.Cavern FROM Regions a, Regions b, 
			CurrentRegionState c, CurrentRegionState d WHERE c.CurrentRegionId=%s 
			AND d.TokenBadgeId=%s AND a.RegionId=c.RegionId AND b.RegionId=d.RegionId""", 
			attackedRegion, tokenBadgeId)
		cavern1, cavern2 = fetchone()
		return (cavern1 and cavern2)
		
	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		regionInfo = getRegionInfoById(currentRegionId)
		return -1 if regionInfo['cavern'] else 0

	
class SpecialPowerWealthy(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Wealthy', 4) 
	
	def getInitBonusNum(self):
		return 1

	def countAdditionalCoins(self, userId, gameId, raceId):
		query("""SELECT b.Turn-a.Turn FROM History a, Games b WHERE a.TokenBadgeId=%s 
			AND a.State=%s AND b.GameId=a.GameId""", 
			getTokenBadgeIdByRaceAndUser(raceId, userId), GAME_SELECT_RACE)
		return 0 if fetchone()[0] else 7

specialPowerList = [
	SpecialPowerAlchemist(),
	SpecialPowerBerserk(),
 	SpecialPowerBivouacking(),
	SpecialPowerCommando(),
	SpecialPowerDiplomat(),
	SpecialPowerDragonMaster(),
	SpecialPowerFlying(),
	SpecialPowerForest(),
	SpecialPowerFortifield(),
	SpecialPowerHeroic(),
	SpecialPowerHill(),
	SpecialPowerMerchant(),
	SpecialPowerMounted(),
	SpecialPowerPillaging(),
	SpecialPowerSeafaring(), 
#	SpecialPowerSpirit(),
	SpecialPowerStout(),
	SpecialPowerSwamp(),
	SpecialPowerUnderworld(),
	SpecialPowerWealthy()
]

for i in range(len(specialPowerList)):
	specialPowerList[i].setId(i)
