import httplib
import json
import threading
import time
import races
import Queue

from copy import copy as copy
from misc_ai import *
from misc import *
from gameExceptions import BadFieldException

class Region:
	def __init__(self, id, adjacent, props, ownerId, tokenBadgeId, tokensNum, holeInTheGround,
		encampment, dragon, fortress, hero, inDecline):
		self.id = id
		self.adjacentIds = adjacent
		self.props = props
		self.ownerId = ownerId
		self.tokenBadgeId = tokenBadgeId
		self.tokensNum = tokensNum
		self.holeInTheGround = holeInTheGround
		self.encampment = encampment
		self.dragon = dragon
		self.fortress = fortress
		self.hero = hero
		self.inDanger = False
		self.inDecline = inDecline
		for prop in possibleLandDescription[:11]:
			setattr(self, prop, False)
		for prop in props:
			setattr(self, prop, True)

	def isAdjacent(self, region):
		return region.id in map(lambda x: x, self.adjacentIds) 

	def isImmune(self, enchanting = False):
		return self.holeInTheGround or self.dragon or self.hero or\
			(enchanting and (self.encampment or not self.tokensNum or\
				self.tokensNum > 1 or self.inDecline or not self.tokenBadgeId))
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
		self.players = players
		
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
		return res[0] if res else None

	
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
		self.totalTokensNum = totalTokensNum
		self.specPowNum = specPowNum

	def getRegions(self, defReg = None):
		return filter(lambda x: x.tokenBadgeId == self.id and (not defReg or not x.isAdjacent(defReg)),
			self.game.map.regions)
		
	def isNeighbor(self, region):
		return len(filter(lambda x: x.isAdjacent(region), self.getRegions())) > 0

	def characteristic(self):
		return self.race.initialNum + self.specPower.tokensNum + self.race.turnStartReinforcements()
	

currentRegionFields = ['ownerId', 'tokenBadgeId', 'tokensNum', 'holeInTheGround', 
	'encampment', 'dragon', 'fortress', 'hero', 'inDecline']

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
	
