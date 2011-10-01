from checkFields import *
from editDb import query, fetchall, fetchone, lastId
from misc_game import *
from gameExceptions import BadFieldException

def act_setReadinessStatus(data):
	sid, (userId, gameId) = extractValues('Users', 'Sid', data['sid'], 'badSid', 
		True, ['Id', 'GameId'])
	if not query('SELECT State FROM Games WHERE GameId=%s', gameId):
		raise BadFieldException('notInGame')
	gameState = fetchone()[0]
	if gameState != misc.gameStates['waiting']:
		raise BadFieldException('badGameState')

	status = data['isReady']
	query('UPDATE Users SET IsReady=%s WHERE sid=%s', status, sid)
	query("""SELECT Maps.PlayersNum, Games.MapId FROM Games, Maps WHERE 
		Games.GameId=%s AND Games.MapId=Maps.MapId""", gameId)
	maxPlayersNum = fetchone()[0]
	query('SELECT COUNT(*) FROM Users WHERE GameId=%s AND IsReady=1', gameId)
	readyPlayersNum = fetchone()[0]
	if maxPlayersNum == readyPlayersNum:
		# Starting
		query('UPDATE Users SET Coins=%s, TokensInHand=0, CurrentTokenBadge=NULL, \
			DeclinedTokenBadge=NULL WHERE GameId=%s', misc.INIT_COINS_NUM, gameId)
		query('SELECT Id FROM Users WHERE GameId=%s ORDER BY Priority', gameId)
		actPlayer = fetchone()[0]
		query("""UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s, PrevState=%s 
			WHERE GameId=%s""", misc.gameStates['processing'], actPlayer, 
			misc.gameStates['finishTurn'], gameId)

		#generate first 6 races
		for i in range(misc.VISIBLE_RACES):
			showNextRace(gameId, misc.VISIBLE_RACES - 1)
	return {'result': 'ok'}
	
def act_selectRace(data):
	sid, (tokenBadgeId, coins, userId, gameId) = extractValues('Users', 'Sid', 
		data['sid'], 'badSid', True, ['CurrentTokenBadge', 'Coins', 'Id', 'GameId'])

	checkActivePlayer(gameId, userId)

	if tokenBadgeId:
		raise BadFieldException('badStage')
	
	checkForDefendingPlayer(gameId)

	position, (raceId, specialPowerId, tokenBadgeId, bonusMoney) = extractValues(
		'TokenBadges', 'Position', data['position'], 'badPsition', True, 
		['RaceId', 'SpecialPowerId','TokenBadgeId', 'BonusMoney'])
	query('SELECT COUNT(*) From TokenBadges WHERE Position>%s', position)
	price = fetchone()[0]
	if coins < price : 
		raise BadFieldException('badMoneyAmount')

	tokensNum = races.racesList[raceId].initialNum + races.specialPowerList[specialPowerId].tokensNum
	query("""UPDATE Users SET CurrentTokenBadge=%s, Coins=Coins-%s+%s, TokensInHand=%s 
		WHERE Sid=%s""", tokenBadgeId, price, bonusMoney, tokensNum, sid)
	query("""UPDATE TokenBadges SET OwnerId=%s, InDecline=False, SpecialPowerBonusNum=%s, 
		RaceBonusNum=%s, TotalTokensNum=%s, Position=NULL WHERE 
		TokenBadgeId=%s""", userId,	callSpecialPowerMethod(specialPowerId, 
		'getInitBonusNum'), callRaceMethod(raceId, 'getInitBonusNum'), tokensNum,
		tokenBadgeId)	
	query('UPDATE Games SET PrevState=%s', misc.gameStates['selectRace'])
	updateRacesOnDesk(gameId, position)
	return {'result': 'ok', 'tokenBadgeId': tokenBadgeId }

