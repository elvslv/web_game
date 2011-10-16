import misc_game
from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, WarHistoryEntry
from gameExceptions import BadFieldException
from checkFields import  checkObjectsListCorrection
from misc_game import *
from misc import *
from checkFields import *

dbi = Database()

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id

	def canConquer(self, region, tokenBadge):
		ans = (not tokenBadge.regions and (region.coast or region.border)
			) or tokenBadge.regions
		return ans
		
	def attackBonus(self, region, tokenBadge):
		return 0
	
	def decline(self, user): 
		curTokenBadge = user.currentTokenBadge
		user.declinedTokenBadge = curTokenBadge
		for region in curTokenBadge.regions:
			region.tokensNum = 1
			region.inDecline = True
		curTokenBadge.inDecline = True
		curTokenBadge.totalTokensNum = len(curTokenBadge.regions)
		user.tokensInHand = 0
	
	def turnEndReinforcements(self, user):
		return 0

	def turnStartReinforcements(self, user):		
		return 0

	def needRedeployment(self):
		return False
	
	def incomeBonus(self, user):
		return 0

	def defenseBonus(self):
		return 0

	def updateBonusStateAtTheEndOfTurn(self, tokenBadgeId):
		pass

	def conquered(self, regionId, tokenBadgeId):
		pass

	def enchant(self, tokenBadgeId, regionId):
		return BadFieldException('badRace')

	def clearRegion(self, tokenBadge, region):
		region.encampent = 0
		region.fortress = False
		region.dragon = False
		region.holeInTheGround = False
		region.hero = False
		return -1

	def sufferCasualties(self, tokenBadge):
		tokenBadge.totalTokensNum -= 1
		return -1

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
		
	def clearRegion(self, tokenBadge, region):
		region.holeInTheGround = False

class RaceGiants(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Giants', 6, 11)

	def attackBonus(self, region, tokenBadge):
		res = 0
		lands = filter(lambda x: x.region.mountain, tokenBadge.regions)
		for  land in lands:
			if region.adjacent(land.region):					#Need better names
					res = -1
					break
		return res

class RaceTritons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Tritons', 6, 11)

	def attackBonus(self, region, tokenBadge):
		return -1 if region.coast else 0

class RaceDwarves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Dwarves', 3, 8)

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: x.region.mine, tokenBadge.regions))

class RaceHumans(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Humans', 5, 10)

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: x.region.farmland, tokenBadge.regions))

class RaceOrcs(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Orcs', 5, 10)

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else tokenBadge.owner.getNonEmptyConqueredRegions()

class RaceWizards(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Wizards', 5, 10)

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: x.region.magic, tokenBadge.regions))
		
class RaceAmazons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Amazons', 6, 15)

	def turnStartReinforcements(self, user):
		return 4

	def needRedeployment(self):
		return True
	
class RaceSkeletons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Skeletons', 6, 18)

	def turnEndReinforcements(self, user):
		return user.getNonEmptyConqueredRegions() / 2
		
			
class RaceElves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Elves', 6, 11)

	def sufferCasualties(self, tokenBadge):
		return 0

	def clearRegion(self, tokenBadge, region):
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

	def enchant(self, tokenBadge, regState):
		game =  tokenBadge.owner.game
		victimBadge = regState.tokenBadge
		regState.checkIfImmune(True)
		if not (self.canConquer(regState.region, tokenBadge) and 
			specialPowerList[tokenBadge.specPowId].canConquer(regState.region, 
			tokenBadge)):
			raise BadFieldException('badRegion')
		if victimBadge == tokenBadge: 
			raise BadFieldException('badAttackedRace')			
		if not regState.tokensNum:
			raise BadFieldException('nothingToEnchant')
		if regState.tokensNum > 1:
			raise BadFieldException('cannotEnchantMoreThanOneToken')
		if regState.inDecline:
			raise BadFieldException('cannotEnchantDeclinedRace')
		if tokenBadge.totalTokensNum == self.maxNum: 
			raise BadFieldException('noMoreTokensInStorageTray')
		
		victimBadge.totalTokensNum -= 1
		tokenBadge.totalTokensNum += 1
		raceId, specialPowerId  = victimBadge.raceId, victimBadge.specPowId
		regState.tokenBadge = tokenBadge
		regState.owner = tokenBadge.owner
		regState.tokensNum = 1

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
	def __init__(self, name, tokensNum, bonusNum=None):
		self.name = name
		self.tokensNum = tokensNum
		self.bonusNum = bonusNum

	def setId(self, id):
		self.specialPowerId = id

	def canConquer(self, region, tokenBadge):
		return (tokenBadge.isNeighbor(region) or not tokenBadge.regions) and\
			not region.sea
		
	def attackBonus(self, regionId, tokenBadgeId):
		return 0

	def incomeBonus(self, tokenBadge):
		return 0

	def decline(self, user):
		if user.game.getLastState() != GAME_FINISH_TURN:
			raise BadFieldException('badStage')

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

	def setEncampments(self, tokenBadge, encampments):
		raise BadFieldException('badSpecialPower')

	def setFortifield(self, tokenBadge, fortifield):
		raise BadFieldException('badSpecialPower')

	def selectFriend(self, user, data):
		raise BadFieldException('badSpecialPower')

	def setHero(self, tokenBadgeId, heroes):
		raise BadFieldException('badSpecialPower')

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else 2	

