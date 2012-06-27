import httplib
import json
import threading
import time
import races
import Queue
import misc_const

from copy import copy as copy
from misc_ai import *
from misc_const import *
from gameExceptions import BadFieldException
from operator import itemgetter

class Region:
	def __init__(self, id, adjacent, props, ownerId, tokenBadgeId, tokensNum, holeInTheGround,
		encampment, dragon, fortified, hero, inDecline):
		self.id = id
		self.adjacentIds = adjacent
		self.props = props
		self.ownerId = ownerId
		self.tokenBadgeId = tokenBadgeId
		self.tokensNum = tokensNum
		self.holeInTheGround = holeInTheGround
		self.encampment = encampment
		self.dragon = dragon
		self.fortified = fortified
		self.hero = hero
		self.distFromEnemy = 0
		self.inDecline = inDecline
		for prop in possibleLandDescription[:11]:
			setattr(self, prop, False)
		for prop in props:
			setattr(self, prop, True)

	def isAdjacent(self, region):
		return region.id in self.adjacentIds

	def isImmune(self, enchanting = False):
		return self.holeInTheGround or self.dragon or self.hero or\
			(enchanting and (self.encampment or not self.tokensNum or\
				self.tokensNum > 1 or self.inDecline or not self.tokenBadgeId))

	def isCoast(self):
		ans = False
		for reg in self.adjacent:
			if reg.sea:
				ans = True
				break
		return ans
		
class Map:
	def __init__(self, id, playersNum, turnsNum, regions):
		self.id = id
		self.playersNum = playersNum
		self.turnsNum = turnsNum
		self.regions = regions
		for region in self.regions:
			region.adjacent = map(lambda x: self.getRegion(x), region.adjacentIds)

	def getRegion(self, id):
		for region in self.regions:
			if region.id == id:
				return region

	def adjacent_(self, reg, badge):
		return reg.adjacent + (filter(lambda x: x.cavern and x.id != reg.id, self.regions) if 	reg.cavern and badge.specPower.name == 'Underworld' else list())

class Game:
	def __init__(self, id, tokenBadgesInGame, 
					map_, state, turn, activePlayerId, visibleTokenBadges, players):
		self.id = id
		self.tokenBadgesInGame = tokenBadgesInGame
		self.map = map_
		self.state = state
		self.turn = turn
		self.activePlayerId = activePlayerId
		self.visibleTokenBadges = visibleTokenBadges
		self.players = map(lambda x: Player(**x), players)
		
	def checkStage(self, state, ai, attackType = None):
		lastEvent = self.state
		badStage = not (lastEvent in possiblePrevCmd[state]) 
		if attackType:
			badStage = badStage and ai.badAttack(attackType)
		return not badStage

	def getLastState(self):
		return self.state

	def getTokenBadgeById(self, id):
		res = filter(lambda x: x.id == id, self.tokenBadgesInGame)
		return res[0] if len(res) else None

	def getUserInfo(self, id):
		res = filter(lambda x: x['userId'] == id, self.players)
		return res[0] if len(res) else None

	
class TokenBadge:
	def __init__(self, id, raceName, specPowerName, pos, bonusMoney, inDecline = None,
			totalTokensNum = None, specPowNum = None, owner = None):
		self.id = id
		self.owner = owner
		for race in races.racesList:
			if race.name == raceName:
				self.race = race
				break
		for specPower in races.specialPowerList:
			if specPower.name == specPowerName:
				self.specPower = specPower
				break
		self.pos = pos
		self.bonusMoney = bonusMoney
		self.inDecline = inDecline
		self.totalTokensNum = totalTokensNum or (self.race.initialNum + self.specPower.tokensNum)
		self.specPowNum = specPowNum

	def getRegions(self, defReg = None):
		return filter(lambda x: x.tokenBadgeId == self.id and (not defReg or not x.isAdjacent(defReg)),
			self.game.map.regions)
		
	def isNeighbor(self, region):
		return len(filter(lambda x: x.isAdjacent(region), self.getRegions())) > 0

	def characteristic(self):
		return self.race.initialNum + self.specPower.tokensNum + self.race.turnStartReinforcements()

	def regBonus(self, reg):
		return 1 + self.race.regBonus(reg) + self.specPower.regBonus(reg)

