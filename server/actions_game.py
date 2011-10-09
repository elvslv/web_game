from db import Database, User, Message, Game, Map, Adjacency, RegionState, HistoryEntry
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
	
	chosenBadge = dbi.getXbyY('TokenBadge', 'pos', data['position'])
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
	chosenBadge.tokensNum = tokensNum
	updateRacesOnDesk(game, position)

	dbi.updateHistory(user.id, game.id, GAME_SELECT_RACE, chosenBadge.id)

	return {'result': 'ok', 'tokenBadgeId': chosenBadge.id}

def act_conquer(data):
	user = dbi.getUserBySid(data['sid'])
	if not user.tokenBadge: raise BadFieldException('badStage')

	user.game.checkStage(GAME_CONQUER, user)
	region = dbi.getCurrentRegionStateById(data['regionId'])
	if region.owner == user and not region.inDecline: 
		raise BadFieldException('badRegion')
	raceId, specialPowerId = user.tokenBadge.raceId, user.tokenBadge.specialPowerId
	user.checkForFriends(owner)
	playerRegions = user.tokenBadge.regions
	playerBorderline = False	
	for plRegion in playerRegions:
		if region in plRegion.getNeighbors():
			playerBorderline = True
			break
	if playerBorderline: #case for flying and seafaring
		if not callSpecialPowerMethod(specialPowerId, 'tryToConquerAdjacentRegion', 
			playerRegions, region.border, region.coast, region.sea):
			raise BadFieldException('badRegion')
	else:
		f1 = callRaceMethod(raceId, 'tryToConquerNotAdjacentRegion', playerRegions, region, user.tokenBadge)
		f2 = callSpecialPowerMethod(specialPowerId, 'tryToConquerNotAdjacentRegion',  playerRegions, region,  user.TokenBadge)
		if not (f1 or f2):
			raise BadFieldException('badRegion')

	if region.holeInTheGround or region.dragon or region.hero:
		raise BadFieldException('regionIsImmune')
	attackedRace = None
	attackedSpecialPower = None
	if attackedTokenBadgeId:
		attackedRace = region.tokenBadge.race
		attackedSpecialPower = region.tokenBadge.specialPower
	additionalTokensNum = 0
	if attackedRace:
		additionalTokensNum = callRaceMethod(attackedRace, 'countAdditionalConquerPrice')
	unitPrice = max(misc.BASIC_CONQUER_COST + attackedTokensNum + region.mountain + 
		region.encampment + region.fortress + additionalTokensNum + 
		callRaceMethod(raceId, 'countConquerBonus', currentRegionId, 
		attackedTokenBadgeId) + callSpecialPowerMethod(specialPowerId, 
		'countConquerBonus', currentRegionId, attackedTokenBadgeId), 1)
			
	unitsNum = user.tokensInHand
	dice = user.game.history[-1].dice
	if not dice and unitsNum < unitPrice : 
		dice = throwDice()
	unitPrice -= int(dice)
	if unitsNum < unitPrice:
		dbi.add(History(user.id, game.id, GAME_UNSUCCESFUL_CONQUER, user.tokenBadge.id))
		return {'result': 'badTokensNum', 'dice': dice}
	if attackedTokenBadgeId: region.clearFromRace(attackedTokenBadge)
	region.owner = user
	region.tokenBadge = user.tokenBadge
	region.inDecline = false
	region.tokensNum = unitPrice
	callRaceMethod(raceId, 'conquered', currentRegionId, tokenBadgeId)
	dbi.add(History(user.id, game.id, GAME_CONQUER, user.tokenBadge.id))
	dbi.add(WarHistory(dbi.last_id(), user.tokenBadge.id, region, owner.tokenBadge.id, attackedTokensNum,
		attackedTokensNum, dice, ATTACK_CONQUER))
	return {'result': 'ok', 'dice': dice} if dice else {'result': 'ok'}
		
def act_decline(data):
	user = dbi.getUserBySid(data['sid'])
	if not user.tokenBadge:
		raise BadFieldException('badStage')

	user.game.checkStage(GAME_DECLINE, user)
	raceId, specialPowerId = user.tokenBadge.raceId, user.tokenBadge.specialPowerId
	callSpecialPowerMethod(specialPowerId, 'tryToGoInDecline', gameId)

	callRaceMethod(raceId, 'decline', userId)	
	callSpecialPowerMethod(specialPowerId, 'decline', userId)	
	user.declinedTokenBadge = user.currentTokenBadge
	user.currentTokenBadge = None
	user.tokensInHand = 0
	dbi.add(History(user.id, game.id, GAME_DECLINE, user.tokenBadge.id))
	return {'result': 'ok'}

