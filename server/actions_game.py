from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, WarHistoryEntry
from checkFields import *
from misc_game import *
from gameExceptions import BadFieldException
from misc import *

dbi = Database()

def act_setReadinessStatus(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	if not game:
		raise BadFieldException('notInGame')
	
	if game.state != GAME_WAITING:
		raise BadFieldException('badGameState')

	user.isReady = data['isReady']
	maxPlayersNum = game.map.playersNum
	readyPlayersNum = dbi.query(User).filter(User.game==game).filter(User.isReady==True).count()
	if maxPlayersNum == readyPlayersNum:
		# Starting
		game.activePlayerId = min(game.players, key=lambda x: x.priority).id
		game.state = GAME_START
		#generate first 6 races
		if TEST_MODE and 'visibleRaces' in data and 'visibleSpecialPowers' in data:
                        vRaces = data['visibleRaces']
                        vSpecialPowers = data['visibleSpecialPowers']
                        for i in range(misc.VISIBLE_RACES):
                                showNextRace(game, misc.VISIBLE_RACES - 1, vRaces[misc.VISIBLE_RACES-i-1], 
                                	vSpecialPowers[misc.VISIBLE_RACES-i-1])
                else:
                        for i in range(misc.VISIBLE_RACES):
                                showNextRace(game, misc.VISIBLE_RACES - 1)
			
	dbi.updateHistory(user.id, game.id, GAME_START, None)
	return {'result': 'ok'}
	
def act_selectRace(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if user.currentTokenBadge:
		raise BadFieldException('badStage')
	game = user.game	
	game.checkStage(GAME_SELECT_RACE, user)
	
	chosenBadge = game.getTokenBadge(data['position'])
	position = chosenBadge.pos
	price = dbi.query(TokenBadge).filter(TokenBadge.pos >position).count()
	if user.coins < price : 
		raise BadFieldException('badMoneyAmount')
	raceId, specialPowerId = chosenBadge.raceId, chosenBadge.specPowId
	tokensNum = races.racesList[raceId].initialNum + races.specialPowerList[specialPowerId].tokensNum
	addUnits =  callRaceMethod(raceId, 'countAdditionalConquerUnits', game)
	user.coins += chosenBadge.bonusMoney - price
	user.currentTokenBadge = chosenBadge
	user.tokensInHand = tokensNum + addUnits
	chosenBadge.inDecline = False
	chosenBadge.bonusMoney = 0
	chosenBadge.totalTokensNum = tokensNum
	updateRacesOnDesk(game, position)

	dbi.updateHistory(user.id, game.id, GAME_SELECT_RACE, chosenBadge.id)

	return {'result': 'ok', 'tokenBadgeId': chosenBadge.id}

def act_conquer(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: raise BadFieldException('badStage')
	game = user.game
	game.checkStage(GAME_CONQUER, user)
	region = game.map.getRegion(data['regionId'])
	regState = region.getState(game.id)
	owner = regState.owner
	if owner == user and not regState.inDecline: 
		raise BadFieldException('badRegion')
	raceId, specialPowerId = user.currentTokenBadge.raceId, user.currentTokenBadge.specPowId
	user.checkForFriends(owner)
	f1 = callRaceMethod(raceId, 'canConquer', region, user.currentTokenBadge)
	f2 = callSpecialPowerMethod(specialPowerId, 'canConquer',  region,  user.currentTokenBadge)
	if not (f1 or f2):
		raise BadFieldException('badRegion')
	regState.checkIfImmune()
	attackedRace = None
	attackedSpecialPower = None
	if regState.tokenBadge:
		attackedRace = regState.tokenBadge.raceId
		attackedSpecialPower = regState.tokenBadge.specPowId
	additionalTokensNum = 0
	if attackedRace:
		enemyDefenseBonus = callRaceMethod(attackedRace, 'defenseBonus')
	defense = regState.tokensNum
	unitPrice = max(misc.BASIC_CONQUER_COST + defense + region.mountain + 
		regState.encampment + regState.fortress + additionalTokensNum + 
		callRaceMethod(raceId, 'conquerBonus', region, regState.tokenBadge) + 
		callSpecialPowerMethod(specialPowerId, 'conquerBonus', region, regState.tokenBadge)
			, 1)
	unitsNum = user.tokensInHand
	dice = user.game.history[-1].dice
	if not dice and unitsNum < unitPrice : 
		dice = throwDice()
	unitPrice -= dice if dice else 0				# How do I turn None into 0? int() doesn't seem to work
	if unitsNum < unitPrice:
		dbi.updateHistory(user.id, game.id, GAME_UNSUCCESSFULL_CONQUER, user.currentTokenBadge.id)
		return {'result': 'badTokensNum', 'dice': dice}
	if regState.tokenBadge: region.clearFromRace(regState.tokenBadge)
	regState.owner = user
	regState.tokenBadge = user.currentTokenBadge
	regState.inDecline = False
	regState.tokensNum = unitPrice
	callRaceMethod(raceId, 'conquered', regState, user.currentTokenBadge)
	victimBadgeId = owner.currentTokenBadge.id if owner else None
	dbi.updateWarHistory(user.id, game.id, victimBadgeId, user.currentTokenBadge.id, dice, 
		region.id, defense, ATTACK_CONQUER)
	user.tokensInHand -= unitPrice
	return {'result': 'ok', 'dice': dice} if dice else {'result': 'ok'}
		
def act_decline(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: raise BadFieldException('badStage')

	user.game.checkStage(GAME_DECLINE, user)
	raceId, specialPowerId = user.currentTokenBadge.raceId, user.currentTokenBadge.specPowId
	callSpecialPowerMethod(specialPowerId, 'tryToGoInDecline', game.id)

	callRaceMethod(raceId, 'decline', user.id)	
	callSpecialPowerMethod(specialPowerId, 'decline', user.id)	
	user.declinedTokenBadge = user.currentTokenBadge
	user.currentTokenBadge = None
	user.tokensInHand = 0
	dbi.updateHistory(user.id, game.id, GAME_DECLINE, user.currentTokenBadge.id)
	return {'result': 'ok'}

def act_redeploy(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	tokenBadge = user.currentTokenBadge
	if not tokenBadge: raise BadFieldException('badStage')
	user.game.checkStage(GAME_REDEPLOY, user)
	raceId, specialPowerId = tokenBadge.raceId, tokenBadge.specPowId
	unitsNum = tokenBadge.totalTokensNum
	if not unitsNum: raise BadFieldException('noTokensForRedeployment')
	if not tokenBadge.regions:
		raise BadFieldException('userHasNoRegions')
	for region in tokenBadge.regions: region.tokensNum = 0
	for rec in data['regions']:
		if not ('regionId' in rec and 'tokensNum' in rec):
			raise BadFieldException('badJson')							## Shouldn't it be in some sort of
																	## ``check everything'' function?
		if not isinstance(rec['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(rec['tokensNum'], int):
			raise BadFieldException('badTokensNum')
		regState = user.game.map.getRegion(rec['regionId']).getState(user.game.id)
		tokensNum = rec['tokensNum']
		if  regState.tokenBadge != user.currentTokenBadge: raise BadFieldException('badRegion')
		if tokensNum > unitsNum: raise BadFieldException('notEnoughTokensForRedeployment')
		regState.tokensNum = tokensNum		
		unitsNum -= tokensNum

	specAbilities = [
	{'name': 'encampments', 'cmd': 'setEncampments'},
	{'name': 'fortifield', 'cmd': 'setFortifield'},
	{'name': 'heroes', 'cmd': 'setHeroes'},
	{'name': 'selectFriend', 'cmd': 'selectFriend'}]

	for specAbility in specAbilities:
		if specAbility['name'] in data:
			callSpecialPowerMethod(specialPowerId, specAbility['cmd'], 
				data[specAbility['name']], tokenBadgeId)

			
	if unitsNum: regState.tokensNum += unitsNum
	emptyRegions = filter( lambda x: not x.tokensNum, tokenBadge.regions)
	for region in emptyRegions:
		callRaceMethod(raceId, 'declineRegion', region.tokenBadge)
		callSpecialPowerMethod(specialPowerId, 'declineRegion', region.tokenBadge)		##??
		region.owner = None

	dbi.updateHistory(user.id, user.game.id, GAME_REDEPLOY, user.currentTokenBadge.id)
	return {'result': 'ok'}
		
def endOfGame(coins): #rewrite!11
	return {'result': 'ok', 'coins': coins}

def act_finishTurn(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	user.game.checkStage(GAME_FINISH_TURN, user)

	income =len(user.regions)
	additionalCoins = 0
	races = dbi.query(TokenBadge).filter_by(owner=user)
	for race in races:
		income += callRaceMethod(race.raceId, 'countAdditionalCoins', user.id, user.game.id)
		income += callSpecialPowerMethod(race.specPowId, 'countAdditionalCoins', user.id, user.game.id, user.currentTokenBadge.raceId)
	user.coins += income
	user.tokensInHand = 0
	nextPlayer = dbi.getNextPlayer(user.game)
	if not nextPlayer:
		nextPlayer = user.game.players[0]
		user.game.turn += 1
		if user.game.turn == user.game.turnsNum:
			return endOfGame(coins)

	for rec in races:
		callRaceMethod(rec.raceId, 'updateBonusStateAtTheAndOfTurn', user.currentTokenBadge.id)
		callSpecialPowerMethod(rec.specPowId, 'updateBonusStateAtTheAndOfTurn', user.currentTokenBadge.id)

	dbi.updateHistory(user.id, user.game.id, GAME_FINISH_TURN, user.currentTokenBadge.id)
	prepareForNextTurn(user.game, nextPlayer)
	return {'result': 'ok', 'nextPlayer' : nextPlayer,'coins': coins}

def act_defend(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])

	if not(user.tokenBadgeId): raise BadFieldException('badStage')
	
	user.game.checkStage(GAME_DEFEND, user)
	attackedRegion = user.game.getDefendingRegionInfo(user)
	tokenBadge = user.currentTokenBadge
	raceId, specialPowerId = tokenBadge.raceId, tokenBadge.specPowId
	tokensNum += callRaceMethod(raceId, 'countAddDefendingTokensNum')

	#find not adjacent regions
	notAdjacentRegions = []
	for region in tokenBadge.regions:
		if not region.id in attackedRegion.getNeighbors(): 
			notAdjacentRegions.extend(region.id)
	for region in data['regions']:
		if not 'regionId' in region:
			raise BadFieldException('badJson')					## Oh for crying out loud
		if not 'tokensNum' in region:	
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')

		if tokensNum < region['tokensNum']:
			raise BadFieldException('notEnoughTokens')
		destination = user.game.map.getRegion(data['regionId'])
		destState = destination.getState(user.game.id)
		if  notAdjacentRegions and destination.id not in notAdjacentRegions.id  or destState.owner.id != user.id:
			raise BadFieldException('badRegion')
		
		destState.tokensNum += region['tokensNum']
		tokensNum -= region['tokensNum']
	if tokensNum:  raise BadFieldException('thereAreTokensInTheHand')
	callRaceMethod(raceId, 'updateAttackedTokensNum', user.tokenBadge.id)
	dbi.updateHistory(user.id, user.game.id, GAME_DEFEND, user.currentTokenBadge.id)
	return {'result': 'ok'}

def act_dragonAttack(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_DRAGON_ATTACK, user)
	callSpecialPowerMethod(user.currentTokenBadge.specialPower.id, 'dragonAttack', tokenBadgeId, data['regionId'], 
		data['tokensNum'])
	return {'result': 'ok'}	

def act_enchant(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_ENCHANT, user)
	callRaceMethod(user.currentTokenBadge.raceId, 'enchant', user.currentTokenBadge.id, data['regionId'])

	return {'result': 'ok'}	

def act_getVisibleTokenBadges(data):
	game = dbi.getXbyY('Game', 'id', data['gameId'])
	rows = game.tokenBadges()
	result = list()
	for tokenBadge in filter(lambda x: x.position > 0, rows):
		result.append({
			'raceId': races.racesList[tokenBadge.raceId].name, 
			'specialPowerId': races.specialPowerList[tokenBadge.specPowerId].name,
			'position': tokenBadge.position})
	return {'result': result}

def act_throwDice(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not(user.tokenBadgeId): raise BadFieldException('badStage')
	checkStage(GAME_THROW_DICE, user)
	
	specialPowerId =user.currentTokenBadge.specPowerId
	dice = callSpecialPowerMethod(specialPowerId, 'throwDice')
	dbi.add(History(user.id, game.id, GAME_THROW_DICE, user.tokenBadge.id))
	return {'result': 'ok', 'dice': dice}	


