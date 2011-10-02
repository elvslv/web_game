from editDb import query, fetchall, fetchone
from gameExceptions import BadFieldException
from misc_game import getTokenBadgeIdByRaceAndUser, getRegionInfoById
from misc import *

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id
	
	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, 
		tokenBadgeId):
		return not regions and (border or coast)
	
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

	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return True	

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
		query('SELECT RaceBonusNum FROM TokenBadges WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		if not fetchone()[0]:
			return
		query("""UPDATE CurrentRegionState SET HoleInTheGround=TRUE WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		query("""UPDATE TokenBadges SET RaceBonusNum=RaceBonusNum-1 WHERE 
			TokenBadgeId=%s""", tokenBadgeId)

	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, 
		tokenBadgeId):
		return False if regions else True

	
	def getInitBonusNum(self):
		return 2

	def decline(self, userId):
		BaseRace.decline(self, userId)
		query("""UPDATE CurrentRegionState SET HoleInTheGround=FALSE WHERE 
			OwnerId=%s""", userId)
		query("""UPDATE TokenBadges SET RaceBonusNum=0 WHERE OwnerId=%s""", 
			userId)
		
	def declineRegion(self, currentRegionId):
		query("""UPDATE CurrentRegionState SET HoleInTheGround=FALSE WHERE 
			CurrentRegionId=%s""", currentRegionId)
		query("""UPDATE TokenBadges SET RaceBonusNum=0 WHERE TokenBadgeId=%s""",
			tokenBadgeId)

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
		return int(fetchone()[0])

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
		query('SELECT InDecline FROM TokenBadges WHERE TokenBadgeId=%s', 
			getTokenBadgeIdByRaceAndUser(self.raceId, userId))
		if fetchone()[0]:
			return 0
		query('SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s', gameId)
		res = fetchone()
		if res:
			return res[0]
		else:
			0

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
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		return -4 if  prevState == GAME_CONQUER else 0

	def countAdditionalConquerUnits(self, userId, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		return 4 if prevSTate in (GAME_FINISH_TURN, GAME_SELECT_RACE) else 0

class RaceSkeletons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Skeletons', 5, 18)

	def countAdditionalRedeploymentUnits(self, userId, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		if prevState == GAME_CONQUER:
			query("""SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s""", 
				gameId)
			regionsNum = int(fetchone()[0])
			return regionsNum / 2
		else:
			return 0
			
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

	def updateBonusStateAtTheAndOfTurn(self, tokenBadgeId):
		query('UPDATE TokenBadges SET RaceBonusNum=1 WHERE TokenBadgeId=%s', 
			tokenBadgeId)
	
	def enchant(self, tokenBadgeId, currentRegionId):
		checkRegionIsImmune(currentRegionId)
		checkRegionIsCorrect(currentRegionId, tokenBadgeId)
		query("""SELECT Encampment, TokensNum, TokenBadgeId, InDecline FROM CurrentRegion 
			WHERE CurrentRegionId=%s""", currentRegionId)
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

		query('SELECT TotalTokensNum FROM TokenBadges WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		if fetchone()[0] == self.maxNum:
			raise BadFieldException('noMoreTokensInStorageTray')

		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", row[0])
		
		raceId, specialPowerId  = getRaceAndPowerIdByTokenBadge(row[0])
		racesList[raceId].clearRegion(row[0], currentRegionId)
		specialPowerList[specialPowerId].clearRegion(row[0], currentRegionId)
		query("""UPDATE CurrentRegionState SET TokenBadgeId=%s 
			WHERE CurrentRegionId=%s""", tokenBadgeId, currentRegionId) 

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

	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, tokenBadgeId):
		return not regions and (border or coast)

	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return not sea	
	
	def countConquerBonus(self, currentRegionId, tokenBadgeId):
		return 0

	def countAdditionalCoins(self, userId, gameId, raceId):
		return 0

	def tryToGoInDecline(self, gameId): ##rewrite in context of history
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		if fetchone()[0] != GAME_FINISH_TURN:
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

	def setEncampment(self, tokenBadgeId, currentRegionId, encampmentsNum):
		raise BadFieldException('badAction')

	def breakEncampment(self, tokenBadgeId, currentRegionId, encampmentsNum):
		raise BadFieldException('badAction')

	def throwDice(self):
		raise BadFieldException('badAction')

	def thrownDice(self):
		raise BadFieldException('badSpecialPower')

	def declineRegion(self, currentRegionId):
		pass

	def decline(self, userId):
		pass

	def setEncampments(encampments, tokenBadgeId):
		raise BadFieldException('badSpecialPower')

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query('SELECT InDecline FROM TokenBadges WHERE TokenBadgeId=%s',
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		if not fetchone()[0]:
			return 2
		else:
			return 0

class SpecialPowerBerserk(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Berserk', 4)

	def throwDice(self):
		return throwDice()

	def thrownDice(self):
		pass
		

class SpecialPowerBivouacking(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Bivouacking', 5)
	
	def getInitBonusNum(self):
		return 5

	def clearRegion(self, tokenBadgeId, currentRegionId):
		query('SELECT OwnerId FROM TokenBadges WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		userId = fetchone()[0]
		query('SELECT Encampment FROM CurrentRegionState WHERE CurrentRegionId=%s', 
			currentRegionId)
		encampment = fetchone()[0]
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=LEAST(%s, 
			SpecialPowerBonusNum+%s) WHERE TokenBadgeId=%s""", 
			self.getInitBonusNum(), encampment, tokenBadgeId)
		
	def setEncampment(self, tokenBadgeId, currentRegionId, encampmentsNum):
		if not query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s AND 
			TokenBadgeId=%s""", currentRegionId, tokenBadgeId):
			raise BadFieldException('badRegion')
		query("""SELECT SpecialPowerBonusNum FROM TokenBadges WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		if fetchone()[0] < encampmentsNum:
			raise BadFieldException('notEnoughEncampments')

		query("""UPDATE CurrentRegionState SET Encampment=Encampment+%s WHERE 
			CurrentRegionId=%s""", encampmentsNum, currentRegionId)
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=SpecialPowerBonusNum-%s 
			WHERE TokenBadgeId=%s""", encampmentsNum, tokenBadgeId)

	def breakEncampment(self, tokenBadgeId, currentRegionId, encampmentsNum):
		if not query("""SELECT Encampments FROM CurrentRegionState WHERE 
			CurrentRegionId=%s AND TokenBadgeId=%s""", currentRegionId, tokenBadgeId):
			raise BadFieldException('badRegion')
		if fetchone()[0] < encampmentsNum:
			raise BadFieldException('tooManyEncampmentsToBreak')
		query("""UPDATE CurrentRegionState SET Encampment=Encampment-%s WHERE 
			CurrentRegionId=%s""", encampmentsNum, currentRegionId)
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=SpecialPowerBonusNum+%s 
			WHERE TokenBadgeId=%s""", encampmentsNum, tokenBadgeId)

	def decline(self, userId):
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=0, 
			TotalSpecialPowerBonusNum=0 WHERE OwnerId=%s""", userId)

	def setEncampments(encampments, tokenBadgeId):
		checkObjectsListCorrection(encampments, 
			[{'name': 'regionId', 'type': int, 'min': 1}, 
			{'name': 'encampmentsNum', 'type': int, 'min': 0}])

		query('UPDATE CurrentRegionState SET Encampment=0 WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		freeEncampments = 5
		for encampment in ecampments:
			currentRegionId = region['regionId']
			encampmentsNum = region['encampmentsNum']
			if not query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s 
				AND TokenBadgeId=%s""", currentRegionId, tokenBadgeId):
				raise BadFieldException('badRegion')
			if encampmentsNum > freeEncampments:
				raise BadFieldException('notEnoughEncampentsForRedeployment')
			query("""UPDATE CurrentRegionState SET Encampment=%s WHERE 
				CurrentRegionId=%s""", encampmentsNum, currentRegionId )

			freeEncampments -= encampmentsNum

		query('UPDATE Users SET SpecialPowerBonusNum=%s WHERE TokenBadgeId=%s',
			freeEncampments, tokenBadgeId)

				
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
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=0, 
			TotalSpecialPowerBonusNum=0 WHERE OwnerId=%s""", userId)
	

class SpecialPowerDragonMaster(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Dragon master', 5)
	
	def getInitBonusNum(self):
		return 1

	def updateBonusStateAtTheAndOfTurn(self, tokenBadgeId):
		query('UPDATE TokenBadges SET SpecialPowerBonusNum=%s WHERE TokenBadgeId=%s', 
			self.getInitBonusNum(), tokenBadgeId)

	def dragonAttack(self, tokenBadgeId, currentRegionId, tokensNum):
		checkRegionIsImmune(currentRegionId)
		checkRegionIsCorrect(currentRegionId, tokenBadgeId)

		query("""SELECT Games.PrevState FROM Games, Users WHERE 
			Users.TokenBadgeId=%s AND Users.GameId=Games.GameId""", tokenBadgeId)
		prevState = fetchone()[0]
		if prevState in (GAME_FINISH_TURN, GAME_DECLINE): ###fix it!!!
			raise('badStage')
		query('SELECT SpecialPowerBonusNum FROM TokenBadges WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		if not fetchone()[0]:
			raise BadFieldException('dragonAlreadyAttackedOnThisTurn')
		query("""SELECT a.OwnerId, b.OwnerId FROM CurrentRegionState a, 
			CurrentRegionState b WHERE a.CurrentRegionId=%s AND b.TokenBadgeId=%s""", 
			currentRegionId, tokenBadgeId)
		row = fetchone()
		if row[0] == row[1]:
			raise BadFieldException('badRegion')
		##check anything else?
		query('UPDATE CurrentRegionState SET Dragon=FALSE WHERE TokenBadgeId=%s', 
			tokenBadgeId)
		query("""UPDATE CurrentRegionState SET TokenBadgeId=%s, Dragon=TRUE, 
			TokensNum=%s WHERE CurrentRegionId=%s""", tokenBadgeId, tokensNum, 
			currentRegionId)

	def decline(self, userId):
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=0, 
			TotalSpecialPowerBonusNum=0 WHERE OwnerId=%s""", userId)
 		query("""UPDATE CurrentRegionState SET Dragon=FALSE WHERE OwnerId=%s""", 
 			userId)

