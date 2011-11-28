import httplib
import json
import threading
import time
import races


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
		self.visited = False
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
				self.tokensNum > 1 or self.inDecline))
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
	def __init__(self, id, raceName, specPowerName, owner, pos, bonusMoney, inDecline = None,
			totalTokensNum = None, specPowNum = None):
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

def createTokenBadge(tokenBadge, owner, declined):
	return TokenBadge(tokenBadge['tokenBadgeId'], tokenBadge['raceName'], 
		tokenBadge['specialPowerName'], owner, None, None, declined, tokenBadge['totalTokensNum'])
	
class AI(threading.Thread):
	def __init__(self, host, game, sid, id ):
		self.conn = httplib.HTTPConnection(host, timeout = 10000)
		self.gameId = game.id 
		self.conqueredRegions = list()
		self.dragon = None #regions
		self.enchant = None
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
				region.visited = False
				if 'currentRegionState' in data['gameState']['map']['regions'][i]:
					curState = data['gameState']['map']['regions'][i]['currentRegionState']
					for field in currentRegionFields:
						setattr(region, field, curState[field] if field in curState else None)
		tokenBadges = list()
		visibleBadges = gameState['visibleTokenBadges']
		for i, visibleBadge in enumerate(visibleBadges):
			tokenBadge = TokenBadge(0, visibleBadge['raceName'], visibleBadge['specialPowerName'],
				None, i, visibleBadge['bonusMoney'])
			tokenBadges.append(tokenBadge)
		tokenBadgesInGame = list()	
		for player in gameState['players']:
			if 'currentTokenBadge' in player:
				tokenBadge = createTokenBadge(player['currentTokenBadge'], player['id'], False)
				tokenBadgesInGame.append(tokenBadge);
				if player['id'] == self.id: self.currentTokenBadge = tokenBadge
			elif 'declinedTokenBadge' in player:
				tokenBadge = createTokenBadge(player['declinedTokenBadge'], player['id'], True)
				tokenBadgesInGame.append(tokenBadge);
				if player['id'] == self.id: self.declinedTokenBadge = tokenBadge
				
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
		maxTokensNum = 0
		bestTokens = list()

		for i, visibleBadge in enumerate(self.game.visibleTokenBadges):
			if self.coins >= 5 - i:
				if visibleBadge.race.maxNum + visibleBadge.specPower.tokensNum >= maxTokensNum:
					maxTokensNum = visibleBadge.race.maxNum + visibleBadge.specPower.tokensNum
					if visibleBadge.race.maxNum + visibleBadge.specPower.tokensNum > maxTokensNum:
						bestTokens = list()
					bestTokens.append({'tok': visibleBadge, 
						'num': visibleBadge.race.initialNum + visibleBadge.specPower.tokensNum})

		if not len(bestTokens):
			return False
		badge = sorted(bestTokens, key = lambda bestToken: bestToken['num'], reverse = True)[0]['tok']
		result = self.sendCmd({'action': 'selectRace', 'sid': self.sid, 'position': badge.pos})
		if result['result'] != 'ok':
			raise BadFieldException('unknown error in select race %s' % result['result'])
		return True
	
	def defend(self):
		defInfo = self.game.defendingInfo
		tokenBadge = self.currentTokenBadge
		tokensNum = defInfo['tokensNum']
		defRegion = self.game.map.getRegion(defInfo['regionId'])
		regionsToRetreat = tokenBadge.getRegions(defRegion) or tokenBadge.getRegions()
		calcDistances(self, regionsToRetreat)
		request = list()
		distributeUnits(borders, freeUnits, request)
		data = self.sendCmd({'action': 'defend', 'sid': self.sid, 
			'regions': convertRedeploymentRequest(request, REDEPLOYMENT_CODE)})
		if data['result'] != 'ok':
				raise BadFieldException('unknown error in defend: %s' % data['result'])
		
		
	def shouldDecline(self):
		return self.currentTokenBadge and self.currentTokenBadge.specPower.canDecline(self, False) and\
			self.game.checkStage(GAME_DECLINE, self) and\
			self.currentTokenBadge.totalTokensNum - len(self.currentTokenBadge.getRegions()) < 4

	def decline(self):
		data = self.sendCmd({'action': 'decline', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in decline %s' % data['result'])

	def shouldFinishTurn(self):
		return self.game.checkStage(GAME_FINISH_TURN, self)

	def finishTurn(self):
		data = self.sendCmd({'action': 'finishTurn', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in finish turn %s' % data['result'])
		self.conqueredRegions = list()
		self.dragon = None #regions
		self.enchant = None
		self.slaveId = None
	
	def shouldSelectFriend(self):
		f1 = self.game.checkStage(GAME_CHOOSE_FRIEND, self)
		f2 = not self.slaveId
		f3 = self.currentTokenBadge and self.currentTokenBadge.specPower.canSelectFriend()
		return f1 and f2 and f3

	def selectFriend(self):
		players = [player['id'] for player in self.game.players]
		for region in self.conqueredRegions:
			try:
				players.remove(region.owner)
			except:
				pass

		if len(players):
			data = self.sendCmd({'action': 'selectFriend', 'sid': self.sid, 
				'friendId': players[0]})
			if data['result'] != 'ok':
				raise BadFieldException('unknown error in select friend: %s' % data['result'])
			self.slaveId = players[0]

	def canConquer(self, region):
		f1 = region.ownerId != self.id or region.ownerId == self.id and region.inDecline
		f2 = not(self.masterId and self.masterId == region.ownerId)
		self.currentTokenBadge.regions = self.currentTokenBadge.getRegions()
		f3 = self.currentTokenBadge.race.canConquer(region, self.currentTokenBadge)
		f4 = self.currentTokenBadge.specPower.canConquer(region, self.currentTokenBadge)
		f5 = not region.isImmune(False)
		return f1 and f2 and f3 and f4 and f5

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
		regions = set(self.conquerableRegions)
		chosenRegion = None
		cur = None
		found = False
		for player in players:
			cur = filter(lambda x: x.ownerId == player['id'], regions)
			if len(cur): 
				chosenRegion = min(cur, key=lambda x: self.getRegionPrice(x))
				if self.tokensInHand >= self.getRegionPrice(chosenRegion):
					found = True
					break
		if not found: chosenRegion = min(regions, key=lambda x: self.getRegionPrice(x))
		chosenRegion.nonEmpty = chosenRegion.tokensNum > 0
		data = self.sendCmd({'action': 'conquer', 'sid': self.sid, 'regionId': chosenRegion.id})
		ok = data['result'] == 'ok'
		if ok: self.conqueredRegions.append(chosenRegion)
		if not(ok or data['result'] == 'badTokensNum'):
				raise BadFieldException('unknown error in conquer: %s' % data['result'])

	def canBeAttackedFromOutsideTheMap(self):
		return len(filter(lambda x: 'currentTokenBadge' not in x or\
			not len(self.game.getTokenBadgeById(x['currentTokenBadge']['tokenBadgeId']).getRegions()), 
				self.game.players))
		

	def redeploy(self):
		codeTable = {
			'heroes' :     HERO_CODE,
			'fortified' :  FORTRESS_CODE,
			'encampments' : ENCAMPMENTS_CODE
		};
		regions = self.currentTokenBadge.getRegions()
		calcDistances(self, regions)
		tokenBadge = self.currentTokenBadge
		freeUnits = tokenBadge.totalTokensNum + tokenBadge.race.turnEndReinforcements(self)
		req = {}
		redplReqName = tokenBadge.specPower.redeployReqName
		code = codeTable[redplReqName] if redplReqName in codeTable else None
		if code: req[redplReqName] = {}			
		for region in regions: 
			if code == ENCAMPMENTS_CODE:
				req['encampments'][region.id] = 0
			req[region.id] = 1
			freeUnits -= 1
		minDist = min(regions, key=lambda x: x.distFromEnemy).distFromEnemy
		borders = filter(lambda x: x.distFromEnemy == minDist, regions)
		if code == HERO_CODE:
			n = 2
			for reg in sorted(regions, key=lambda x: x.distFromEnemy):
				req['heroes'][reg.id] = 1
				n -= 1
				borders.remove(reg)
				if not n: break
		elif code == FORTRESS_CODE and len(filter(lambda x: x.fortified, regions)) < 6:
			reg = borders[0]
			req['fortified'][reg.id] = 1
			borders.remove(reg)
		distributeUnits(borders, freeUnits, req)
		if code == ENCAMPMENTS_CODE:
			distributeUnits(borders, 5, req['encampments'])
		redeployRequest = convertRedeploymentRequest(req, REDEPLOYMENT_CODE)
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
