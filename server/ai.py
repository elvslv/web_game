import httplib
import json
import threading
import misc
import time
import races

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
		badStage = not (lastEvent in misc.possiblePrevCmd[state]) 
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

class AI(threading.Thread):
	def __init__(self, host, game, id, sid):
		self.conn = httplib.HTTPConnection(host, timeout = 10000)
		self.game = game
		self.sid = sid
		self.id = id
		
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
			
	def defend(self):
		pass

	def run(self):
		while True:
			data = self.getGameState()
			activePlayer = self.gameState['activePlayerId']
			defendingPlayer = self.gameState['defendingInfo']['playerId'] if 'defendingInfo' in self.gameState else None
			if data['state'] == misc.GAME_WAITING or not self.id in (activePlayer, defendingPlayer) or\
				(self.id == activePlayer and defendingPlayer):
				time.sleep(5)
				continue
			if self.id == defendingPlayer:
				self.defend()