class AI(threading.Thread):
	def __init__(self, host, game, sid, id ):
		self.conn = httplib.HTTPConnection(host, timeout = 10000)
		self.gameId = game.id 
		self.conqueredRegions = list()
		self.dragonUsed = False #regions
		self.enchantUsed = False
		self.slaveId = None
		self.sid = sid
		self.id = id
		self.game = None
		self.currentTokenBadge = None
		self.declinedTokenBadge = None
		threading.Thread.__init__(self)
		self.start()
		
	def sendCmd(self, obj):
		self.conn.request("POST", "/ajax", json.dumps(obj))
		r1 = self.conn.getresponse()
		res = r1.read()
		data = json.loads(res)
		if not 'result' in data:
			raise BadFieldException('Unknown result')
		if (data['result'] in ('badJson', 'badReadinessStatus', 'badUserSid', 
			'badGameId', 'badMapId', 'badPosition', 'badFriendId', 'badRegionId')):
			raise BadFieldException(data['result'])
		return data

	def getGameState(self):
		data = self.sendCmd({'action': 'getGameState', 'gameId': self.gameId})
		gameState = data['gameState']
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
		for player in gameState['players']:
			if 'currentTokenBadge' in player:
				tokenBadge = createTokenBadge(player['currentTokenBadge'], False, player['id'])
				tokenBadgesInGame.append(tokenBadge);
				if player['id'] == self.id: self.currentTokenBadge = tokenBadge
			else: 
				self.currentTokenBadge = None
			if 'declinedTokenBadge' in player:
				tokenBadge = createTokenBadge(player['declinedTokenBadge'], True, player['id'])
				tokenBadgesInGame.append(tokenBadge);
				if player['id'] == self.id: self.declinedTokenBadge = tokenBadge
			else: 
				self.declinedTokenBadge = None				
			if player['id'] == self.id:
				self.coins = player['coins']
				self.tokensInHand = player['tokensInHand']
				self.priority = player['priority']

		if not self.game:
			self.game = Game(gameState['gameId'], tokenBadgesInGame, map_, 
				gameState['lastEvent'] if (gameState['state'] == GAME_START) else gameState['state'],
				gameState['currentTurn'], gameState['activePlayerId'], tokenBadges, gameState['players'])
		else:
			self.game.visibleTokenBadges = tokenBadges
			self.game.tokenBadgesInGame = tokenBadgesInGame
			self.game.players = gameState['players']
			self.game.activePlayerId = gameState['activePlayerId'];
			self.game.state = gameState['lastEvent'] if gameState['state'] == GAME_START else gameState['state'];
		self.game.defendingInfo = gameState['defendingInfo'] if 'defendingInfo' in gameState else None
		if 'friendsInfo' in gameState and 'slaveId' in gameState['friendsInfo'] and\
				gameState['friendsInfo']['slaveId']== self.id:
				self.masterId = gameState['friendsInfo']['masterId']
		else:
			self.masterId = None 

		for tokenBadge in self.game.tokenBadgesInGame:
			tokenBadge.game = self.game
			
	def selectRace(self):
		visibleBadges = self.game.visibleTokenBadges
		chosenBadge = max(filter(lambda x: self.coins >= 5 - x.pos, visibleBadges), 
				key=lambda x: x.characteristic())
		result = self.sendCmd({'action': 'selectRace', 'sid': self.sid, 'position': chosenBadge.pos})
		if result['result'] != 'ok':
			raise BadFieldException('unknown error in select race %s' % result['result'])
		return True
	
	def defend(self):
		defInfo = self.game.defendingInfo
		tokenBadge = self.currentTokenBadge
		tokensNum = defInfo['tokensNum']
		defRegion = self.game.map.getRegion(defInfo['regionId'])
		regionsToRetreat = tokenBadge.getRegions(defRegion) or tokenBadge.getRegions()
		self.findRegionsInDanger(regionsToRetreat)
		request = {}
		for region in regionsToRetreat: request[region.id] = 0
		distributeUnits(regionsToRetreat, tokensNum, request)
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
		result = 'Game: %d, turn: %d\n' % (self.gameState.id, self.gameState.turn)
		result += 'Players: %d\n' % self.id
		result += 'Income coins: %d\n' % (data['incomeCoins'] if 'incomeCoins' in data else 0)
		result += 'Statistics: \n'
		for statistics in data['statistics']:
			result += '%s: %d\n' % (statistics[0], statistics[1])
		result += 'Total coins number: %d\n\n\n' % data['coins']
		LOG_FILE.write(result)
		self.conqueredRegions = list()
		self.dragonUsed = False #regions
		self.enchantUsed = False
		self.slaveId = None

	def canSelectFriend(self):
		return not self.slaveId and self.currentTokenBadge.specPower.canSelectFriend()
	
	def shouldSelectFriend(self):
		if self.game.checkStage(GAME_CHOOSE_FRIEND, self) and self.canSelectFriend():
			players = filter(lambda x: x != self.id, map(lambda x: x['id'], self.game.players))
			for region in self.conqueredRegions:
				if region.ownerId in players: 
					players.remove(region.ownerId)
			self.friendCandidates = players
			return len(players)
		return False

	def selectFriend(self):
		chosenPlayer = max(self.friendCandidates, key=lambda x: x.totalTokensNum) 
		data = self.sendCmd({'action': 'selectFriend', 'sid': self.sid, 
			'friendId': chosenPlayer})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in select friend: %s' % data['result'])
		self.slaveId = chosenPlayer

	def canConquer(self, region):
		f1 = region.ownerId != self.id or region.ownerId == self.id and region.inDecline
		f2 = not(self.masterId and self.masterId == region.ownerId)
		self.currentTokenBadge.regions = self.currentTokenBadge.getRegions()
		f3 = self.currentTokenBadge.race.canConquer(region, self.currentTokenBadge)
		f4 = self.currentTokenBadge.specPower.canConquer(region, self.currentTokenBadge)
		f5 = not region.isImmune(False)
		f6 = self.tokensInHand > 0
		return f1 and f2 and f3 and f4 and f5

	def canThrowDice(self):
		return self.currentTokenBadge.specPower.canThrowDice() and\
			self.game.checkStage(GAME_THROW_DICE, self)

	def canUseDragon(self):
		return self.currentTokenBadge.specPower.canUseDragon() and not self.dragonUsed and\
			self.tokensInHand > 0 and\
			not len(filter(lambda x: x.dragon, self.currentTokenBadge.getRegions()))


	def getConquerableRegions(self):
		result = list()
		if not(self.game.checkStage(GAME_CONQUER, self) and self.currentTokenBadge and self.tokensInHand):
			return result
		for region in self.game.map.regions:
			if self.canConquer(region):
				result.append(region)
		return result

	
	def getRegionPrice(self, reg):
		tokenBadge = self.game.getTokenBadgeById(reg.tokenBadgeId)
		enemyDefense = tokenBadge.race.defenseBonus() if tokenBadge else 0
		return max(BASIC_CONQUER_COST + reg.encampment + reg.fortress +
			reg.encampment + reg.fortress + reg.tokensNum + reg.mountain + enemyDefense +
			self.currentTokenBadge.race.attackBonus(reg, self.currentTokenBadge) + 
			self.currentTokenBadge.specPower.attackBonus(reg, self.currentTokenBadge), 1)

	def getNonEmptyConqueredRegions(self):
		return len(filter(lambda x: x.nonEmpty,  self.conqueredRegions))

	def conquer(self):
		players = sorted(self.game.players, key=lambda x: x['coins'])
		regions = self.conquerableRegions
		chosenRegion = None
		cur = None
		found = False
		for player in players:
			cur = filter(lambda x: x.ownerId == player['id'], regions)
			if len(cur): 
				chosenRegion = min(cur, key=lambda x: self.getRegionPrice(x))
				if self.tokensInHand * 1.5  > self.getRegionPrice(chosenRegion):
					found = True
					break
		if not found: chosenRegion = min(regions, key=lambda x: self.getRegionPrice(x))
		conqdReg = copy(chosenRegion)
		conqdReg.nonEmpty = chosenRegion.tokensNum > 0
		self.conqueredRegions.append(conqdReg)
		if self.canThrowDice(): self.sendCmd({'action': 'throwDice', 'sid': self.sid})
		data = self.sendCmd({'action': 'conquer', 'sid': self.sid, 'regionId': chosenRegion.id})
		ok = data['result'] == 'ok'
		if not(ok or data['result'] == 'badTokensNum'):
				raise BadFieldException('unknown error in conquer: %s' % data['result'])

	def invadersExist(self):
		return len(filter(lambda x: 'currentTokenBadge' not in x or\
			not len(self.game.getTokenBadgeById(x['currentTokenBadge']['tokenBadgeId']).getRegions()), 
				self.game.players))

	def mostDangerousPlayer(self):
		theKey = lambda x: x['currentTokenBadge']['totalTokensNum'] if 'currentTokenBadge' in x else 0
		return max(filter(lambda x: x['id'] not in (self.id, self.slaveId), self.game.players), key=theKey)
			

	def needDefendAgainst(self, mdPlayer, abilityName, race):
		return (len(self.game.players)== 2 and\
				not 'currentTokenBadge' in 
					filter(lambda x: x['id'] != self.id, self.game.players)[0] and\
				len(filter(lambda x: (x.race.name if race else x.specPower.name) == abilityName, 
					self.game.visibleTokenBadges))) or\
			mdPlayer and\
			'currentTokenBadge' in mdPlayer and\
			mdPlayer['currentTokenBadge']['raceName' if race else 'specialPowerName'] == abilityName
					
	def findRegionsInDanger(self, regions):
		dangerous = lambda x: x.ownerId and not x.inDecline and x.ownerId not in (self.id, self.slaveId)
		invaders = self.invadersExist()
		mdPlayer = self.mostDangerousPlayer()
		hobbitsAreEnemies =  self.needDefendAgainst(mdPlayer, 'Hobbits', True)
		for region in regions:
			if invaders and (region.border or hobbitsAreEnemies):
				region.inDanger = True
				continue				
			for reg in region.adjacent:
				if dangerous(reg):
					region.inDanger = True
					break
		
		if mdPlayer:
			if self.needDefendAgainst(mdPlayer, 'Underworld', False):
				if not mdPlayer['currentTokenBadge'] or\
					len(filter(lambda x: x.ownerId == mdPlayer['id'] and\
							not x.inDecline and\
							x.cavern, 
						self.game.map.regions)):
					for region in regions:
						if region.cavern: region.inDanger = True
			elif self.needDefendAgainst(mdPlayer, 'Flying', False):
				for region in regions: region.inDanger = not region.inDanger
		

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
		self.findRegionsInDanger(regions)
		borders = filter(lambda x: x.inDanger and not x.dragon and not x.holeInTheGround, regions)
		if code == HERO_CODE:
			n = 2
			for reg in sorted(regions, key=lambda x: int(x.inDanger), reverse=True):
				req['heroes'][reg.id] = 1
				n -= 1
				if reg in borders:
					borders.remove(reg)
				if not n: break
		elif code == FORTRESS_CODE and len(filter(lambda x: x.fortress, regions)) < 6:
			reg = borders[0]
			req['fortified'][reg.id] = 1
			borders.remove(reg)
		if freeUnits:
			distributeUnits(borders if len(borders) else regions, freeUnits, req['redeployment'])
		if code == ENCAMPMENTS_CODE:
			distributeUnits(borders, 5, req['encampments'])
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
			activePlayer = self.game.activePlayerId
			defendingPlayer = self.game.defendingInfo['playerId'] if self.game.defendingInfo else None
			if self.game.state == GAME_WAITING or not (self.id in (activePlayer, defendingPlayer)) or\
				(self.id == activePlayer and defendingPlayer):
				time.sleep(5)
				continue
			self.getNextAct()()
