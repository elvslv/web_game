from editDb import query

class BaseRace:
	@staticmethod
	def tryToAttackByDeclinedRace():
		raise BadFieldException('badAttackinRace')
	
	@staticmethod
	def tryToConquerNotAdjacentRegion(self, regions, border, coast):
		if not(border or coast):
			raise BadFieldException('badRegion')
	
	@staticmethod
	def countAdditionalConquerPrice(self, userId, regionId):
		return 0
	
	@staticmethod
	def setRegionsInDecline(self, userId):
		query('UPDATE Regions SET InDecline=1, TokensNum=1 WHERE OwnerId=%s', userId)

	@staticmethod
	def tryToRedeploymentDeclinedRace(self):
		raise BadFieldException('badRace') 
	
	@staticmethod
	def countAdditionalRedeploymentUnits(self, userId, gameId):
		pass
	
	@staticmethod
	def countAdditionalCoins(self, userId, gameId):
		return 0
	
	@staticmethod
	def countAdditionalDefendingTokens(self, tokensBadgeId):
		query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-1 WHERE 
			TokenBadgeId=%s""", tokensBadgeId)
		return 0
	
class RaceHalflings(BaseRace):
	def tryToConquerNotAdjacentRegion(self, border, coast):
		if regions:
			raise BadFieldException('badRegion')

class RaceGhouls(BaseRace):
	def tryToAttackByDeclinedRace():
		pass

	def setRegionsInDecline(self, userId):
		query('UPDATE Regions SET InDecline=1 WHERE OwnerId=%s', userId)

	def tryToRedeploymentDeclinedRace(self):
		pass

	def tryToFinishTurnOfDeclinedRace(self):
		pass

class RaceGiants(BaseRace):
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
	def countAdditionalConquerPrice(self, userId, regionId, regionInfo, race):
		return -1 if regionInfo[1] else 0

class RaceDwarves(BaseRace):
	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=1 AND Mine=1""", 
			userId)
		return fetchone()[0]

class RaceHumans(BaseRace):
	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=6 AND Farmland=1""", 
			userId)
		return fetchone()[0]

class RaceOrcs(BaseRace):
	def countAdditionalCoins(self, userId, gameId):
		query('SELECT InDecline FROM TokenBadges WHERE OwnerId=%s AND RaceId=7', userId)
		if fetchone()[0]:
			return 0
		query('SELECT NonEmptyCounqueredRegionsNum FROM Games WHERE GameId=%s', gameId)
		return fetchone()[0]

class RaceWizards(BaseRace):
	def countAdditionalCoins(self, userId, gameId):
		query("""SELECT COUNT(*) FROM Regions WHERE OwnerId=%s AND RaceId=13 AND Magic=1""", 
			userId)
		return fetchone()[0]
		
class RaceAmazons(BaseRace):
	def countAdditionalRedeploymentUnits(self, userId, gameId):
		query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
		prevState = fetchone()[0]
		if prevState == misc.gameStates['finishTurn']:
			query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum+4 WHERE 
				OwnerId=%s AND RaceId=0""")
		elif prevState == misc.gameStates['conquer']:
			query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum-4 WHERE 
				OwnerId=%s AND RaceId=0""")
		else:
			raise BadFieldException('badStage')

class RaceSkeletons(BaseRace):
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
				WHERE OwnerId=%s AND RaceId=9""", regionsNum, raceDescription[9], userId)
		else:
			raise BadFieldException('badStage')

class RaceElves(BaseRace):
	def countAdditionalDefendingTokens(self):
		return 1

raceDescription = [
	{
		'name': 'Amazons',
		'initialNum': 6,
		'maxNum': 15
	},
	{
		'name': 'Dwarves',
		'initialNum': 3,
		'maxNum': 8		
	},
	{
		'name': 'Elves',
		'initialNum': 6,
		'maxNum': 11
	},
	{
		'name': 'Ghouls',
		'initialNum': 5,
		'maxNum': 10
	},
	{
		'name': 'Giants',
		'initialNum': 6,
		'maxNum': 11
	},
	{
		'name': 'Halflings',
		'initialNum': 6,
		'maxNum': 11
	},
	{
		'name': 'Humans',
		'initialNum': 5,
		'maxNum': 10
	},
	{
		'name': 'Orcs',
		'initialNum': 5,
		'maxNum': 10
	},
	{
		'name': 'Ratmen',
		'initialNum': 8,
		'maxNum': 13
	},
	{
		'name': 'Skeletons',
		'initialNum': 6,
		'maxNum': 20
	},
	{
		'name': 'Sorcerers',
		'initialNum': 5,
		'maxNum': 18
	},
	{
		'name': 'Tritons',
		'initialNum': 6,
		'maxNum': 11
	},
	{
		'name': 'Trolls',
		'initialNum': 5	,
		'maxNum': 10	
	},
	{
		'name': 'Wizards',
		'initialNum': 5,
		'maxNum': 10
	}		
]