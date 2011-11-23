import httplib
import json
import threading
import time
import races

from misc import *
from gameExceptions import BadFieldException

class Region:
	def __init__(self, id, adjacent, props, ownerId, tokenBadgeId, tokensNum, holeInTheGround,
		encampment, dragon, fortress, hero, inDecline):
		self.id = id
		self.adjacent = adjacent
		self.props = props
		self.ownerId = ownerId
		self.tokenBadgeId = tokenBadgeId
		self.tokensNum = tokensNum
		self.holeInTheGround = holeInTheGround
		self.encampment = encampment
		self.dragon = dragon
		self.fortress = fortress
		self.hero = hero
		self.inDecline = inDecline
		for prop in props:
			setattr(self, prop, True)

	def isAdjacent(self, region):
		return region.id in self.adjacent 

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

	def getRegion(self, id):
		for region in self.regions:
			if region.id == id:
				return region
				

class Game:
	def __init__(self, id, map, state, turn, activePlayerId, visibleTokenBadges, players):
		self.id = id
		self.map = map
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
		return badStage

class TokenBadge:
	def __init__(self, id, raceName, specPowerName, pos, bonusMoney, inDecline = None,
			totalTokensNum = None, specPowNum = None):
		self.id = id
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

	def getRegions(self, game):
		result = list()
		for region in game.map.regions:
			if region.tokenBadgeId == self.id:
				result.append(region)
		return result


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
	return Map(mapState['mapId'], mapState['playersNum'], mapState['turnsNum'], regions);

