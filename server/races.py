import misc_game
from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, WarHistoryEntry, dbi
from gameExceptions import BadFieldException
from checkFields import  checkObjectsListCorrection
from misc_game import *
from misc_const import *
from checkFields import *

class BaseRace:
	def __init__(self, name, initialNum, maxNum):
		self.name = name
		self.initialNum = initialNum
		self.maxNum = maxNum

	def setId(self, id):
		self.raceId = id

	def canConquer(self, region, tokenBadge):
		ans = (not len(tokenBadge.regions) and region.border) or len(tokenBadge.regions)
		return ans
					
	def attackBonus(self, region, tokenBadge):
		return 0
	
	def decline(self, user, leaveGame): 
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

	def turnStartReinforcements(self):		
		return 0

	def needRedeployment(self):
		return False
	
	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: self.regBonus(x, not tokenBadge.inDecline), tokenBadge.regions))

	def defenseBonus(self):
		return 0

	def conquered(self, regionId, tokenBadgeId):
		pass

	def canEnchant(self):
		return False

	def enchant(self, tokenBadgeId, regionId):
		raise BadFieldException('badRace')

	def clearRegion(self, tokenBadge, region):
		region.encampment = 0
		region.fortified = False
		region.dragon = False
		region.holeInTheGround = False
		region.hero = False
		return -1

	def getCasualties(self):
		return 1
		
	def sufferCasualties(self, tokenBadge):
		tokenBadge.totalTokensNum -= 1

	def regBonus(self, reg, tok = None):
		return 0

