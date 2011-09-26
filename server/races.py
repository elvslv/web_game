from editDb import query, fetchall
from gameExceptions import BadFieldException

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id

	def tryToAttackByRaceInDecline():
		raise BadFieldException('badAttackingRace')
	
	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		return not regions and (border or coast)
	
	def countConquerBonus(self, userId, regionId, regionInfo, race):
		return 0
	
	def setRegionsInDecline(self, userId):
		query('UPDATE Regions SET InDecline=1, TokensNum=1 WHERE OwnerId=%s', userId)

	def tryToRedeployDeclinedRace(self):
		raise BadFieldException('badRace') 
	
	def countAdditionalRedeploymentUnits(self, userId, gameId):
		pass
	
	def countAdditionalCoins(self, userId, gameId):
		return 0

	def updateAttackedTokensNum(self, tokensBadgeId):
		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", tokensBadgeId)
		return -1

	def countAdditionalConquerPrice(self):
		return 0

	def tryToConquerAdjacentRegion(self, regions, border, coast):
		return True	
	
class RaceHalflings(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Halflings', 6, 11)
	
	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		if regions:
			return False

class RaceGhouls(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Ghouls', 5, 10)

	def tryToAttackByRaceInDecline():
		pass

	def setRegionsInDecline(self, userId):
		query('UPDATE Regions SET InDecline=1 WHERE OwnerId=%s', userId)

	def tryToRedeployDeclinedRace(self):
		pass

	def tryToFinishTurnOfDeclinedRace(self):
		pass

class RaceGiants(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Giants', 6, 11)

	def countConquerBonus(self, userId, regionId, regionInfo, race):
		res = 0
		query('SELECT RegionId, Mountain FROM Regions WHERE OwnerId=%s AND RaceId=%s', 
			userId, race)
		row = fetchall()
		for region in row:
			if query("""SELECT 1 FROM AdjacentRegions WHERE FirstRegionId=%s AND 
				SeconRegionId=%s""", regionId, row[0]) and row[1]:
					res = -1
					break
		return res

class RaceTritons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Tritons', 6, 11)

	def countConquerBonus(self, userId, regionId, regionInfo, race):
		return -1 if regionInfo[1] else 0

class RaceDwarves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Dwarves', 3, 8)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Mine=1""", 
			userId, self.raceId)
		return fetchone()[0]

class RaceHumans(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Humans', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Farmland=1""", 
			userId, self.raceId)
		return fetchone()[0]

class RaceOrcs(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Orcs', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		query('SELECT InDecline FROM TokenBadges WHERE OwnerId=%s AND RaceId=%s', userId, 
			self.raceId)
		if fetchone()[0]:
			return 0
		query('SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s', gameId)
		return fetchone()[0]

class RaceWizards(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Wizards', 5, 10)

	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Magic=1""", 
			userId, self.raceId)
		return fetchone()[0]
		
class RaceAmazons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Amazons', 6, 15)

	def countAdditionalRedeploymentUnits(self, userId, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		if prevState == misc.gameStates['finishTurn']:
			query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum+4 WHERE 
				OwnerId=%s AND RaceId=%s""", self.raceId)
		elif prevState == misc.gameStates['conquer']:
			query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-4 WHERE 
				OwnerId=%s AND RaceId=%s""", self.raceId)
		else:
			raise BadFieldException('badStage')

class RaceSkeletons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Skeletons', 5, 18)

	def countAdditionalRedeploymentUnits(self, userId, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		if prevState == misc.gameStates['finishTurn']:
			pass
		elif prevState == misc.gameStates['conquer']:
			query("""SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s""", 
				gameId)
			regionsNum = fetchone()[0]
			query("""UPDATE TokenBadges SET TotalTokensNum=LEAST(TotalTokensNum+%s, %s) 
				WHERE OwnerId=%s AND RaceId=%s""", regionsNum, self.maxNum, userId, 
				self.raceId)
		else:
			raise BadFieldException('badStage')

class RaceElves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Elves', 6, 11)

	def updateAttackedTokensNum(self):
		return 0

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

racesList = [
	RaceAmazons(),
	RaceDwarves(),
	RaceElves(),
	RaceGhouls(),
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

	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		return not regions and (border or coast)

	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return not sea	
	
	def countConquerBonus(self, userId, regionId, regionInfo, race):
		return 0

	def countAdditionalCoins(self, userId, gameId, raceId):
		return 0

	def tryToGoInDecline(self, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		if fetchone()[0] != misc.gameStates['finishTurn']:
			raise BadFieldException('badStage')

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		return 2

class SpecialPowerBerserk(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Berserk', 4)

class SpecialPowerBivouacking(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Bivouacking', 5)

class SpecialPowerCommando(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Commando', 4)

	def countConquerBonus(self, userId, regionId, regionInfo, race):
		return -1

class SpecialPowerDiplomat(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Diplomat', 5)

class SpecialPowerDragonMaster(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Dragon master', 5)

class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		return True

	def tryToConquerAdjacentRegion(self, regions, border, coast):
		return False

class SpecialPowerForest(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Forest', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Forest=1', 
			userId, raceId)
		return fetchone()[0]

class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5)

class SpecialPowerHill(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Hill', 4)

	def countAdditionalCoins(self, userId, gameId, raceId):
		query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Hill=1', 
			userId, raceId)
		return fetchone()[0]

class SpecialPowerMerchant(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Merchant', 2) 

	def countAdditionalCoins(self, userId, gameId, raceId): ###
		query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s', 
			userId, raceId)
		return fetchone()[0]

class SpecialPowerMounted(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Mounted', 5) 

	def countConquerBonus(self, userId, regionId, regionInfo, race):
		return -1 if regionInfo[8] or regionInfo[11] else 0


class SpecialPowerPillaging(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Pillaging', 5)
	
	def countAdditionalCoins(self, userId, gameId, raceId): ###
		query('SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s', 
			gameId)
		return fetchone()[0] 

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 
	
	def tryToConquerAdjacentRegion(self, regions, border, coast, sea):
		return True	

class SpecialPowerSpirit(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Spirit', 5) 

class SpecialPowerStout(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Stout', 4) 

	def tryToGoInDecline(self, gameId):
		pass

class SpecialPowerSwamp(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Swamp', 4) 
	
	def countAdditionalCoins(self, userId, gameId, raceId): ###
		query('SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=%s AND Swamp=1', 
			userId, raceId)
		return fetchone()[0] 

class SpecialPowerUnderworld(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Underworld', 5) 

	def tryToConquerNotAdjacentRegion(self, regions, border, coast, attackedRegion, attackingRegion):
		query("""SELECT a.Cavern, b.Cavern FROM Regions a, Regions b WHERE a.RegionId=%s 
			AND b.RegionId=%s""", attackedRegion, attackingRegion)
		cavern1, cavern2 = fetchone()
		if not (cavern1 and cavern2):
			return False
		
	def countConquerBonus(self, userId, regionId, regionInfo, race):
		if regionInfo[13]: ##cavern
			return -1
	
class SpecialPowerWealthy(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Wealthy', 4) 

specialPowerList = [
	SpecialPowerAlchemist(),
	SpecialPowerBerserk(),
 	SpecialPowerBivouacking(),
	SpecialPowerCommando(),
	SpecialPowerDiplomat(),
	SpecialPowerDragonMaster(),
	SpecialPowerFlying(),
	SpecialPowerForest(),
	SpecialPowerHeroic(),
	SpecialPowerHill(),
	SpecialPowerMerchant(),
	SpecialPowerMounted(),
	SpecialPowerPillaging(),
	SpecialPowerSeafaring(), 
	SpecialPowerSpirit(),
	SpecialPowerStout(),
	SpecialPowerSwamp(),
	SpecialPowerUnderworld(),
	SpecialPowerWealthy()
]

for i in range(len(specialPowerList)):
	specialPowerList[i].setId(i)