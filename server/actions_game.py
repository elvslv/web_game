import misc_game
from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry, WarHistoryEntry, dbi
from checkFields import *
from misc_game import *
from gameExceptions import BadFieldException
from misc import *
from sqlalchemy import func

def act_setReadinessStatus(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	if not game:
		raise BadFieldException('notInGame')
	
	if game.state != GAME_WAITING:
		raise BadFieldException('badGameState')

	user.isReady = data['isReady']
	dbi.flush(user)
	maxPlayersNum = game.map.playersNum
	readyPlayersNum = dbi.query(User).filter(User.game==game).filter(User.isReady==True).count()
	if maxPlayersNum == readyPlayersNum:
		misc_game.startGame(game, user, data)
	return {'result': 'ok'}
	
def act_selectRace(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if user.currentTokenBadge:
		raise BadFieldException('badStage')
	game = user.game	
	checkStage(GAME_SELECT_RACE, user)
	chosenBadge = game.getTokenBadge(data['position'])
	position = chosenBadge.pos
	price = dbi.query(TokenBadge).filter(TokenBadge.pos > position).count()
	if user.coins < price : 
		raise BadFieldException('badMoneyAmount')
	raceId, specialPowerId = chosenBadge.raceId, chosenBadge.specPowId
	addUnits = callRaceMethod(raceId, 'turnStartReinforcements')
	tokensNum = races.racesList[raceId].initialNum + races.specialPowerList[specialPowerId].tokensNum					
	user.coins += chosenBadge.bonusMoney - price
	user.currentTokenBadge = chosenBadge
	user.tokensInHand = tokensNum + addUnits
	chosenBadge.inDecline = False
	chosenBadge.bonusMoney = 0
	chosenBadge.totalTokensNum = tokensNum
	chosenBadge.specPowNum = races.specialPowerList[specialPowerId].bonusNum
	chosenBadge.pos = None
	dbi.flush(chosenBadge)
	updateRacesOnDesk(game, position)
	dbi.updateHistory(user, GAME_SELECT_RACE, chosenBadge.id)
	dbi.updateGameHistory(game, data)
	return {'result': 'ok', 'tokenBadgeId': chosenBadge.id}

def act_conquer(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: raise BadFieldException('badStage')
	game = user.game
	checkStage(GAME_CONQUER, user)
	region = game.map.getRegion(data['regionId'])
	regState = region.getState(game.id)
	owner = regState.owner
	if owner == user and not regState.inDecline: 
		raise BadFieldException('badRegion')
	tokenBadge = user.currentTokenBadge
	raceId, specialPowerId = tokenBadge.raceId, tokenBadge.specPowId
	user.checkForFriends(owner)
	f1 = callRaceMethod(raceId, 'canConquer', region, tokenBadge)
	f2 = callSpecialPowerMethod(specialPowerId, 'canConquer',  region,  tokenBadge)
	if not (f1 and f2):
		raise BadFieldException('badRegion')
	regState.checkIfImmune()
	attackedRace = None
	attackedSpecialPower = None
	if regState.tokenBadge:
		attackedRace = regState.tokenBadge.raceId
		attackedSpecialPower = regState.tokenBadge.specPowId
	enemyDefenseBonus = 0
	if attackedRace:
		enemyDefenseBonus = callRaceMethod(attackedRace, 'defenseBonus')
	defense = regState.tokensNum
	unitPrice = max(misc.BASIC_CONQUER_COST + defense + region.mountain + 
		regState.encampment + regState.fortress +  enemyDefenseBonus +
		callRaceMethod(raceId, 'attackBonus', region, tokenBadge) + 
		callSpecialPowerMethod(specialPowerId, 'attackBonus', region, tokenBadge)
			, 1)
	unitsNum = user.tokensInHand
	dice = user.game.getLastState() == GAME_THROW_DICE and user.game.history[-1].dice
	if not dice and unitsNum < unitPrice : 
		dice = misc_game.throwDice(game)
	unitPrice -= dice if dice else 0				# How do I turn None into 0? int() doesn't seem to work
	unitPrice = max(unitPrice, 1)
	if unitsNum < unitPrice:
		dbi.updateHistory(user, GAME_UNSUCCESSFULL_CONQUER, user.currentTokenBadge.id)
		return {'result': 'badTokensNum', 'dice': dice}
	clearFromRace(regState)					# Not sure if it's necessary
	victimBadgeId = regState.tokenBadgeId
	regState.owner = user
	regState.tokenBadge = user.currentTokenBadge
	regState.inDecline = False
	regState.tokensNum = unitPrice
	callRaceMethod(raceId, 'conquered', regState, tokenBadge)
	dbi.updateWarHistory(user, victimBadgeId, tokenBadge.id, dice, 
		region.id, defense, ATTACK_CONQUER)
	user.tokensInHand -= unitPrice
	dbi.updateGameHistory(game, data)
	return {'result': 'ok', 'dice': dice} if dice else {'result': 'ok'}

def act_decline(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_DECLINE, user)
	makeDecline(user)
	dbi.updateHistory(user, GAME_DECLINE, user.declinedTokenBadge.id)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}

def act_redeploy(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	tokenBadge = user.currentTokenBadge
	if not tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_REDEPLOY, user)
	raceId, specialPowerId = tokenBadge.raceId, tokenBadge.specPowId
	tokenBadge.totalTokensNum += callRaceMethod(raceId, 'turnEndReinforcements', user)
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
	{'name': 'fortified', 'cmd': 'setFortified'},
	{'name': 'heroes', 'cmd': 'setHero'}]

	for specAbility in specAbilities:
		if specAbility['name'] in data:
			callSpecialPowerMethod(specialPowerId, specAbility['cmd'], tokenBadge, 
				data[specAbility['name']])

			
	if unitsNum: 
		if not regState:
			raise BadFieldException('thereAreTokensInHand')
		regState.tokensNum += unitsNum
	emptyRegions = filter( lambda x: not x.tokensNum, tokenBadge.regions)
	for region in emptyRegions:
		clearFromRace(region)	
		region.owner = None
		region.tokenBadge = None
	user.tokensInHand = 0
	dbi.updateHistory(user, GAME_REDEPLOY, user.currentTokenBadge.id)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}
		