def act_conquer(data):
	sid, (userId, tokenBadgeId, gameId) = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	checkActivePlayer(gameId, userId)
	checkForDefendingPlayer(gameId)		
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	currentRegionId = data['regionId']
	if not query("""SELECT 1 From Games, Users, Regions, CurrentRegionState WHERE 
		Users.Id=%s AND Users.GameId=Games.GameId AND Games.MapId=Regions.MapId AND 
		Regions.RegionId=CurrentRegionState.RegionId AND 
		CurrentRegionState.CurrentRegionId=%s""", userId, currentRegionId):
		raise BadFieldException('badRegionId')

	ownerId, attackedTokenBadgeId, attackedTokensNum, regInfo = getRegionInfo(
		currentRegionId)
	#check the attacking race
	inDecline = 0
	if 'tokenBadgeId' in data:
		tokenBadgeId, raceId, specialPowerId, inDecline = extractValues('TokenBadges', 
		'TokenBadgeId', data['tokenBadgeId'], 'badTokenBadgeId', True, ['RaceId', 'SpecialPowerId',
		'InDecline'])
		if inDecline:
			callRaceMethod(raceId, 'tryToAttackByRaceInDecline')

	if ownerId == userId and not inDecline: 
		raise BadFieldException('badRegion')

	query("""SELECT CurrentRegionId FROM CurrentRegionState WHERE 
		TokenBadgeId=%s""", tokenBadgeId)
	playerRegions = fetchall()
	playerBorderline = False	
	for plRegion in playerRegions:
		query("""SELECT COUNT(*) FROM AdjacentRegions a, CurrentRegionState b,
			CurrentRegionState c WHERE b.RegionId=a.FirstRegionId 
			AND c.RegionId=a.SecondRegionId AND b.CurrentRegionId=%s AND 
			c.CurrentRegionId=%s""", plRegion[0], currentRegionId)
		if fetchone():
			playerBorderline = True
			break
	if playerBorderline: #case for flying and seafaring
		if not callSpecialPowerMethod(specialPowerId, 'tryToConquerAdjacentRegion', 
			playerRegions, regInfo['border'], regInfo['coast'], regInfo['sea']):
			raise BadFieldException('badRegion')

	if not playerBorderline: 
		f1 = callRaceMethod(raceId, 'tryToConquerNotAdjacentRegion', playerRegions, 
				regInfo['border'], regInfo['coast'], currentRegionId, tokenBadgeId)
		f2 = callSpecialPowerMethod(specialPowerId, 'tryToConquerNotAdjacentRegion', 
				playerRegions, regInfo['border'], regInfo['coast'], 
				currentRegionId, tokenBadgeId)
		if not (f1 or f2):
			raise BadFieldException('badRegion')

	if (regInfo['holeInTheGround'] or regInfo['dragon'] or regInfo['hero']):
		raise BadFieldException('badRegion')

	mountain = regInfo['mountain']
	encampment = regInfo['encampment']
	fortress = regInfo['fortress']
	attackedRace = None
	attackedSpecialPower = None
	if attackedTokenBadgeId:
		attackedRace, attackedSpecialPower = getRaceAndPowerIdByTokenBadge(attackedTokenBadgeId)
	additionalTokensNum = 0
	if attackedRace:
		additionalTokensNum = callRaceMethod(attackedRace, 'countAdditionalConquerPrice')
	unitPrice = max(misc.BASIC_CONQUER_COST + attackedTokensNum + mountain + encampment + 
		fortress + additionalTokensNum + callRaceMethod(raceId, 'countConquerBonus', 
		currentRegionId, attackedTokenBadgeId) + callSpecialPowerMethod(raceId, 
		'countConquerBonus', currentRegionId, attackedTokenBadgeId), 1)
	
	query('SELECT TokensInHand FROM Users WHERE Id=%s', userId)
	unitsNum = fetchone()[0]
	query('SELECT Dice FROM Games WHERE GameId=%s', gameId)
	dice = fetchone()[0]
	if dice:
		callSpecialPowerMethod(specialPowerId, 'thrownDice')
		unitsNum += dice

	if unitsNum < unitPrice : 
		dice = throwDice()
		unitPrice -= dice
		if unitsNum < unitPrice:
			raise BadFieldException('badTokensNum')

	query('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE Id=%s', unitPrice, userId)
	if attackedTokenBadgeId:
		clearRegionFromRace(currentRegionId, attackedTokenBadgeId)
	query("""UPDATE CurrentRegionState SET OwnerId=%s, TokensNum=%s, InDecline=%s, TokenBadgeId=%s	
		WHERE CurrentRegionId=%s""", userId, unitPrice, inDecline, tokenBadgeId, 
		currentRegionId) 
	query("""UPDATE Games SET DefendingPlayer=%s, CounqueredRegionsNum=
		CounqueredRegionsNum+1, NonEmptyCounqueredRegionsNum=NonEmptyCounqueredRegionsNum+%s, 
		PrevState=%s, ConqueredRegion=%s, AttackedTokenBadgeId=%s, AttackedTokensNum=%s, 
		Dice=NULL""", ownerId, 1 if attackedTokensNum else 0, misc.gameStates['conquer'], 
		currentRegionId, attackedTokenBadgeId, attackedTokensNum)

	callRaceMethod(raceId, 'conquered', currentRegionId, tokenBadgeId)
	return {'result': 'ok'}
		
