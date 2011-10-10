from gameExceptions import BadFieldException
from misc_game import *
from misc import *

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id
	
	def canConquer(self, region, tokenBadge):
		return not region.sea and ((not tokenBadge.regions and (region.coast or region.border)) or tokenBadge.isNeighbor(region))

	def conquerBonus(self, region, tokenBadge):
		return 0
	
	def decline(self, user): 
		user.decline()
	
	def turnEndReinforcements(self, user):
		return 0

	def turnStartReinforcements(self, user):		
		return 0
	
	def incomeBonus(self, user):
		return 0

	def countAddDefendingTokensNum(self):
		return -1

	def defenseBonus(self):
		return 0

	def getInitBonusNum(self):
		return 0

	def flee(self, region):
		pass
	
	def updateBonusStateAtTheEndOfTurn(self, tokenBadgeId):
		pass

	def conquered(self, currentRegionId, tokenBadgeId):
		pass

	def enchant(self, tokenBadgeId, currentRegionId):
		return BadFieldException('badRace')

	def clearRegion(self, tokenBadge, region):
		region.encampent = 0
		region.fortress = False
		region.dragon = False
		region.holeInTheGround = False
		region.hero = False

	def sufferCasualties(self, tokenBadge):
		tokenBadge.totalTokensNum -= 1

