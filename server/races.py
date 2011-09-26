from editDb import query
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
		if not(border or coast):
			raise BadFieldException('badRegion')
	
	def countAdditionalConquerPrice(self, userId, regionId, regionInfo, race):
		return 0
	
	def setRegionsInDecline(self, userId):
		query('UPDATE Regions SET InDecline=1, TokensNum=1 WHERE OwnerId=%s', userId)

	def tryToRedeployDeclinedRace(self):
		raise BadFieldException('badRace') 
	
	def countAdditionalRedeploymentUnits(self, userId, gameId):
		pass
	
	def countAdditionalCoins(self, userId, gameId):
		return 0

	def countAdditionalDefendingTokens(self, tokensBadgeId):
		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", tokensBadgeId)
		return 0
	
class RaceHalflings(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Halflings', 6, 11)
	
	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		if regions:
			raise BadFieldException('badRegion')

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

	def countAdditionalConquerPrice(self, userId, regionId, regionInfo, race):
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

	def countAdditionalConquerPrice(self, userId, regionId, regionInfo, race):
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

	def countAdditionalDefendingTokens(self):
		return 1

class RaceRatmen(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Ratmen', 8, 13)

class RaceTrolls(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Trolls', 5, 10)

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