class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, tokenBadgeId):
		return True

	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return False

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

	def updateBonusStateAtTheAndOfTurn(self, tokenBadgeId):
		query("""SELECT COUNT(*) FROM CurrentRegionState WHERE Fortifield=TRUE AND 
			TokenBadgeId=%s""", tokenBadgeId)
		curBonusNum = fetchone()[0]
		query("""SELECT TotalSpecialPowerBonusNum FROM TokenBadges WHERE 
			TokenBadgeId=%s""", tokenBadgeId)
		if curBonusNum < fetchone()[0]:
			query('UPDATE TokenBadges SET SpecialPowerBonusNum=%s WHERE TokenBadgeId=%s', 
				self.getInitBonusNum(), tokenBadgeId)

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
                query("""Select TotalSpecialPowerBonusNum FROM TokenBadges WHERE TokenBadgeId=%s""", 
			tokenBadgeId)
                TotalSpecialPowerBonusNum = fetchone()[0]
                m = max(TotalSpecialPowerBonusNum-1, 0)
		query("""UPDATE TokenBadges SET TotalSpecialPowerBonusNum=%s
			WHERE TokenBadgeId=%s""", m, tokenBadgeId)


class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5)
		
	def getInitBonusNum(self):
		return 2

	def decline(self, userId):
		query("""UPDATE TokenBadges SET SpecialPowerBonusNum=0, 
			TotalSpecialPowerBonusNum=0 WHERE OwnerId=%s""", userId)
 		query("""UPDATE CurrentRegionState SET Hero=FALSE WHERE OwnerId=%s""", 
 			userId)

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
		query('SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s', 
			gameId)
		return int(fetchone()[0]) 

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 
	
	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return True	

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
		query('SELECT SpecialPowerBonusNum FROM TokenBadges WHERE TokenBadgeId=%s', 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		if not fetchone()[0]:
			return 0
		query('UPDATE TokenBadges SET SpecialPowerBonusNum=0 WHERE TokenBadgeId=%s', 
			getTokenBadgeIdByRaceAndUser(raceId, userId))
		return 7

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
