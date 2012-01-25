import ai
from misc_ai import *
from copy import copy as copy

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
		self.advance(conqStrat)

	def conquer(self):
		strat = self.chooseStrategy()[0]
		self.advance(strat)

	def advance(self, strategy):
		for act in strategy:
			chosenRegion = self.game.map.getRegion(act['regionId'])
			conqdReg = copy(chosenRegion)
			conqdReg.nonEmpty = chosenRegion.tokensNum > 0
			res = self.sendCmd(act)['result']
			if res == 'badTokensNum':	
				return
			elif res != 'ok':
				raise BadFieldException('unknown error in conquer: %s' % res)
			self.conqueredRegions.append(conqdReg)	



	def chooseStrategy(self, badge=None):
		if badge: 
			initNum = badge.totalTokensNum + badge.race.turnStartReinforcements()
			tBadge = badge
		else:
			initNum = self.tokensInHand
			tBadge = self.currentTokenBadge
		strategies = self.generateConquestStrategies(tBadge, initNum)
		maxReward, bestStrategy = 0, list()
		tBadge = badge or self.currentTokenBadge
		initNum = 0
		for strat in strategies:
			reward = sum(map(lambda x: tBadge.regBonus(x), strat))
			if reward > maxReward:
				maxReward = reward
				bestStrategy = strat
		return [map(lambda x: {'action' : 'conquer', 'sid' : self.sid, 'regionId' : x.id}, bestStrategy), 
				maxReward] 	

	
	def generateConquestStrategies(self, badge, initNum):
		start = self.getConquerableRegions(badge)
		global conquestStrategies
		conquestStrategies = list()
		def addConqReg(lst, reg, n):
			reg.d = 1
			nextLst = self.game.map.adjacent_(reg, badge)
			if badge.specPower.name != 'Seafaring': nextLst = filter(lambda x: not x.sea, nextLst) 	
			for region in filter(lambda x: self.canConquer(x, badge, 0xC) and not x.d, nextLst):
				price = self.getRegionPrice(region, badge)
				if price <= n: 
					addConqReg(lst + mList(region), region, n - price)
				else:
					global conquestStrategies
					conquestStrategies += mList(lst)
					break
			reg.d = 0	

		for st in start:
			for reg in self.game.map.regions: reg.d = 0
			addConqReg(mList(st), st, initNum - self.getRegionPrice(st, badge))
		return conquestStrategies
