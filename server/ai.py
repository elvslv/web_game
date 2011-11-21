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
		self.name = name
		self.descr = descr
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

	def regions(self, game):
		result = list()
		for region in game.map.regions:
			if region.tokenBadgeId == self.id:
				result.append(region)
		return result

currentRegionFields = ['ownerId', 'tokenBadgeId', 'tokensNum', 'holeInTheGround', 
	'encampment', 'dragon', 'fortress', 'hero', 'inDecline']

def createMap(mapState):
	regions = list()
	for region in mapState.regions:
		curReg = list()
		if 'currentRegionState' in region:
			curState = region['currentRegionState']
			for field in currentRegionFields:
				curReg.append(curState[field] if field in curState else None)
		regions.append(Region(region.id, region.adjacentRegions, region.constRegionState, 
			*curReg))
	return Map(mapState.mapId, mapState.playersNum, mapState.turnsNum, regions);

def createTokenBadge(tokenBadge, declined):
	return TokenBadge(tokenBadge.id, tokenBadge.raceName, tokenBadge.specialPowerName,
				None, None, declined, tokenBadge.totalTokensNum)
	
class AI(threading.Thread):
	def __init__(self, host, game, id, sid):
		self.conn = httplib.HTTPConnection(host, timeout = 10000)
		self.game = game
		self.sid = sid
		self.id = id
		self.conqueredRegions = list()
		self.dragon = None #regions
		self.enchant = None
		self.friend = None
		
	def sendCmd(self, obj):
		self.conn.request("POST", "/ajax", obj)
		data = json.loads(conn.getresponse().read())
		if not 'result' in data:
			raise BadFieldException('Unknown result')
		if (data['result'] in ('badJson', 'badReadinessStatus', 'badUserSid', 
			'badGameId', 'badMapId', 'badPosition', 'badFriendId', 'badRegionId')):
			raise BadFieldException(data['result'])
		return data

	def getGameState(self):
		data = self.sendCmd({'action': 'getGameState', 'gameId': self.game.id})
		gameState = data['gameState']
		map = None
		if not self.gameState:
			map = createMap(data['gameState']['map'])
		else:
			for i, region in enumerate(data['gameState']['map']):
				curReg = list()
				if 'currentRegionState' in region:
					curState = region['currentRegionState']
					for field in currentRegionFields:
						self.game.map.regions[i][field] = curState[field] if field in curState else None
		
		tokenBadges = list()
		visibleBadges = gameState['visibleTokenBadges']
		for visibleBadge in visibleBadges:
			tokenBadge = TokenBadge(0, visibleBadge.raceName, visibleBadge.specialPowerName,
				i, visibleBadge.bonusMoney)
			tokenBadges.append(tokenBadge)
		for player in gameState['players']:
			if player['id'] == self.id:
				self.coins = player['coins']
				self.tokensInHand = player['tokensInHand']
				if player['currentTokenBadge']:
					self.currentTokenBadge = createTokenBadge(player['currentTokenBadge'], 
						False)
				if player['declinedTokenBadge']:
					self.declinedTokenBadge = createTokenBadge(player['declinedTokenBadge'], 
						True)	

		if not self.gameState:
			self.gameState = Game(gameState.gameId, map, 
				gameState.lastEvent if (gameState.state == GAME_START) else gameState.state,
				gameState.currentTurn, gameState.activePlayerId, tokenBadges, gameState['players'])
		else:
			self.gameState.visibleTokenBadges = tokenBadges
			self.gameState.players = gameState['players']
			self.gameState.activePlayerId = gameState['activePlayerIndex'];
			self.gameState.state = gameState.lastEvent if gameState.state == GAME_START else gameState.state;
		
		if 'defendingInfo' in gameState:
			self.gameState['defendingInfo'] = gameState['defendingInfo']

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
			self.currentTokenBadge.totalTokensNum - len(self.currentTokenBadge.regions()) < 4

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
		self.friend = None

	def shouldSelectFriend():
		return self.gameState.checkStage(GAME_CHOOSE_FRIEND) and not self.friend

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
			self.friend = players[0]

	def getNextAct(self):
		if self.id == defendingPlayer:
			return self.defend
		if not self.currentTokenBadge and self.gameState.checkStage(GAME_SELECT_RACE)
			return self.selectRace
		if self.shouldDecline():
			return self.decline
		if self.shouldSelectFriend():
			return self.selectFriend
		if self.shouldFinishTurn():
			return self.finishTurn
		if not self.canConquer() #should redeploy
			return self.redeploy
		return self.conquer

	def run(self):
		while True:
			data = self.getGameState()
			activePlayer = self.gameState['activePlayerId']
			defendingPlayer = self.gameState['defendingInfo']['playerId'] if 'defendingInfo' in self.gameState else None
			if data['state'] == GAME_WAITING or not self.id in (activePlayer, defendingPlayer) or\
				(self.id == activePlayer and defendingPlayer):
				time.sleep(5)
				continue
			