def act_finishTurn(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	game = user.game
	checkStage(GAME_FINISH_TURN, user)
	tokenBadge = user.currentTokenBadge
	if tokenBadge and callRaceMethod(tokenBadge.raceId, 'needRedeployment') and\
		game.getLastState() != GAME_REDEPLOY and game.getLastState() != GAME_CHOOSE_FRIEND :  
		raise BadFieldException('badStage')

	incomeCoins = countCoins(user)
	user.coins += incomeCoins['totalCoinsNum']
	user.tokensInHand = 0
	nextPlayer = game.getNextPlayer()

	dbi.updateHistory(user, GAME_FINISH_TURN, None)
	dbi.updateGameHistory(game, data)
	prepareForNextTurn(game, nextPlayer)
	if misc.TEST_MODE:
		result = {'result': 'ok', 'nextPlayer' : nextPlayer.id, 'coins': user.coins}
	else:	
		result = {'result': 'ok', 'nextPlayer' : nextPlayer.id, 'coins': user.coins, 
		'incomeCoins':incomeCoins['totalCoinsNum'], 'statistics': incomeCoins['statistics']}
	return result

def act_defend(data):			## Should be renamed to retreat
	user = dbi.getXbyY('User', 'sid', data['sid'])
	tokenBadge = user.currentTokenBadge
	if not tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_DEFEND, user)
	attackedRegion = user.game.getDefendingRegion(user)
	raceId, specialPowerId = tokenBadge.raceId, tokenBadge.specPowId
	callRaceMethod(raceId, 'sufferCasualties', tokenBadge)
	tokensNum = user.game.history[-1].warHistory.victimTokensNum - callRaceMethod(raceId, 'getCasualties')
	notAdjacentRegions = []
	for terr in tokenBadge.regions:
		if terr.region.id not in attackedRegion.getNeighbors():##~~
			notAdjacentRegions.append(terr.region.id)
	for region in data['regions']:
		if not 'regionId' in region:
			raise BadFieldException('badJson')				
		if not 'tokensNum' in region:	
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')
		if tokensNum < region['tokensNum']:
			raise BadFieldException('notEnoughTokens')
		destination = user.game.map.getRegion(region['regionId'])
		destState = destination.getState(user.game.id)
		if  notAdjacentRegions and destination.id not in notAdjacentRegions  or destState.owner.id != user.id:
			raise BadFieldException('badRegion')
		destState.tokensNum += region['tokensNum']
		tokensNum -= region['tokensNum']
	if tokensNum:  raise BadFieldException('thereAreTokensInTheHand')
	dbi.updateHistory(user, GAME_DEFEND, tokenBadge.id)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}

def act_dragonAttack(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_CONQUER, user, ATTACK_DRAGON)
	callSpecialPowerMethod(user.currentTokenBadge.specPowId, 'dragonAttack', 
		user.currentTokenBadge, user.game.map.getRegion(data['regionId']).getState(
		user.game.id))
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}	

def act_enchant(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadge: 
		raise BadFieldException('badStage')
	checkStage(GAME_CONQUER, user, ATTACK_ENCHANT)
	
	reg = user.game.map.getRegion(data['regionId']).getState(user.game.id)
	victimBadgeId = reg.tokenBadge.id
	reg.checkIfImmune(True)
	clearFromRace(reg)
	callRaceMethod(user.currentTokenBadge.raceId, 'enchant', user.currentTokenBadge,
		reg)
	dbi.updateWarHistory(user, victimBadgeId, user.currentTokenBadge.id, None, 
			reg.region.id, 1, ATTACK_ENCHANT)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}	

def act_selectFriend(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadgeId : 
		raise BadFieldException('badStage')
	checkStage(GAME_CHOOSE_FRIEND, user)
	callSpecialPowerMethod(user.currentTokenBadge.specPowId, 'selectFriend',
		user, data)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok'}


def act_throwDice(data):
	user = dbi.getXbyY('User', 'sid', data['sid'])
	if not user.currentTokenBadgeId : raise BadFieldException('badStage')
	checkStage(GAME_THROW_DICE, user)
	if misc.TEST_MODE: 
		dice = data['dice'] if 'dice' in data else 0
	else:
		specialPowerId = user.currentTokenBadge.specPowId
		dice = callSpecialPowerMethod(specialPowerId, 'throwDice', user.game)
	dbi.updateHistory(user, GAME_THROW_DICE, user.currentTokenBadge.id, dice)
	dbi.updateGameHistory(user.game, data)
	return {'result': 'ok', 'dice': dice}	