def act_decline(data):
	sid, (userId, freeUnits, tokenBadgeId, gameId) = extractValues('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'TokensInHand', 'CurrentTokenBadge', 'GameId'])
	
	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	if not tokenBadgeId:
		raise BadFieldException('badStage')

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'tryToGoInDecline', gameId)
	query("""DELETE FROM TokenBadges WHERE TokenBadgeId=(SELECT DeclinedTokenBadge 
		FROM Users WHERE Users.Id=%s)""", userId)
	query("""UPDATE CurrentRegionState SET OwnerId=NULL, InDecline=0, TokenBadgeId=NULL WHERE OwnerId=%s 
		AND InDecline=1""", userId)
	
	callRaceMethod(raceId, 'setRegionsInDecline', userId)	
	query("""UPDATE Users SET DeclinedTokenBadge=%s, CurrentTokenBadge=NULL, TokensInHand=0 WHERE Sid=%s""", 
		tokenBadgeId, sid)
	query('UPDATE TokenBadges SET SpecialPowerId=NULL WHERE TokenBadgeId=%s', tokenBadgeId)
	query('UPDATE Games SET PrevState=%s', misc.gameStates['decline'])

	return {'result': 'ok'}

def act_redeploy(data):
	sid, (userId, tokenBadgeId, gameId) = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	checkForDefendingPlayer(gameId)
	query('SELECT PrevState FROM Games WHERE GameId=%s', gameId)
	prevState = fetchone()[0]
	if prevState:
		if not prevState in (misc.gameStates['finishTurn'], misc.gameStates['conquer']):
			raise BadFieldException('badStage')
	inDecline = False
	if 'tokenBadgeId' in data:
		tokenBadgeId, inDecline = extractValues('TokenBadges', 'TokenBadgeId', 
			data['tokenBadgeId'], 'badTokenBadgeId', ['InDecline'])
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	if inDecline:
		callRaceMethod(raceId, 'tryToRedeploymentInDeclineRace')

	callRaceMethod(raceId, 'countAdditionalRedeploymentUnits', userId, gameId)
	query('SELECT TotalTokensNum FROM TokenBadges WHERE TokenBadgeId=%s', tokenBadgeId)
	unitsNum = fetchone()[0]
	if not unitsNum:
		raise BadFieldException('noTokensForRedeployment')
	query('UPDATE CurrentRegionState SET TokensNum=0 WHERE TokenBadgeId=%s', tokenBadgeId)

	if not query("""SELECT CurrentRegionId, COUNT(*) FROM CurrentRegionState WHERE 
		TokenBadgeId=%s""", tokenBadgeId):
		raise BadFieldException('userHasNotRegions') ##better comment?
	currentRegionId, regionsNum = fetchone()

	for region in data['regions']:
		if not ('regionId' in region and 'tokensNum' in region):
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')

		currentRegionId = region['regionId']
		tokensNum = region['tokensNum']
		if not query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s 
			AND TokenBadgeId=%s""", currentRegionId, tokenBadgeId):
			raise BadFieldException('badRegion')
		if tokensNum > unitsNum:
			raise BadFieldException('notEnoughTokensForRedeployment')

		query('UPDATE CurrentRegionState SET TokensNum=%s WHERE CurrentRegionId=%s', 
			tokensNum, currentRegionId)
		unitsNum -= tokensNum

	if unitsNum:
		query("""UPDATE CurrentRegionState SET TokensNum=TokensNum+%s WHERE 
			CurrentRegionId=%s""", tokensNum, currentRegionId)
	
	query("""SELECT CurrentRegionId FROM CurrentRegionState WHERE TokenBadgeId=%s 
		AND TokensNum=0""", tokenBadgeId)
	regions = fetchall()
	for region in regions:
		callRaceMethod(raceId, 'declineRegion', region[0])
		callSpecialPowerMethod(specialPowerId, 'declineRegion', region[0])

	query('UPDATE Games SET PrevState=%s', misc.gameStates['redeployment'])
	return {'result': 'ok'}
		
def endOfGame(coins): #rewrite!11
	return {'result': 'ok', 'coins': coins}

def act_finishTurn(data):
	sid, (userId, gameId, tokenBadgeId, freeUnits, priority) = extractValues('Users', 
		'Sid', data['sid'], 'badSid', True, ['Id', 'GameId','CurrentTokenBadge',
		'TokensInHand', 'Priority'])

	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)

	query('SELECT COUNT(*) FROM CurrentRegionState WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	if not income:
		raise BadFieldException('badStage')

	additionalCoins = 0
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE OwnerId=%s', userId)
	races = fetchall()
	for rec in races:
		income += callRaceMethod(rec[0], 'countAdditionalCoins', userId, gameId)
		income += callSpecialPowerMethod(rec[1], 'countAdditionalCoins', userId, gameId, rec[0])

	query('UPDATE Users SET Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s',  income, sid)
	query('SELECT Coins FROM Users WHERE UserId=%s', userId)
	coins = fecthone()[0]
	#check for the end of game		
	query("""SELECT Maps.TurnsNum, Games.Turn FROM Maps, Games WHERE Games.GameId=%s AND 
			Maps.MapId=Games.MapId""", gameId)
	turnsNum, curTurn = fetchone()
	if turnsNum == curTurn + 1:
		return endOfGame(coins)

	#select the next player
	query('SELECT Id, CurrentTokenBadge, TokensInHand FROM Users WHERE Priority>%s AND GameId=%s',
		priority, gameId)
	row = fetchone()
	if not row:
		query("""SELECT Id, CurrentTokenBadge, TokensInHand FROM Users WHERE GameId=%s 
			ORDER BY Priority""", gameId)
		row = fetchone()
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)

	newActPlayer, newTokenBadgeId, tokensInHand = row
	query('UPDATE Games SET ActivePlayer=%s WHERE GameId=%s', newActPlayer, gameId)
	query("""SELECT TokenBadges.TotalTokensNum, COUNT(*) FROM CurrentRegionState, 
		TokenBadges WHERE CurrentRegionState.OwnerId=%s AND 
		TokenBadges.OwnerId=CurrentRegionState.OwnerId""", newActPlayer)
	unitsNum, regionsNum = fetchone()
	if not unitsNum: unitsNum = 0

	#	Gathering troops
	query('UPDATE Users SET TokensInHand=%s WHERE Id=%s', unitsNum - regionsNum,  
		newActPlayer)
	query('UPDATE CurrentRegionState SET TokensNum=1 WHERE TokenBadgeId=%s', newTokenBadgeId)

	for rec in races:
		callRaceMethod(rec[0], 'updateBonusStateAtTheAndOfTurn', tokenBadgeId)
		callSpecialPowerMethod(rec[1], 'updateBonusStateAtTheAndOfTurn', 
			tokenBadgeId)

	query('UPDATE Games SET PrevState=%s', misc.gameStates['finishTurn'])
	return {'result': 'ok', 'nextPlayer' : newActPlayer,'coins': coins}

def act_defend(data):
	sid, (userId, tokenBadgeId, gameId) = extractValues('Users', 'Sid', data['sid'], 
		'badSid', True, ['Id', 'CurrentTokenBadge', 'GameId'])
	if not query("""SELECT AttackedTokenBadgeId, ConqueredRegion, AttackedTokensNum 
		FROM Games WHERE GameId=%s AND DefendingPlayer=%s""", gameId, userId):
		raise BadFieldException('badStage') ##better comment?
	raceId, currentRegionId, tokensNum = fetchone()
	tokensNum += callRaceMethod(raceId, 'updateAttackedTokensNum', tokenBadgeId)
	if not 'regions' in data:
		raise BadFieldException('badJson')

	#find not adjacent regions
	query("""SELECT b.CurrentRegionId FROM CurrentRegionState a, CurrentRegionState b 
		WHERE a.CurrentRegionId=%s AND a.TokenBadgeId=b.TokenBadgeId AND 
		a.TokenBadgeId=%s AND NOT EXISTS(SELECT 1 FROM AdjacentRegions WHERE 
		FirstRegionId=a.RegionId AND SecondRegionId=b.RegionId)""", 
		currentRegionId, tokenBadgeId)
	notAdjacentRegions = fetchall()
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
		if not query("""SELECT 1 FROM CurrentRegionState WHERE CurrentRegionId=%s 
			AND OwnerId=%s""", region['regionId'], userId):
			raise BadFieldException('badRegion')
		if query("""SELECT 1 FROM AdjacentRegions a, CurrentRegionState b, 
			CurrentRegionState c WHERE a.FirstRegionId=b.RegionId AND 
			a.SecondRegionId=c.RegionId AND b.CurrentRegionId=%s AND 
			c.CurrentRegionId=%s""", currentRegionId, region['regionId']) and notAdjacentRegions:
			raise BadFieldException('badRegion')
		
		query("""UPDATE CurrentRegionState SET TokensNum=TokensNum+%s WHERE 
			CurrentRegionId=%s""", region['tokensNum'], region['regionId'])
		tokensNum -= region['tokensNum']
	
	if tokensNum:
		raise BadFieldException('thereAreTokensInTheHand')
	query('UPDATE Games SET DefendingPlayer=NULL WHERE GameId=%s', gameId)
	return {'result': 'ok'}

def act_dragonAttack(data):
	sid, (userId, gameId, tokenBadgeId)= extractValues('Users', 'Sid', data['sid'], 
		'badSid', ['Id', 'GameId', 'CurrentTokenBadge'])
	
	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'dragonAttack', tokenBadgeId, data['regionId'], 
		data['tokensNum'])

	query('UPDATE Games SET PrevState=%s', misc.gameStates['conquer'])
	return {'result': 'ok'}	

def act_enchant(data):
	sid, (userId, gameId, tokenBadgeId)= extractValues('Users', 'Sid', data['sid'], 
		'badSid', ['Id', 'GameId', 'CurrentTokenBadge'])

	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(raceId, 'enchant', tokenBadgeId, data['regionId'])

	query('UPDATE Games SET PrevState=%s', misc.gameStates['conquer'])
	return {'result': 'ok'}	

def act_breakEncampment(data):
	sid, (userId, gameId, tokenBadgeId)= extractValues('Users', 'Sid', data['sid'], 
		'badSid', ['Id', 'GameId', 'CurrentTokenBadge'])

	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'breakEncampment', tokenBadgeId, 
		data['regionId'], data['encampmentsNum'])

	return {'result': 'ok'}	

def act_setEncampment(data):
	sid, (userId, gameId, tokenBadgeId)= extractValues('Users', 'Sid', data['sid'], 
		'badSid', ['Id', 'GameId', 'CurrentTokenBadge'])
	
	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'setEncampment', tokenBadgeId, 
		data['regionId'], data['encampmentsNum'])

	return {'result': 'ok'}	

def act_getVisibleTokenBadges(data):
	gameId = extractValues('Games', 'GameId', data['gameId'], 'badGameId', True)[0]
	query("""SELECT RaceId, SpecialPowerId, Position FROM TokenBadges WHERE
		GameId=%s AND Position>=0 ORDER BY Position ASC""", gameId)
	rows = fetchall()
	result = list()
	for tokenBadge in rows:
		result.append({
			'raceId': races.racesList[tokenBadge[0]].name, 
			'specialPowerId': races.specialPowerList[tokenBadge[1]].name,
			'position': tokenBadge[2]})
	return {'result': result}

def act_throwDice(data):
	sid, (userId, gameId, tokenBadgeId)= extractValues('Users', 'Sid', data['sid'], 
		'badSid', ['Id', 'GameId', 'CurrentTokenBadge'])
	
	checkForDefendingPlayer(gameId)
	checkActivePlayer(gameId, userId)
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	dice = callSpecialPowerMethod(specialPowerId, 'throwDice')
	query('UPDATE Games SET Dice WHERE GameId=%s', gameId)
	return {'result': 'ok', 'dice': dice}	