class RaceHalflings(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Halflings', 6, 11)
	
	def conquered(self, region, tokenBadge):	
		if len(dbi.query(WarHistoryEntry).filter(WarHistoryEntry.agressorBadgeId == tokenBadge.id).all()) >= 2:
			return
		for region in tokenBadge.regions: region.holeInTheGround = True

	def canConquer(self, region, tokenBadge):
		return True

	def getInitBonusNum(self):
		return 2

	def decline(self, user, leaveGame):
		BaseRace.decline(self, user, leaveGame)
		for region in user.currentTokenBadge.regions: region.holeInTheGround = False
		
	def clearRegion(self, tokenBadge, region):
		region.holeInTheGround = False

class RaceGiants(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Giants', 6, 11)

	def attackBonus(self, region, tokenBadge):
		res = 0
		lands = filter(lambda x: x.region.mountain if hasattr(x, 'region') else x.mountain, 
					tokenBadge.regions)
		for  land in lands:
			r = land.region if hasattr(land, 'region') else land
			if region.isAdjacent(r) or (r.cavern and tokenBadge.specPowId == 17 and\
					region.region.cavern if hasattr(region, 'region') else region.cavern):					
				res = -1
				break
		return res

class RaceTritons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Tritons', 6, 11)

	def attackBonus(self, region, tokenBadge):
		return -1 if region.isCoast() and not region.sea else 0

class RaceDwarves(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Dwarves', 3, 8)

	def regBonus(self, reg, tok = None):
		return reg.region.mine if hasattr(reg, 'region') else reg.mine


class RaceHumans(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Humans', 5, 10)

	def regBonus(self, reg, tok = None):
		if not tok:
			return 0
		return reg.region.farmland if hasattr(reg, 'region') else reg.farmland


class RaceOrcs(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Orcs', 5, 10)

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else tokenBadge.Owner().getNonEmptyConqueredRegions()

class RaceWizards(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Wizards', 5, 10)

	def regBonus(self, reg, tok = None):
		if not tok:
			return 0
		return reg.region.magic if hasattr(reg, 'region') else reg.magic
		
class RaceAmazons(BaseRace):
	def __init__(self):
		BaseRace.__init__(self, 'Amazons', 6, 15)

	def turnStartReinforcements(self):
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

	def getCasualties(self):
		return 0

	def sufferCasualties(self, tokenBadge):
		pass

	def clearRegion(self, tokenBadge, region):
		pass
		
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

	def canEnchant(self):
		return True
	
	def enchant(self, tokenBadge, regState):
		game =  tokenBadge.Owner().game
		victimBadge = regState.tokenBadge
		if not (self.canConquer(regState.region, tokenBadge) and 
			specialPowerList[tokenBadge.specPowId].canConquer(regState.region, 
			tokenBadge)):
			raise BadFieldException('badRegion')
			
		if not regState.inDecline:
			tokenBadge.Owner().checkForFriends(regState.owner)

		print 'v', victimBadge.id, tokenBadge.id
		if victimBadge.id == tokenBadge.id: 
			raise BadFieldException('badAttackedRace')			
		if not regState.tokensNum:
			raise BadFieldException('nothingToEnchant')
		if regState.tokensNum > 1:
			raise BadFieldException('cannotEnchantMoreThanOneToken')
		if regState.inDecline:
			raise BadFieldException('cannotEnchantDeclinedRace')
		regState.checkIfImmune(True)
		if tokenBadge.totalTokensNum == self.maxNum: 
			raise BadFieldException('noMoreTokensInStorageTray')
		
		victimBadge.totalTokensNum -= 1
		tokenBadge.totalTokensNum += 1
		raceId, specialPowerId  = victimBadge.raceId, victimBadge.specPowId
		regState.tokenBadge = tokenBadge
		regState.owner = tokenBadge.Owner()
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
	def __init__(self, name, tokensNum, bonusNum=None, redeployReqName=None):
		self.name = name
		self.tokensNum = tokensNum
		self.bonusNum = bonusNum
		self.redeployReqName = redeployReqName

	def setId(self, id):
		self.specialPowerId = id

	def canConquer(self, region, tokenBadge):
		return (tokenBadge.isNeighbor(region) or not len(tokenBadge.regions)) and\
			not region.sea

	def canUseDragon(self):
		return False
		
	def attackBonus(self, regionId, tokenBadge):
		return 0

	def canDecline(self, user, leaveGame):
		return leaveGame or user.game.getLastState() == GAME_FINISH_TURN

	def decline(self, user, leaveGame):
		if not self.canDecline(user, leaveGame):
			raise BadFieldException('badStage')

	def turnFinished(self, tokenBadgeId):
		pass

	def dragonAttack(self, tokenBadgeId, regionId):
		raise BadFieldException('badStage') 

	def clearRegion(self, tokenBadge, region):
		pass

	def throwDice(self, game, dice = None):
		raise BadFieldException('badStage')

	def setEncampments(self, tokenBadge, encampments, data):
		raise BadFieldException('badStage')

	def setFortified(self, tokenBadge, fortified, data):
		raise BadFieldException('badStage')

	def canSelectFriend(self):
		return False

	def selectFriend(self, user, data):
		raise BadFieldException('badStage')

	def setHero(self, tokenBadgeId, heroes, data):
		raise BadFieldException('badStage')

	def canThrowDice(self):
		return False

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: self.regBonus(x, not tokenBadge.inDecline), tokenBadge.regions))

	def regBonus(self, reg, tok = None):
		return 0

class SpecialPowerAlchemist(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Alchemist', 4)

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else 2	

class SpecialPowerBerserk(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Berserk', 4)

	def throwDice(self, game, dice = None):
		return misc_game.throwDice(game, dice)

	def canThrowDice(self):
		return True


class SpecialPowerBivouacking(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Bivouacking', 5, 5, 'encampments')
	
	def decline(self, user, leaveGame):
		BaseSpecialPower.decline(self, user, leaveGame)
		for region in user.regions:
			region.encampment = False
		
	def setEncampments(self, tokenBadge, encampments, data):
		checkObjectsListCorrection(encampments, 
			[{'name': 'regionId', 'type': int, 'min': 1}, 
			{'name': 'encampmentsNum', 'type': int, 'min': 0}])
		game = tokenBadge.Owner().game
		freeEncampments = 5
		for encampment in encampments:
			region = game.map.getRegion(encampment['regionId']).getState(game.id)
			encampmentsNum = encampment['encampmentsNum']
			if region.tokenBadge != tokenBadge or not region.tokensNum:
				raise BadFieldException('badRegion')
			if encampmentsNum > freeEncampments:
				raise BadFieldException('notEnoughEncampmentsForRedeployment')
			region.encampment = encampmentsNum
			freeEncampments -= encampmentsNum

class SpecialPowerCommando(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Commando', 4)

	def attackBonus(self, region, tokenBadge):
		return -1

class SpecialPowerDiplomat(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Diplomat', 5, 1)
		
	def canSelectFriend(self):
		return True
		
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
		BaseSpecialPower.__init__(self, 'DragonMaster', 5, 1)

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
			racesList[attackedTokenBadge.raceId].sufferCasualties(attackedTokenBadge)
		else:
			attackedTokensNum = 0
		##check anything else?
		for region in tokenBadge.regions: 
			region.dragon = False
		regState.tokenBadge = tokenBadge
		regState.dragon = True
		regState.tokensNum = 1
		regState.owner = tokenBadge.Owner()
		regState.inDecline = False
		tokenBadge.Owner().tokensInHand -= 1
		if attackedTokenBadge:
			racesList[attackedTokenBadge.raceId].sufferCasualties(attackedTokenBadge)
			attackedTokenBadge.Owner().tokensInHand += attackedTokensNum - racesList[attackedTokenBadge.raceId].getCasualties()
		dbi.updateWarHistory(tokenBadge.Owner(), attackedTokenBadge.id if 
			attackedTokenBadge else None, tokenBadge.id, None, regState.regionId,
			attackedTokensNum, ATTACK_DRAGON)

	def clearRegion(self, tokenBadge, region):
		tokenBadge.specPowNum -= 1
		region.dragon = False

	def canUseDragon(self):
		return True
		
	def decline(self, user, leaveGame):
		BaseSpecialPower.decline(self, user, leaveGame)
		for region in user.regions: region.dragon = False
		
class SpecialPowerFlying(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Flying', 5)

	def canConquer(self, region, tokenBadge):
		return not region.sea

class SpecialPowerForest(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Forest', 4)

	def incomeBonus(self, tokenBadge):
		return len(filter(lambda x: x.region.forest, tokenBadge.regions)) if not tokenBadge.inDecline else 0

class SpecialPowerFortified(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Fortified', 3, 6, 'fortified')
		self.maxNum = 6

	def clearRegion(self, tokenBadge, region):
		if region.fortified:
			tokenBadge.specPowNum = max(tokenBadge.specPowNum - 1, 0)

	def setFortified(self, tokenBadge, fortified, data):
		if not('regionId' in fortified and isinstance(fortified['regionId'], int)):
			raise BadFieldException('badRegionId')
		user = tokenBadge.Owner()
		regionId = fortified['regionId']
		regState = user.game.map.getRegion(regionId).getState(user.game.id)

		if regState.ownerId != tokenBadge.Owner().id or not regState.tokensNum:
			raise BadFieldException('badRegion')

		if regState.fortified:
			raise BadFieldException('tooManyFortifiedsInRegion')

		fortifiedsOnMap = len(filter(lambda x: x.fortified == True, tokenBadge.regions))
		if fortifiedsOnMap >= self.maxNum:
			raise BadFieldException('tooManyFortifiedsOnMap')
		if fortifiedsOnMap == tokenBadge.specPowNum:
			raise BadFieldException('tooManyFortifieds')
		regState.fortified = True

	def incomeBonus(self, tokenBadge):
		return 0 if tokenBadge.inDecline else len(filter(lambda x: x.fortified, tokenBadge.regions))

class SpecialPowerHeroic(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Heroic', 5, 2, 'heroes')

 	def setHero(self, tokenBadge, heroes, data):
		checkObjectsListCorrection(heroes, 
			[{'name': 'regionId', 'type': int, 'min': 1}])

		if len(heroes) > 2:
			raise BadFieldException('badSetHeroCommand')
		if len(heroes) < 2 and len(data['regions']) > 1:
			raise BadFieldException('badSetHeroCommand')
			
		for region in tokenBadge.regions:
			region.hero = False
		user = tokenBadge.Owner()
		for hero in heroes:
			regState = user.game.map.getRegion(hero['regionId']).getState(
				user.game.id)
			
			if not regState.owner or regState.owner.currentTokenBadge != tokenBadge or\
				not region.tokensNum:
				raise BadFieldException('badRegion')

			regState.hero = True

	def decline(self, user, leaveGame):
		BaseSpecialPower.decline(self, user, leaveGame)
		for region in user.regions:
			region.hero = False

	def clearRegion(self, tokenBadge, region):
		tokenBadge.specPowNum -= 1
		region.hero = False
		

class SpecialPowerHill(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Hill', 4)

	def regBonus(self, reg, tok = None):
		if not tok:
			return 0
		f = reg.region.hill if hasattr(reg, 'region') else reg.hill
		return f

class SpecialPowerMerchant(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Merchant', 2) 

	def incomeBonus(self, tokenBadge):
		return len(tokenBadge.regions)

class SpecialPowerMounted(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Mounted', 5) 

	def attackBonus(self, region, tokenBadge):
		return -1 if region.farmland or region.hill else 0


class SpecialPowerPillaging(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Pillaging', 5)
	
	def incomeBonus(self, tokenBadge): 
		return tokenBadge.Owner().getNonEmptyConqueredRegions()

class SpecialPowerSeafaring(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Seafaring', 5) 
	
	def canConquer(self, region, tokenBadge):
		return (tokenBadge.isNeighbor(region) and tokenBadge.regions) or not\
			tokenBadge.regions 


class SpecialPowerStout(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Stout', 4) 

	def canDecline(self, user, leaveGame):
		return True

class SpecialPowerSwamp(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Swamp', 4) 
	
	def regBonus(self, reg, tok = None):
		if not tok:
			return 0
		return reg.region.swamp if hasattr(reg, 'region') else reg.swamp

class SpecialPowerUnderworld(BaseSpecialPower):
	def __init__(self):
		BaseSpecialPower.__init__(self, 'Underworld', 5) 

	def canConquer(self, region, tokenBadge):
		if BaseSpecialPower.canConquer(self, region, tokenBadge):
			return True
		cav = False
		for reg in tokenBadge.regions:
			if hasattr(reg, 'cavern') and reg.cavern or \
					hasattr(reg, 'region') and reg.region.cavern:### For AI compatibility
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