class RaceHalflings(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Halflings', 6, 11)
	
	def conquered(self, region, tokenBadge):	
		if len(filter(lambda x: x.holeInTheGround, tokenBadge.regions)) >= 2:
			return
		for region in tokenBadge.regions: region.holeInTheGround = True

	def canConquer(self, region, tokenBadge):
		return True

	
	def getInitBonusNum(self):
		return 2

	def decline(self, user):
		BaseRace.decline(user)
		for region in user.currentTokenBadge.regions: region.holeInTheGround = False
		
	def flee(self, region):
		region.holeInTheGround = False

class RaceGiants(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Giants', 6, 11)

	def conquerBonus(self, region, tokenBadge):
		res = 0
		lands = filter(lambda x: x.region.mountain, tokenBadge.regions)
		for  land in lands:
			if currentRegion.adjacent(land.region):					#how do I set this straight?
					res = -1
					break
		return res

class RaceTritons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Tritons', 6, 11)

	def conquerBonus(self, currentRegion, tokenBadge):
		return -1 if currentRegion.region.coast else 0

class RaceDwarves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Dwarves', 3, 8)

	def incomeBonus(self, user):
		return len(filter(lambda x: x.region.mine, user.currentTokenBadge.regions))

class RaceHumans(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Humans', 5, 10)

	def incomeBonus(self, user):
		return len(filter(lambda x: x.region.farmland, user.currentTokenBadge.regions))

class RaceOrcs(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Orcs', 5, 10)

	def incomeBonus(self, user):
		return game.getNonEmptyConqueredRegions(user.currentTokenBadge)

class RaceWizards(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Wizards', 5, 10)

	def incomeBonus(self, user):
		return len(filter(lambda x: x.region.magic, user.currentTokenBadge.regions))
		
class RaceAmazons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Amazons', 6, 15)

	def turnEndReinforcements(self,  user):
		return -4 if  user.game.getLastState() == GAME_CONQUER else 0

	def turnStartReinforcements(self, user):
		return 4 if user.game.getLastState()  in (GAME_FINISH_TURN, GAME_SELECT_RACE) else 0

	def attackReinforcenments(self, game):		
		return 0

class RaceSkeletons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Skeletons', 5, 18)

	def turnEndReinforcements(self, user):
		return user.game.getNonEmptyConqueredRegions(user.tokenBadge, user.game) / 2
		
			
class RaceElves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Elves', 6, 11)

	def sufferCasualties(self):
		return 0

class RaceRatmen(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Ratmen', 8, 13)

class RaceTrolls(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Trolls', 5, 10)

	def defenseBonus(self):
		return 1

class RaceSorcerers(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Sorcerers', 5, 18)

	def enchant(self, tokenBadge, currentRegion):
		currentRegion.checkIfImmune()
		currentRegion.checkIfCorrect(tokenBadge)
		attackedTokenBadge = currentRegion.tokenBadge
		if attackedTokenBadge == tokenBadge: raise BadFieldException('badAttackedRace')
		if currentRegion.encampment: raise BadFieldException('regionIsImmune')
		if not currentRegion.tokensNum: 	raise BadFieldException('nothingToEnchant')
		if currentRegion.tokensNum > 1: 	raise BadFieldException('cannotEnchantMoreThanOneToken')
		if currentRegion.inDecline: raise BadFieldException('cannotEnchantDeclinedRace')

		if tokenBadge.totalTokensNum == self.maxNum: raise BadFieldException('noMoreTokensInStorageTray')
		attackedTokenBadge.totalTokensNum -= 1
		tokenBadge.totalTokensNum += 1
		raceId, specialPowerId  = attackedTokenBadge.raceId,attackedTokenBadge.specPowerId
		racesList[raceId].clearRegion(attackedTokenBadge, currentRegion)
		specialPowerList[specialPowerId].clearRegion(attackedTokenBadge, currentRegion)
		currentRegion.tokenBadge = tokenBadge
		currentRegion.owner = tokenBadge.owner
		currentRegion.tokensNum = 1
		dbi.add(History(user.id, game.id, GAME_CONQUER, tokenBadge.id))
		dbi.add(WarHistory(dbi.last_id(), tokenBadge.id, currentRegion, attackedTokenBadge, attackedTokenBadge,
			attackedTokensNum, dice, ATTACK_CONQUER))
		
		updateHistory(userId, gameId, GAME_CONQUER, tokenBadgeId)
		updateConquerHistory(lastId(), tokenBadgeId, regionId, attackedTokenBadge.tokensNum, 
			attackedTokenBadge.encampment, -1, ATTACK_ENCHANT)


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

	def canConquer(self, region, tokenBadge):
		return False
		
	def conquerBonus(self, regionId, tokenBadgeId):
		return 0

	def incomeBonus(self, user):
		return 0

	def decline(self, user):
		if user.game.getLastState() != GAME_FINISH_TURN:
			raise BadFieldException('badStage')

	def getInitBonusNum(self):
		return 0

	def updateBonusStateAtTheEndOfTurn(self, tokenBadgeId):
		pass

	def turnFinished(self, tokenBadgeId):
		pass

	def dragonAttack(self, tokenBadgeId, regionId, tokensNum):
		raise BadFieldException('badAction') 

	def clearRegion(self, tokenBadge, region):
		pass

	def throwDice(self):
		raise BadFieldException('badAction')


	def setEncampments(encampments, tokenBadgeId):
		raise BadFieldException('badSpecialPower')

	def setFortifield(fortifield, tokenBadgeId):
		raise BadFieldException('badSpecialPower')
	

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def incomeBonus(self, user):
		return 2 if not user.currentTokenBadge.inDecline else 0

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

	def decline(self, user):
		BaseSpecialPower.decline(user)
		for region in user.regions:
			region.encampment = False

	def setEncampments(self, encampments, tokenBadge):
		checkObjectsListCorrection(encampments, 
			[{'name': 'regionId', 'type': int, 'min': 1}, 
			{'name': 'encampmentsNum', 'type': int, 'min': 0}])

		tokenBadge.region.encampment = 0
		freeEncampments = 5
		for encampment in encampments:
			region =dbi.getRegionById(encampment['regionId'])
			encampmentsNum = encampment['encampmentsNum']
			if region.tokenBadge != tokenBadge:
				raise BadFieldException('badRegion')
			if encampmentsNum > freeEncampments:
				raise BadFieldException('notEnoughEncampentsForRedeployment')
				region.encampent = encampmentsNum

			freeEncampments -= encampmentsNum

class SpecialPowerCommando(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Commando', 4)

	def conquerBonus(self, region, tokenBadge):
		return -1

class SpecialPowerDiplomat(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Diplomat', 5)
		
	def getInitBonusNum(self):
		return 1

	def selectFriend(data, userId, tokenBadgeId, gameId):
		pass
	#	if not('friendId' in data and isinstance(data['friendId'], int)):
	#		raise BadFieldException('badFriendId')
#
#		friendId, friendBadgeId = extractValues('Users', ['Id', 
#			'CurrentTokenBadge'], [data['friendId']])

#		if friendId == userId:
#			raise BadFieldException('badFriend')
			
#		if not query("""SELECT 1 FROM Users a, Users b WHERE a.Id=%s AND b.Id=%s
#			AND a.GameId=b.GameId"""):
#			raise BadFieldException('badFriend')
			
#		if query("""SELECT 1 FROM AttackingHistory a, History b, Games c, 
#			TokenBadges d WHERE a.AttackingTokenBadgeId=%s AND 
#			a.AttackedTokenBadgeId=%s AND a.HistoryId=b.HistoryId AND 
#			b.GameId=c.GameId AND b.Turn=c.Turn	AND c.GameId=d.GameId AND 
#			d.TokenBadgeId=%s AND d.InDecline=False""", tokenBadgeId, 
#			friendBadgeId, friendBadgeId):
#			raise BadFieldException('badFriend')

#		query("""INSERT INTO History(UserId, GameId, State, TokenBadgeId, Turn, 
#			Friend) SELECT %s, %s, %s, %s, Turn FROM Games WHERE GameId=%s""", 
#			userId, gameId, GAME_CHOOSE_FRIEND, tokenBadgeId, gameId, friendId)


class SpecialPowerDragonMaster(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Dragon master', 5)
	
	def getInitBonusNum(self):
		return 1

	def dragonAttack(self, tokenBadgeId, regionId, tokensNum):
		pass
	#	regionId, gameId = extractValues('CurrentRegionState', ['RegionId', 'GameId'], 
	#		[regionId, getGameIdByTokenBadge(tokenBadgeId)])
	#	checkRegionIsImmune(regionId, gameId)
	#	checkRegionIsCorrect(regionId, tokenBadgeId)
	#	raceId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)[0]
		
	#	if not(racesList[raceId].tryToConquerRegion(regionId, tokenBadgeId) 
	#		and self.tryToConquerRegion(regionId, tokenBadgeId)):
	#		raise BadFieldException('badRegion')
			
	#	if query("""SELECT 1 FROM History a, AttackingHistory b, TokenBadges c, 
	#		Users d, Games e WHERE b.AttackingTokenBadgeId=%s AND 
	#		c.TokenBadgeId=b.AttackingTokenBadgeId AND c.UserId=d.Id AND 
	#		d.GameId=a.GameId AND e.GameId = a.GameId AND a.Turn=e.Turn AND 
	#		a.HistoryId=b.HistoryId AND b.AttackType=%s""", tokenBadgeId, 
	#		ATTACK_DRAGON):
	#		raise BadFieldException('dragonAlreadyAttackedOnThisTurn')
			
	#	query("""SELECT a.TokenBadgeId, a.TokensNum FROM CurrentRegionState a
	#		WHERE a.RegionId=%s AND a.GameId""", regionId, gameId)
	#	row = fetchone()
	#	if row[0] == tokenBadgeId:
	#		raise BadFieldException('badRegion')
		##check anything else?
	#	query('UPDATE CurrentRegionState SET Dragon=FALSE WHERE TokenBadgeId=%s', 
	#		tokenBadgeId)
	#	query("""UPDATE CurrentRegionState SET TokenBadgeId=%s, Dragon=TRUE, 
	#		TokensNum=%s WHERE RegionId=%s AND GameId=%s""", tokenBadgeId, 
	#		tokensNum, regionId, gameId)
	#	
	#		updateHistory(userId, gameId, GAME_CONQUER, tokenBadgeId)
	#		updateConquerHistory(lastId(), tokenBadgeId, regionId, row[0], row[2], 
	#			-1, ATTACK_DRAGON)

	def decline(self, user):
		BaseSpecialPower.decline(user)
		for region in user.regions: region.dragon = False
		
class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def canConquer(self, region, tokenBadge):
		return True
#		isAdjacent, regions = isRegionAdjacent(regionId, tokenBadgeId)
#		regionInfo = getRegionInfoById(regionId, getGameIdByTokenBadge(tokenBadgeId))
#		return ((not isAdjacent and regions) or not regions) and not regionInfo['sea']


class SpecialPowerForest(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Forest', 4)

	def incomeBonus(self, user):
		return len(filter(lambda x: x.region.forest, user.currentTokenBadge.regions))

class SpecialPowerFortified(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Fortified', 3)
		self.maxNum = 6

	def getInitBonusNum(self):
		return 1

	def incomeBonus(self, user):
		return len(filter(lambda x: x.fortified, user.regions))

	def clearRegion(self, tokenBadge, region):
		pass
#		query("""SELECT TotalSpecialPowerBonusNum FROM TokenBadges WHERE 
#			TokenBadgeId=%s""", tokenBadgeId)
#		query("""UPDATE TokenBadges SET TotalSpecialPowerBonusNum=GREATEST(%s-1,
#			0) WHERE TokenBadgeId=%s""", fetchone()[0], tokenBadgeId)

	def setFortified(fortifield, tokenBadgeId):
		pass
#		if not('regionId' in fortifield and isinstance(fortifield['regionId'])):
#			raise BadFieldException('badRegionId')

#		regionId, gameId, ownerBadgeId, hasFortifield = extractValues(
#			'CurrentRegionState', ['RegionId', 'GameId', 'TokenBadgeId', 
#			'Fortifield'], [fortifield['regionId'], 
#			getGameIdByTokenBadge(tokenBadgeId)])

#		if ownerBadgeId != tokenBadgeId:
#			raise BadFieldException('badRegion')

#		if hasFortifield:
#			raise BadFieldException('tooManyFortifieldsInRegion')

#		query("""SELECT COUNT(*) FROM CurrentRegionState WHERE Fortifield=True 
#			AND TokenBadgeId=%s""", tokenBadgeId)
#		fortifieldsOnMap = fetchone()[0]
#		if fortifieldsOnMap >= self.maxNum:
#			raise BadFieldException('tooManyFortifieldsOnMap')
#		query("""SELECT TotalSpecialPowerBonusNum FROM TokenBadges WHERE 
#			TokenBadgeId=%s""", tokenBadgeId)
#		if fortifieldsOnMap == fetchone()[0]:
#			raise BadFieldException('tooManyFortifields')
#		query("""UPDATE CurrentRegionState SET Fortifield=True WHERE 
#			RegionId=%s AND GameId=%s""", regionId, gameId)
	

class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5)
		
	def getInitBonusNum(self):
		return 2

	def decline(self, user):
		BaseSpecialPower.decline(user)
		for region in user.regions:
			region.hero = False

 	def setHero(heroes, tokenBadgeId):
 		pass
	#	checkObjectsListCorrection(heroes, 
	#		[{'name': 'regionId', 'type': int, 'min': 1}])
#
#		if len(heroes) > 2:
#			raise BadFieldException('badSetHeroCommand')
#
#		query('UPDATE CurrentRegionState SET Hero=False WHERE TokenBadgeId=%s',
#			tokenBadgeId)
#		for hero in heroes:
#			regionId, gameId, ownerBadgeId = extractValues('CurrentRegionState', 
#				['RegionId', 'GameId', 'TokenBadgeId'], [heroe['regionId'], 
#				getGameIdByTokenBadge(tokenBadgeId)])

#			if ownerBadgeId != tokenBadgeId:
#				raise BadFieldException('badRegion')

#			query("""SELECT 1 FROM CurrentRegionState WHERE RegionId=%s 
#				AND TokenBadgeId=%s""", regionId, tokenBadgeId)
#			if not fetchone():
#				raise BadFieldException('badRegion')

#			query('UPDATE CurrentRegionState SET Hero=True WHERE TokenBadgeId=%s',
#				tokenBadgeId)
		

class SpecialPowerHill(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Hill', 4)

	def incomeBonus(self, user):
		return len(filter(lambda x: x.region.hill, user.currentTokenBadge.regions))


class SpecialPowerMerchant(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Merchant', 2) 

	def incomeBonus(self, user):
		return len(user.regions)

class SpecialPowerMounted(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Mounted', 5) 

	def conquerBonus(self, region, tokenBadge):
		return -1 if region.farmland or region.hill else 0


class SpecialPowerPillaging(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Pillaging', 5)
	
	def countAdditionalCoins(self, user): 
		return user.game.getNonEmptyConqueredRegions(user.tokenBadge)

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 
	
	def canConquer(self, region, tokenBadge):
		return True
	#	isAdjacent, regions = isRegionAdjacent(regionId, tokenBadgeId)
	#	return (isAdjacent and regions) or not regions 


class SpecialPowerStout(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Stout', 4) 

	def decline(self, user):
		pass

class SpecialPowerSwamp(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Swamp', 4) 
	
	def incomeBonus(self, user): 
		return len(filter(lambda x: x.swamp, user.currentTokenBadge.regions))

class SpecialPowerUnderworld(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Underworld', 5) 

	def canConquer(self, region, tokenBadge):
#		if BaseSpecialPower.tryToConquerRegion(self, regionId, tokenBadgeId):
#			return True
#		query("""SELECT a.Cavern, b.Cavern FROM Regions a, Regions b, 
#			CurrentRegionState c WHERE a.RegionId=%s 
#			AND c.TokenBadgeId=%s AND b.RegionId=c.RegionId AND b.MapId=%s 
#			AND a.MapId=b.MapId""", attackedRegion, tokenBadgeId, 
#			getMapIdByTokenBadge(tokenBadgeId))
		cavern1, cavern2 = True, True
		return (cavern1 and cavern2)
		
	def conquerBonus(self, region, tokenBadge):
		return -1 if region.cavern else 0

	
class SpecialPowerWealthy(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Wealthy', 4) 
	
	def getInitBonusNum(self):
		return 1

	def incomeBonus(self, user):
		return 0
#		query("""SELECT b.Turn-a.Turn FROM History a, Games b WHERE a.TokenBadgeId=%s 
#			AND a.State=%s AND b.GameId=a.GameId""", 
#			getTokenBadgeIdByRaceAndUser(raceId, userId), GAME_SELECT_RACE)
#		return 0 if fetchone()[0] else 7

specialPowerList = [
	SpecialPowerAlchemist(),
	SpecialPowerBerserk(),
 	SpecialPowerBivouacking(),
	SpecialPowerCommando(),
	SpecialPowerDiplomat(),
	SpecialPowerDragonMaster(),
	SpecialPowerFlying(),
	SpecialPowerForest(),
	SpecialPowerFortified(),
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