currentRegionFields = ['ownerId', 'tokenBadgeId', 'tokensNum', 'holeInTheGround', 
	'encampment', 'dragon', 'fortified', 'hero', 'inDecline']

def createMap(mapState):
	regions = list()
	for i, region in enumerate(mapState['regions']):
		curReg = list()
		if 'currentRegionState' in region:
			curState = region['currentRegionState']
			for field in currentRegionFields:
				curReg.append(curState[field] if field in curState else None)
		regions.append(Region(i + 1, region['adjacentRegions'], region['constRegionState'], 
			*curReg))
	return Map(mapState['mapId'], mapState['playersNum'], mapState['turnsNum'], regions)

def createTokenBadge(tokenBadge, declined, owner=None):
	return TokenBadge(tokenBadge['tokenBadgeId'], tokenBadge['raceName'], 
		tokenBadge['specialPowerName'], None, None, declined, tokenBadge['totalTokensNum'], owner)

class Player:
	def __init__(self, **entries): 
		self.__dict__.update(entries)
	
class AI(threading.Thread):
	def __init__(self, host, url, gameId, sid, id, logFile):
		self.conn = httplib.HTTPConnection(host, timeout = 10000)
		self.url = url
		self.gameId = gameId 
		self.conqueredRegions = list()
		self.dragonUsed = False 
		self.enchantUsed = False
		self.friendId = None
		self.sid = sid
		self.id = id
		self.logFile = logFile
		self.game = None
		self.conquestStrategies = None
		self.currentTokenBadge = None
		self.declinedTokenBadge = None
		threading.Thread.__init__(self)
		self.start()
		
	def sendCmd(self, obj):
		self.conn.request("POST", self.url, json.dumps(obj))
		r1 = self.conn.getresponse()
		res = r1.read()
		print 'cmd', obj
	#	print 'res', res
		data = json.loads(res)
		if not 'result' in data:
			print data
			raise BadFieldException('Unknown result')
		if (data['result'] in ('badJson', 'badReadinessStatus', 'badUserSid', 
			'badGameId', 'badMapId', 'badPosition', 'badFriendId', 'badRegionId')):
			print obj, 'req'
			raise BadFieldException(data['result'])
		return data

	def getGameState(self):
		data = self.sendCmd({'action': 'getGameState', 'gameId': self.gameId})
		gameState = data['gameState']
		if gameState['state'] == GAME_ENDED:
			self.game.state = GAME_ENDED
			return
		map_ = None
		if not self.game:
			map_ = createMap(data['gameState']['map'])
		else:
			for i, region in enumerate(self.game.map.regions):
				region.inDanger = False
				if 'currentRegionState' in data['gameState']['map']['regions'][i]:
					curState = data['gameState']['map']['regions'][i]['currentRegionState']
					for field in currentRegionFields:
						setattr(region, field, curState[field] if field in curState else None)
		tokenBadges = list()
		visibleBadges = gameState['visibleTokenBadges']
		for i, visibleBadge in enumerate(visibleBadges):
			tokenBadge = TokenBadge(0, visibleBadge['raceName'], visibleBadge['specialPowerName'],
				i, visibleBadge['bonusMoney'])
			tokenBadges.append(tokenBadge)
		tokenBadgesInGame = list()	
		self.currentTokenBadge = None
		self.declinedTokenBadge = None
		for player in gameState['players']:
			if 'currentTokenBadge' in player:
				tokenBadge = createTokenBadge(player['currentTokenBadge'], False, player['userId'])
				player['currentTokenBadge'] = tokenBadge
				tokenBadgesInGame.append(tokenBadge);
				if player['userId'] == self.id: self.currentTokenBadge = tokenBadge
			else:
				player['currentTokenBadge'] = None
				
			if 'declinedTokenBadge' in player:
				tokenBadge = createTokenBadge(player['declinedTokenBadge'], True, player['userId'])
				player['declinedTokenBadge'] = tokenBadge
				tokenBadgesInGame.append(tokenBadge);
				if player['userId'] == self.id: self.declinedTokenBadge = tokenBadge
			else:
				player['declinedTokenBadge'] = None
			
			if player['userId'] == self.id:
				self.coins = player['coins']
				self.tokensInHand = player['tokensInHand']
				self.priority = player['priority']
				self.enchantUsed = gameState['enchanted']
				self.dragonUsed = gameState['dragonAttacked']

		if not self.game:
			self.game = Game(gameState['gameId'], tokenBadgesInGame, map_, 
				gameState['lastEvent'] if (gameState['state'] != GAME_WAITING) else gameState['state'],
				gameState['currentTurn'], gameState['activePlayerId'], tokenBadges, gameState['players'])
		else:
			self.game.visibleTokenBadges = tokenBadges
			self.game.tokenBadgesInGame = tokenBadgesInGame
			self.game.players = map(lambda x: Player(**x), gameState['players'])
			self.game.activePlayerId = gameState['activePlayerId']
			self.game.state = gameState['lastEvent'] if gameState['state'] != GAME_WAITING else gameState['state']
			self.game.turn = gameState['currentTurn']
		self.game.defendingInfo = gameState['defendingInfo'] if 'defendingInfo' in gameState else None
		if 'friendsInfo' in gameState and 'friendId' in gameState['friendsInfo'] and\
				gameState['friendsInfo']['friendId']== self.id:
				self.masterId = gameState['friendsInfo']['diplomatId']
		else:
			self.masterId = None 

		for tokenBadge in self.game.tokenBadgesInGame + self.game.visibleTokenBadges:
			tokenBadge.game = self.game
			
	def selectRace(self):
		visibleBadges = self.game.visibleTokenBadges
		chosenBadge = max(filter(lambda x: self.coins >= x.pos, visibleBadges), 
				key=lambda x: x.characteristic())
		result = self.sendCmd({'action': 'selectRace', 'sid': self.sid, 'position': chosenBadge.pos})
		if result['result'] != 'ok':
			raise BadFieldException('unknown error in select race %s' % result['result'])
		return True


	
	def defend(self):
		defInfo = self.game.defendingInfo
		tokenBadge = self.currentTokenBadge
		defRegion = self.game.map.getRegion(defInfo['regionId'])
		regionsToRetreat = tokenBadge.getRegions(defRegion) or tokenBadge.getRegions()
		self.calcDistances(regionsToRetreat)
		request = {}
		for region in regionsToRetreat: request[region.id] = 0
		distributeUnits(regionsToRetreat, self.tokensInHand, request)
		data = self.sendCmd({'action': 'defend', 'sid': self.sid, 
			'regions': convertRedeploymentRequest(request, REDEPLOYMENT_CODE)})
		if data['result'] != 'ok':
				raise BadFieldException('unknown error in defend: %s' % data['result'])
		
		
	def shouldDecline(self):
		tBadge = self.currentTokenBadge
		return tBadge and tBadge.specPower.canDecline(self, False) and\
			self.game.checkStage(GAME_DECLINE, self) and\
				(not len (self.getConquerableRegions()) or\
				tBadge.totalTokensNum - len(tBadge.getRegions()) < 4)
	def decline(self):
		data = self.sendCmd({'action': 'decline', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in decline %s' % data['result'])

	def enchant(self):
		data = self.sendCmd({'action': 'enchant', 'sid': self.sid, 
			'regionId': self.enchantableRegions[0].id})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in enchant %s' % data['result'])
		self.enchantUsed = True

	def dragonAttack(self):
		region = max(self.conquerableRegions, key=lambda x: x.tokensNum)
		data = self.sendCmd({'action': 'dragonAttack', 'sid': self.sid, 'regionId': region.id})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in dragon attack %s' % data['result'])
		self.dragonUsed = True

	def shouldFinishTurn(self):
		return self.game.checkStage(GAME_FINISH_TURN, self)

	def finishTurn(self):
		data = self.sendCmd({'action': 'finishTurn', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in finish turn %s' % data['result'])
		result = ''
		if 'ended' in data: #game ended
			result += '***FINISH GAME***\n'
			result += 'Game id: %d\n' % self.game.id
			statistics = data['statistics']
			statistics = sorted(statistics, key = itemgetter('coins', 'regions'), 
				reverse = True)
			for stat in statistics:
				result += 'Name: %s, coins: %d, regions: %d\n' % (stat['name'], 
					stat['coins'], stat['regions'])
			result += '**************\n'
		else:
			result = 'Game id: %d, turn: %d\n' % (self.game.id, self.game.turn)
			result += 'Player id: %d\n' % self.id
			result += 'Statistics: \n'
			totalCoins = 0
			for statistics in data['statistics']:
				result += '%s: %d\n' % (statistics[0], statistics[1])
				totalCoins += statistics[1]
			result += 'Income coins: %d\n\n\n' % totalCoins
		self.logFile.write(result)
		self.conqueredRegions = list()
		self.dragonUsed = False #regions
		self.enchantUsed = False
		self.friendId = None
		self.conqPlans = None

	def canSelectFriend(self):
		return not self.friendId and self.currentTokenBadge.specPower.canSelectFriend()
	
	def shouldSelectFriend(self):
		if self.game.checkStage(GAME_CHOOSE_FRIEND, self) and self.canSelectFriend():
			players = filter(lambda x: x.userId != self.id, 
				self.game.players)
			for region in self.conqueredRegions:
				for player in players:
					if region.ownerId == player.userId:
						players.remove(player)
			self.friendCandidates = players
			return len(players)
		return False

	def selectFriend(self):
		best = 0
		bestCand = None
		bestCand = max(self.friendCandidates, 
				key=lambda x: x.currentTokenBadge and x.currentTokenBadge.totalTokensNum)
						
		chosenPlayer = bestCand.userId if bestCand else self.friendCandidates[0].userId
		data = self.sendCmd({'action': 'selectFriend', 'sid': self.sid, 
			'friendId': chosenPlayer})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in select friend: %s' % data['result'])
		self.friendId = chosenPlayer

	def canConquer(self, region, badge=None, code=0):
		tBadge = badge or self.currentTokenBadge
		f1 = (code & 0x1) or (region.ownerId != self.id or region.ownerId == self.id and region.inDecline)
		f2 = (code & 0x2) or not(self.masterId and self.masterId == region.ownerId)
		f3 = (code & 0x4) or tBadge.race.canConquer(region, tBadge)
		f4 = (code & 0x8) or tBadge.specPower.canConquer(region, tBadge)
		f5 = (code & 0x10) or not region.isImmune(False)
		return f1 and f2 and f3 and f4 and f5

	def canThrowDice(self):
		return self.currentTokenBadge.specPower.canThrowDice() and\
			self.game.checkStage(GAME_THROW_DICE, self)

	def canUseDragon(self, badge=None):
		tBadge = badge or self.currentTokenBadge
		return tBadge.specPower.canUseDragon() and not self.dragonUsed and\
			self.tokensInHand > 0 and\
			not len(filter(lambda x: x.dragon, tBadge.getRegions()))

	def getConquerableRegions(self, badge=None):
		tBadge = badge or self.currentTokenBadge
		if not(badge or (self.game.checkStage(GAME_CONQUER, self) and self.tokensInHand)):
			return list()
		tBadge.regions = tBadge.getRegions()
		return filter(lambda x: self.canConquer(x, tBadge), self.game.map.regions)
	
	def getRegionPrice(self, reg, badge):
		tokenBadge = self.game.getTokenBadgeById(reg.tokenBadgeId)
		enemyDefense = tokenBadge.race.defenseBonus() if tokenBadge else 0
		return max(BASIC_CONQUER_COST + reg.encampment +  
			reg.fortified + reg.tokensNum + reg.mountain + enemyDefense +
			badge.race.attackBonus(reg, badge) + 
			badge.specPower.attackBonus(reg, badge), 1)

	def getRegions(self):
		return filter(lambda x: x.ownerId == self.id, self.game.map.regions)
	
	def getNonEmptyConqueredRegions(self):
		return len(filter(lambda x: x.nonEmpty,  self.conqueredRegions))

	def conquer(self):
		regions = self.conquerableRegions
		calcRegPrior = lambda x: self.getRegionPrice(x, self.currentTokenBadge) + 5*(x.ownerId == self.id) - self.currentTokenBadge.regBonus(x)
		self.calcDistances(regions)
		if self.currentTokenBadge and len(self.currentTokenBadge.getRegions()) and\
				not len(filter(lambda x : x.distFromEnemy < 2, self.currentTokenBadge.getRegions())):
			chosenRegion = min(regions, key=lambda x: calcRegPrior(x) - int(x.tokenBadgeId or 0))
		else:
			farawayRegs = filter(lambda x: x.distFromEnemy > 2, regions)
			chosenRegion = min(farawayRegs if len(farawayRegs) else regions, key=calcRegPrior)
		conqdReg = copy(chosenRegion)
		conqdReg.nonEmpty = chosenRegion.tokensNum > 0
		if self.canThrowDice(): self.sendCmd({'action': 'throwDice', 'sid': self.sid})
		data = self.sendCmd({'action': 'conquer', 'sid': self.sid, 'regionId': chosenRegion.id})
		if data['result'] not in ['ok', 'badTokensNum']:	
			raise BadFieldException('unknown error in conquer: %s' % res)
		self.conqueredRegions.append(conqdReg)	
	

			

	def invadersExist(self):
		return len(filter(lambda x: x.userId != self.id and (currentTokenBadge not in x or\
			not len(self.game.getTokenBadgeById(x.currentTokenBadge.tokenBadgeId).getRegions())), 
				self.game.players))


	def needDefendAgainst(self, abilityName, isRace):
		key = lambda x: x and (abilityName == x.race.name if isRace else x.specPower.name)
		return len(filter(key, map(lambda x: x.currentTokenBadge, self.game.players))) > 0 or\
				(len(filter(lambda x: x.currentTokenBadge, self.game.players) > 0) and\
					(len(filter(key, self.game.visibleTokenBadges) > 0)))
		
					
	def calcDistances(self, regions):
		if self.needDefendAgainst('Flying', False):
			for reg in self.currentTokenBadge.getRegions():
				reg.needDef = 1
			return
		hobbitsAreEnemies =  self.needDefendAgainst(mdPlayer, 'Hobbits', True)
		dangerous = lambda x: x.ownerId and not x.inDecline and x.ownerId not in (self.id, self.friendId)
		for region in regions:
			if invaders and (region.border or hobbitsAreEnemies):
				region.distFromEnemy = 1
				continue
			for reg in self.game.map.regions: reg.d = 0
			q = Queue()
			cur = None
			q.put(region)
			region.d = 1
			stop = False
			while not (q.empty() or stop):              
				cur = q.get()
				for reg in self.game.map.adjacent_(cur, badge):
					if reg.d: continue
					if dangerous(reg):
						stop = True
						break
					reg.d = cur.d + 1
					q.put(reg)
			region.distFromEnemy = cur.d
		maxDist = max(regions, key=lambda x: x.distFromEnemy).distFromEnemy
		for reg in self.currentTokenBadge.getRegions():
			if reg.dragon or reg.holeInTheGround or reg.fortified  or reg.sea:
				reg.needDef = 1
			else:
				reg.needDef = maxDist - reg.distFromEnemy + 1
			reg.needDef += self.currentTokenBadge.regBonus(reg) 
			reg.needDef += self.declinedTokenBadge.regBonus(reg) if self.declinedTokenBadge else 0
			
	

	def redeploy(self):
		codeTable = {
			'heroes' :     HERO_CODE,
			'fortified' :  FORTRESS_CODE,
			'encampments' : ENCAMPMENTS_CODE
		};
		regions = self.currentTokenBadge.getRegions()
		tokenBadge = self.currentTokenBadge
		freeUnits = tokenBadge.totalTokensNum + tokenBadge.race.turnEndReinforcements(self)
		req = {'redeployment' : {}}
		redplReqName = tokenBadge.specPower.redeployReqName
		code = codeTable[redplReqName] if redplReqName in codeTable else None
		if code: req[redplReqName] = {}			
		for region in regions: 
			if code == ENCAMPMENTS_CODE:
				req['encampments'][region.id] = 0
			req['redeployment'][region.id] = 1
			freeUnits -= 1
		self.calcDistances(regions)
		if code == HERO_CODE:
			n = 2
			for reg in sorted(regions, key=lambda x: x.needDef):
				req['heroes'][reg.id] = 1
				n -= 1
				reg.needDef = 1
				if not n: break
		elif code == FORTRESS_CODE and len(filter(lambda x: x.fortified, regions)) < 6:
			maxNeedDef = 0
			reg = None
			for region in regions:
				if region.needDef > maxNeedDef and not region.fortified:
					reg = region
					maxNeedDef = region.needDef
			if reg:
				req['fortified'][reg.id] = 1
				reg.needDef = 1
		if freeUnits:
			distributeUnits(regions, freeUnits, req['redeployment'])
		if code == ENCAMPMENTS_CODE:
			distributeUnits(regions, 5, req['encampments'])
		redeployRequest = convertRedeploymentRequest(req['redeployment'], REDEPLOYMENT_CODE)
		cmd = {'action': 'redeploy', 'sid': self.sid, 'regions': redeployRequest}
		if code: 
			cmd[redplReqName] = convertRedeploymentRequest(req[redplReqName], code)
		data = self.sendCmd(cmd)
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in redeploy %s' % data['result'])

	def getNextAct(self):
		defendingPlayer = self.game.defendingInfo['playerId'] if self.game.defendingInfo else None
		if self.id == defendingPlayer:
			return self.defend
		if not self.currentTokenBadge and self.game.checkStage(GAME_SELECT_RACE, self):
			return self.selectRace
		if self.shouldDecline():
			return self.decline
		if self.shouldSelectFriend():
			return self.selectFriend
		if self.currentTokenBadge:
			self.conquerableRegions = self.getConquerableRegions()
			if self.game.state == GAME_UNSUCCESSFULL_CONQUER or\
				(not len(self.conquerableRegions) and self.game.checkStage(GAME_REDEPLOY, self)):
				return self.redeploy
			if self.canUseDragon():
				return self.dragonAttack
			if self.currentTokenBadge.race.canEnchant() and not self.enchantUsed:
				self.enchantableRegions = filter(lambda x: not x.isImmune(True), self.conquerableRegions)
				if len(self.enchantableRegions):
					return self.enchant
			if self.game.checkStage(GAME_CONQUER, self):
				return self.conquer
		return self.finishTurn

	def run(self):
		time.sleep(10)
		while True:
			self.getGameState()
			if self.game.state == GAME_ENDED:
				if not self.logFile.closed: self.logFile.close()
				break
			activePlayer = self.game.activePlayerId
			defendingPlayer = self.game.defendingInfo['playerId'] if self.game.defendingInfo else None
			if self.game.state == GAME_WAITING or not (self.id in (activePlayer, defendingPlayer)) or\
				(self.id == activePlayer and defendingPlayer):
				time.sleep(1)
				continue
			self.getNextAct()()