class SpecialPowerBerserk(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Berserk', 4)

	def throwDice(self):
		return misc.throwDice()


class SpecialPowerBivouacking(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Bivouacking', 5, 5)
	
	def decline(self, user):
		BaseSpecialPower.decline(self, user)
		for region in user.regions:
			region.encampment = False
		
	def setEncampments(self, tokenBadge, encampments):
		checkObjectsListCorrection(encampments, 
			[{'name': 'regionId', 'type': int, 'min': 1}, 
			{'name': 'encampmentsNum', 'type': int, 'min': 0}])
		game = tokenBadge.owner.game
		freeEncampments = 5
		for encampment in encampments:
			region = game.map.getRegion(encampment['regionId']).getState(game.id)
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

	def attackBonus(self, region, tokenBadge):
		return -1

class SpecialPowerDiplomat(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Diplomat', 5, 1)
		

	def selectFriend(self, user, data):
		if not('friendId' in data and isinstance(data['friendId'], int)):
			raise BadFieldException('badFriendId')
		friend = dbi.getXbyY('User', 'id', data['friendId'])
		if friend.id == user.id or friend.game.id != user.game.id:
			raise BadFieldException('badFriend')

		curTurnHistory = filter(lambda x: x.turn == user.game.turn and 
			x.userId == user.id and x.state == GAME_CONQUER, user.game.history)
		if curTurnHistory:
			if friend.currentTokenBadge and filter(lambda x: x.warHistory.victimBadgeId == 
				friend.currentTokenBadge.id, curTurnHistory):
				raise BadFieldException('badFriend')

		dbi.updateHistory(user, GAME_CHOOSE_FRIEND, user.currentTokenBadge.id, 
			None, friend.id)

class SpecialPowerDragonMaster(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Dragon master', 5, 1)

	def dragonAttack(self, tokenBadge, regState):
		regState.checkIfImmune()
		if not(racesList[tokenBadge.raceId].canConquer(regState.region, tokenBadge) 
			and self.canConquer(regState.region, tokenBadge)):
			raise BadFieldException('badRegion')
			
		attackedTokenBadge = regState.tokenBadge
		attackedTokensNum = regState.tokensNum
		if attackedTokenBadge and attackedTokenBadge.id == tokenBadge.id:
			raise BadFieldException('badRegion')
			
		misc_game.clearFromRace(regState)
		if attackedTokenBadge:
			attackedTokenBadge.totalTokensNum += racesList[attackedTokenBadge.raceId].sufferCasualties(
				attackedTokenBadge)
		else:
			attackedTokensNum = 0
		##check anything else?
		for region in tokenBadge.regions: 
			region.dragon = False
		regState.tokenBadge = tokenBadge
		regState.dragon= True
		regState.tokensNum = 1
		regState.owner = tokenBadge.owner
		tokenBadge.owner.tokensInHand -= 1
		dbi.updateWarHistory(tokenBadge.owner, attackedTokenBadge.id if 
			attackedTokenBadge else None, tokenBadge.id, None, regState.regionId,
			attackedTokensNum, ATTACK_DRAGON)

	def clearRegion(self, tokenBadge, region):
		tokenBadge.specPowNum -= 1
		region.dragon = False
		
	def decline(self, user):
		BaseSpecialPower.decline(self, user)
		for region in user.regions: region.dragon = False
		
class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def canConquer(self, region, tokenBadge):
		return ((not tokenBadge.isNeighbor(region) and tokenBadge.regions) or\
			not tokenBadge.regions) and not region.sea

class SpecialPowerForest(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Forest', 4)

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: x.region.forest, tokenBadge.regions))

class SpecialPowerFortified(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Fortifield', 3, 6)
		self.maxNum = 6

	def clearRegion(self, tokenBadge, region):
		if region.fortress:
			tokenBadge.specPowNum = max(tokenBadge.specPowNum - 1, 0)

	def setFortifield(self, tokenBadge, fortifield):
		if not('regionId' in fortifield and isinstance(fortifield['regionId'], int)):
			raise BadFieldException('badRegionId')
		user = tokenBadge.owner
		regionId = fortifield['regionId']
		regState = user.game.map.getRegion(regionId).getState(user.game.id)

		if regState.ownerId != tokenBadge.owner.id:
			raise BadFieldException('badRegion')

		if regState.fortress:
			raise BadFieldException('tooManyFortifieldsInRegion')

		fortifieldsOnMap = len(filter(lambda x: x.fortress == True, tokenBadge.regions))
		if fortifieldsOnMap >= self.maxNum:
			raise BadFieldException('tooManyFortifieldsOnMap')
		if fortifieldsOnMap == tokenBadge.specPowNum:
			raise BadFieldException('tooManyFortifields')
		regState.fortress = True

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else len(filter(lambda x: x.fortress, tokenBadge.regions))

class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5, 2)

 	def setHero(self, tokenBadge, heroes):
		checkObjectsListCorrection(heroes, 
			[{'name': 'regionId', 'type': int, 'min': 1}])

		if len(heroes) > 2:
			raise BadFieldException('badSetHeroCommand')
		
		for region in tokenBadge.regions:
			region.hero = False
		user = tokenBadge.owner
		for hero in heroes:
			regState = user.game.map.getRegion(hero['regionId']).getState(
				user.game.id)
			
			if regState.owner.currentTokenBadge != tokenBadge:
				raise BadFieldException('badRegion')

			regState.hero = True

	def decline(self, user):
		BaseSpecialPower.decline(self, user)
		for region in user.regions:
			region.hero = False

	def clearRegion(self, tokenBadge, region):
		tokenBadge.specPowNum -= 1
		region.hero = False
		

class SpecialPowerHill(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Hill', 4)

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else len(filter(lambda x: x.region.hill, tokenBadge.regions))

class SpecialPowerMerchant(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Merchant', 2) 

	def incomeBonus(self, user):
		return len(user.regions)

class SpecialPowerMounted(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Mounted', 5) 

	def attackBonus(self, region, tokenBadge):
		return -1 if region.farmland or region.hill else 0


class SpecialPowerPillaging(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Pillaging', 5)
	
	def incomeBonus(self, user): 
		return user.getNonEmptyConqueredRegions()

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 

	def incomeBonus(self, tokenBadge): 
		return len(filter(lambda x: x.region.swamp, tokenBadge.regions))
	
	def canConquer(self, region, tokenBadge):
		return (tokenBadge.isNeighbor(region) and tokenBadge.regions) or not\
			tokenBadge.regions 


class SpecialPowerStout(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Stout', 4) 

	def decline(self, user):
		pass

class SpecialPowerSwamp(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Swamp', 4) 
	
	def incomeBonus(self, tokenBadge): 
		return 0 if tokenBadge.inDecline else len(filter(lambda x: x.region.swamp, tokenBadge.regions))

class SpecialPowerUnderworld(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Underworld', 5) 

	def canConquer(self, region, tokenBadge):
		if BaseSpecialPower.canConquer(self, region, tokenBadge):
			return True
		cav = False
		for reg in tokenBadge.regions:
			if reg.cavern:
				cav = True
				break

		return (region.cavern and cav)
		

	def attackBonus(self, region, tokenBadge):
		return -1 if region.cavern else 0

	
class SpecialPowerWealthy(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Wealthy', 4, 1) 
	
	def incomeBonus(self, tokenBadge):
		if tokenBadge.specPowNum == 1:
			tokenBadge.specPowNum = 0
			return 7
		return 0

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
