import ai

from misc_ai import *
from misc import *
from copy import copy as copy
from gameExceptions import BadFieldException

MIN_ALLOWED_TURN_REWARD = 2

class AdvancedAI(ai.AI):
	def __init__(self, host, gameId, sid, id, logFile):
		ai.AI.__init__(self, host, gameId, sid, id, logFile)

	def selectRace(self):
		visibleBadges = self.game.visibleTokenBadges
		maxReward, bestChoice, conqStrat = 0, None, None
		for badge in visibleBadges:
			strat, reward = self.chooseStrategy(badge)
			if reward > maxReward:
				bestChoice = badge
				maxReward = reward
				conqStrat = strat
		result = self.sendCmd({'action': 'selectRace', 'sid': self.sid, 'position': bestChoice.pos})
		if result['result'] != 'ok':
			raise BadFieldException('unknown error in select race %s' % result['result'])
		self.turnStrategy = conqStrat
		self.turnReward = maxReward

	def conquer(self):
		if not self.turnStrategy:
			self.turnStrategy = self.chooseStrategy()[0]
		cmd = self.turnStrategy[0]
		chosenRegion = self.game.map.getRegion(cmd['regionId'])
		conqdReg = copy(chosenRegion)
		conqdReg.nonEmpty = chosenRegion.tokensNum > 0
		if conqdReg.nonEmpty and chosenRegion.ownerId:
			self.turnStrategy = None
		else:
			self.turnStrategy.pop(0)
		res = self.sendCmd(cmd)['result']
		if res not in ('ok', 'badTokensNum'):
			raise BadFieldException('unknown error in conquer: %s' % res)
		self.conqueredRegions.append(conqdReg)	
		
	def shouldDecline(self):
		tBadge = self.currentTokenBadge
		if self.turnReward is None:
			self.turnStrategy, self.turnReward = self.chooseStrategy()
		print self.turnReward
		return tBadge and tBadge.specPower.canDecline(self, False) and\
			self.game.checkStage(GAME_DECLINE, self) and\
				self.turnReward < MIN_ALLOWED_TURN_REWARD
				

	def chooseStrategy(self, badge=None):
		initNum = 0
		if badge: 
			initNum = badge.totalTokensNum + badge.race.turnStartReinforcements()
			tBadge = badge
		else:
			initNum = self.tokensInHand
			tBadge = self.currentTokenBadge
		strategies = self.generateConquestStrategies(tBadge, initNum)
		maxReward, bestStrategy = 0, list()
		tBadge = badge or self.currentTokenBadge
		for strat in strategies:
			clearStrat = filter(lambda x: isinstance(x, ai.Region), strat)
			reward = sum(map(lambda x: tBadge.regBonus(x) * (x.ownerId != self.id), clearStrat))
			if reward > maxReward:
				maxReward = reward
				bestStrategy = strat
		
		return [convertStrategy(bestStrategy, self.sid), maxReward] 	

	

	def generateConquestStrategies(self, badge, initNum):
		start = self.getConquerableRegions(badge)
		global conquestStrategies
		conquestStrategies = list()
		print initNum, 'inum'
		def addConqReg(lst, reg, n, dragon=False, enchantment=False):
			global conquestStrategies
			reg.d = 1
			found = False
			nextLst = self.game.map.adjacent_(reg, badge)
			if badge.specPower.name != 'Seafaring': nextLst = filter(lambda x: not x.sea, nextLst) 	
			for region in filter(lambda x: self.canConquer(x, badge, 0xC) and not x.d, nextLst):
				price = self.getRegionPrice(region, badge)
				if dragon and n >= 1:
					addConqReg(lst + mList('d') + mList(region), region, n - 1, False, enchantment)
				if enchantment and not region.isImmune(True):
					addConqReg(lst + mList('e') + mList(region), region, n + 1, dragon, False)
				if price <= n:
					found = True
					addConqReg(lst + mList(region), region, n - price, dragon, enchantment)
			if not found: conquestStrategies += mList(lst)
			reg.d = 0	

		for st in start:
			for reg in self.game.map.regions: reg.d = 0
			addConqReg(mList(st), st, initNum - self.getRegionPrice(st, badge), self.canUseDragon(badge), self.canEnchant(badge))
		return conquestStrategies
	
		
	def canEnchant(self, badge):
		return badge.race.canEnchant() and not self.enchantUsed
		
	def finishTurn(self):
		ai.AI.finishTurn(self)
		self.turnStrategy, self.turnReward = None, None



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