def act_redeploy(data):
	user = dbi.getUserBySid(data['sid'])
	if not(tokenBadgeId): raise BadFieldException('badStage')
	checkStage(GAME_REDEPLOY, user)
			
	raceId, specialPowerId = user.tokenBadge.raceId, user.tokenBadge.specialPowerId
	unitsNum = user.currentTokenBadge.totalTokensNum
	if not unitsNum: raise BadFieldException('noTokensForRedeployment')
	if not user.tokenBadge.regions:
		raise BadFieldException('userHasNoRegions')
	for region in user.currentTokenBadge.regions: region.tokensNum = 0

	for region in data['regions']:
		if not ('regionId' in region and 'tokensNum' in region):
			raise BadFieldException('badJson')							## Shouldn't it be in some sort of
																	## ``check everything'' function?
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')

		currentRegion = dbi.getRegionById(data['regionId'])		
		tokensNum = region['tokensNum']
		if  region.tokenBadge != user.currentTokenBadge: raise BadFieldException('badRegion')
		if tokensNum > unitsNum: raise BadFieldException('notEnoughTokensForRedeployment')
		currentRegion.tokensNum = tokensNum		
		unitsNum -= tokensNum

	if 'encampments' in data:
		callSpecialPowerMethod(specialPowerId, 'setEncampments', data['encampments'], tokenBadgeId)

	if 'fortifield' in data:
		callSpecialPowerMethod(specialPowerMethod, 'setFortifield', data['fortifield'], tokenBadgeId)

	if 'heroes' in data:
		callSpecialPowerMethod(specialPowerMethod, 'setHeroes', data['heroes'], 	tokenBadgeId)

	if 'selectFriend' in data:
		callSpecialPowerMethod(specialPowerMethod, 'selectFriend', data['selectFriend'], tokenBadgeId)
			
	if unitsNum: currentRegion.tokensNum += unitsNum
	regions = dbi.query(CurrentRegion).filter(CurrentRegion.tokenBadge.id==user.currentTokenBadge.id).\
								   filter(CurrentTokenBadge.tokensNum == 0)
	for region in regions:
		callRaceMethod(raceId, 'declineRegion', region.tokenBadge)
		callSpecialPowerMethod(specialPowerId, 'declineRegion', region.tokenBadge)		##??
		region.owner = None

	dbi.add(History(user.id, game.id, GAME_REDEPLOY, user.tokenBadge.id))
	return {'result': 'ok'}
		
def endOfGame(coins): #rewrite!11
	return {'result': 'ok', 'coins': coins}

def act_finishTurn(data):
	user = dbi.getUserBySid(data['sid'])
	checkStage(GAME_FINISH_TURN, user)

	income =len(user.regions)
	additionalCoins = 0
	races = dbi.query(TokenBadges).filter_by(ownerId=user.id)
	for rec in races:
		income += callRaceMethod(rec[0], 'countAdditionalCoins', user.id, user.game.id)
		income += callSpecialPowerMethod(rec[1], 'countAdditionalCoins', user.id, user.game.id, user.tokenBadge.raceId)

	user.coins += income
	user.tokensInHand = 0
	#select the next player
	nextPlayer = user.game.getNextPlayer()
	if not nextPlayer:
		nextPlayer = user.game.players[0]
		user.game.turn += 1
		if user.game.turn == user.game.turnsNum:
			return endOfGame(coins)

	for rec in races:
		callRaceMethod(rec.raceId, 'updateBonusStateAtTheAndOfTurn', user.tokenBadge)
		callSpecialPowerMethod(rec.specPowerId, 'updateBonusStateAtTheAndOfTurn', user.tokenBadgeId)

	dbi.add(History(user.id, game.id, GAME_FINISH_TURN, user.tokenBadge.id))
	game.prepareForNextTurn(nextPlayer)
	return {'result': 'ok', 'nextPlayer' : row[0],'coins': coins}

def act_defend(data):
	user = dbi.getUserBySid(data['sid'])

	if not(tokenBadgeId):
		raise BadFieldException('badStage')
	
	checkStage(GAME_DEFEND, gameId)
	attackedRegion = user.game.getDefendingRegionInfo(user)

	raceId, specialPowerId = user.currentTokenBadge.raceId
	tokensNum += callRaceMethod(raceId, 'countAddDefendingTokensNum')

	#find not adjacent regions
	notAdjacentRegions = []
	for region in user.tokenBadge.regions:
		if not region in attackedRegion.getNeighbors(): 
			notAdjacentRegions.extend(region)
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
		destination = dbi.getRegionById(data['regionId'])
		if  notAdjacentRegions and destination not in notAdjacentRegions  or destination.owner != user:
			raise BadFieldException('badRegion')
		
		destination.tokensNum += region['tokensNum']
		tokensNum -= region['tokensNum']
	if tokensNum:  raise BadFieldException('thereAreTokensInTheHand')
	callRaceMethod(raceId, 'updateAttackedTokensNum', user.tokenBadge.id)
	dbi.add(History(user.id, game.id, GAME_DEFEND, user.tokenBadge.id))
	return {'result': 'ok'}

def act_dragonAttack(data):
	user = dbi.getUserBySid(data['sid'])
	if not user.tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_DRAGON_ATTACK, user)
	callSpecialPowerMethod(user.currentTokenBadge.specialPower.id, 'dragonAttack', tokenBadgeId, data['regionId'], 
		data['tokensNum'])
	return {'result': 'ok'}	

def act_enchant(data):
	user = dbi.getUserBySid(data['sid'])
	if not user.tokenBadge: raise BadFieldException('badStage')
	checkStage(GAME_ENCHANT, user)
	callRaceMethod(user.currentTokenBadge.raceId, 'enchant', user.currentTokenBadge.id, data['regionId'])

	return {'result': 'ok'}	

def act_getVisibleTokenBadges(data):
	game = dbi.getGameById(data['gameId'])
	rows = game.tokenBadges()
	result = list()
	for tokenBadge in filter(lambda x: x.position > 0, rows):
		result.append({
			'raceId': races.racesList[tokenBadge.raceId].name, 
			'specialPowerId': races.specialPowerList[tokenBadge.specPowerId].name,
			'position': tokenBadge.position})
	return {'result': result}

def act_throwDice(data):
	user = dbi.getUserBySid(data['sid'])
	if not(user.tokenBadgeId): raise BadFieldException('badStage')
	checkStage(GAME_THROW_DICE, user)
	
	specialPowerId =user.currentTokenBadge.specPowerId
	dice = callSpecialPowerMethod(specialPowerId, 'throwDice')
	dbi.add(History(user.id, game.id, GAME_THROW_DICE, user.tokenBadge.id))
	return {'result': 'ok', 'dice': dice}	