def createTokenBadge(tokenBadge, declined):
	return TokenBadge(tokenBadge.id, tokenBadge.raceName, tokenBadge.specialPowerName,
				None, None, declined, tokenBadge.totalTokensNum)
	
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
		self.gameState = None
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
		map = None
		if not self.gameState:
			map = createMap(data['gameState']['map'])
		else:
			regions = list()
			for i, region in enumerate(data['gameState']['map']):
				curReg = list()
				if 'currentRegionState' in region:
					curState = region['currentRegionState']
					for field in currentRegionFields:
						region[field] = curState[field] if field in curState else None
				regions.append(region)
			self.gameState.map.regions = regions
		
		tokenBadges = list()
		visibleBadges = gameState['visibleTokenBadges']
		for visibleBadge in visibleBadges:
			tokenBadge = TokenBadge(0, visibleBadge['raceName'], visibleBadge['specialPowerName'],
				i, visibleBadge['bonusMoney'])
			tokenBadges.append(tokenBadge)
		for player in gameState['players']:
			if player['id'] == self.id:
				self.coins = player['coins']
				self.tokensInHand = player['tokensInHand']
				if 'currentTokenBadge' in player:
					self.currentTokenBadge = createTokenBadge(player['currentTokenBadge'], 
						False)
				if 'declinedTokenBadge' in player:
					self.declinedTokenBadge = createTokenBadge(player['declinedTokenBadge'], 
						True)

		if not self.gameState:
			self.gameState = Game(gameState['gameId'], map, 
				gameState['lastEvent'] if (gameState['state'] == GAME_START) else gameState['state'],
				gameState['currentTurn'], gameState['activePlayerId'], tokenBadges, gameState['players'])
		else:
			self.gameState.visibleTokenBadges = tokenBadges
			self.gameState.players = gameState['players']
			self.gameState.activePlayerId = gameState['activePlayerId'];
			self.gameState.state = gameState['lastEvent'] if gameState['state'] == GAME_START else gameState['state'];
		
		self.gameState.defendingInfo = gameState['defendingInfo'] if 'defendingInfo' in gameState else None
		if 'friendsInfo' in gameState and 'slaveId' in gameState['friendsInfo'] and\
				gameState['friendsInfo']['slaveId']== self.id:
				self.masterId = gameState['friendsInfo']['masterId']
		else:
			self.masterId = None 
				
	def selectRace(self):
		maxTokensNum = 0
		bestTokens = list()

		for i, visibleBadge in enumerate(self.gameState.visibleTokenBages):
			if self.coins >= 5 - i:
				if visibleBadge.race.maxNum + visibleBadge.specialPower.tokensNum >= maxTokensNum:
					maxTokensNum = visibleBadge.race.maxNum + visibleBadge.specialPower.tokensNum
					if visibleBadge.race.maxNum + visibleBadge.specialPower.tokensNum > maxTokensNum:
						bestTokens = list()
					bestTokens.append({'tok': visibleBadge, 
						'num': visibleBadge.race.initNum + visibleBadge.specialPower.tokensNum})

		if not len(bestTokens):
			return False
		badge = sorted(bestTokens, key = lambda bestToken: bestToken.num, reverse = True)[0]['tok']
		result = self.sendCmd({'action': 'selectRace', 'sid': self.sid, 'pos': bagde.pos})
		if result['result'] != 'ok':
			raise BadFieldException('unknown error in select race')
		return True
	
	def defend(self):
		pass

	def shouldDecline(self):
		return self.currentTokenBadge and self.gameState.checkStage(GAME_DECLINE) and\
			self.currentTokenBadge.totalTokensNum - len(self.currentTokenBadge.getRegions()) < 4

	def decline(self):
		data = self.sendCmd({'action': 'decline', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in decline')

	def shouldFinishTurn():
		return self.gameState.checkStage(GAME_FINISH_TURN)

	def finishTurn():
		data = self.sendCmd({'action': 'finishTurn', 'sid': self.sid})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in decline')
		self.conqueredRegions = list()
		self.dragon = None #regions
		self.enchant = None
		self.slaveId = None

	def shouldSelectFriend():
		return self.gameState.checkStage(GAME_CHOOSE_FRIEND) and not self.slaveId

	def selectFriend():
		players = [player.id for player in self.gameState.players]
		for region in self.conqueredRegions:
			try:
				players.remove(region.owner)
			except:
				pass

		if len(players):
			data = self.sendCmd({'action': 'selectFriend', 'sid': self.sid, 
				'friendId': players[0]})
			if data['result'] != 'ok':
				raise BadFieldException('unknown error in select friend')
			self.slaveId = players[0]

	def canConquer(self, region):
		f1 = region.ownerId != self.id or region.ownerId == self.id and region.inDecline
		f2 = not(self.masterId and self.masterId == region.ownerId)
		self.currentTokenBadge.regions = self.currentTokenBadge.getRegions()
		f3 = self.race.canConquer(region, self.currentTokenBadge)
		f4 = self.race.canConquer(region, self.currentTokenBadge)
		f5 = not region.isImmune(False)
		return f1 and f2 and f3 and f4 and f5

	def getConquerableRegions(self):
		result = list()
		if not(self.gameState.checkStage(GAME_CONQUER) and self.currentTokenBadge and self.tokensInHand):
			return result
		for region in self.gameState.map.regions:
			if self.canConquer(region):
				result.append(region)

	def redeploy(self):
		regions = list()
		for region in self.currentTokenBadge.getRegions():
			regions.append({'regionId': region.id, 'tokensNum': region.tokensNum})
		data = self.sendCmd({'action': 'redeploy', 'sid': self.sid, 'regions': regions})
		if data['result'] != 'ok':
			raise BadFieldException('unknown error in redeploy')

	def getNextAct(self):
		if self.id == defendingPlayer:
			return self.defend
		if not self.currentTokenBadge and self.gameState.checkStage(GAME_SELECT_RACE):
			return self.selectRace
		if self.shouldDecline():
			return self.decline
		if self.shouldSelectFriend():
			return self.selectFriend
		if self.currentTokenBadge:
			self.conquerableRegions = self.getConquerableRegions()
			if not len(self.conquerableRegions): #should redeploy
				return self.redeploy
			return self.conquer
		return self.finishTurn

	def run(self):
		time.sleep(5)
		while True:
			self.getGameState()
			activePlayer = self.gameState.activePlayerId
			defendingPlayer = self.gameState.defendingInfo['playerId'] if self.gameState.defendingInfo else None
			if self.gameState.state == GAME_WAITING or not (self.id in (activePlayer, defendingPlayer)) or\
				(self.id == activePlayer and defendingPlayer):
				time.sleep(5)
				continue
			
