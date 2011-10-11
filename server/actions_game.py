from checkFields import *
from editDb import query, fetchall, fetchone, lastId
from misc_game import *
from gameExceptions import BadFieldException
from misc import *
	
def act_setReadinessStatus(data):
	sid, userId, gameId = extractValues('Users', ['Sid','Id', 'GameId'],
		[data['sid']])
		
	if not query('SELECT State FROM Games WHERE GameId=%s', gameId):
		raise BadFieldException('notInGame')
	gameState = fetchone()[0]
	if gameState != GAME_WAITING:
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
		query("""UPDATE Users SET Coins=%s, TokensInHand=0, 
			CurrentTokenBadge=NULL, DeclinedTokenBadge=NULL WHERE GameId=%s""", 
			misc.INIT_COINS_NUM, gameId)
		query('SELECT Id FROM Users WHERE GameId=%s ORDER BY Priority', gameId)
		actPlayer = fetchone()[0]
		query("""UPDATE Games SET State=%s, Turn=0, ActivePlayer=%s WHERE 
			GameId=%s""", GAME_PROCESSING, actPlayer, gameId)

		#generate first 6 races
		if (TEST_MODE and 'visibleRaces' in data and 
			'visibleSpecialPowers' in data):
			vRaces = data['visibleRaces']
			vSpecialPowers = data['visibleSpecialPowers']
			for i in range(misc.VISIBLE_RACES):
				showNextRace(gameId, misc.VISIBLE_RACES - 1, 
				vRaces[misc.VISIBLE_RACES - i - 1], 
				vSpecialPowers[misc.VISIBLE_RACES - i - 1])
		else:
			for i in range(misc.VISIBLE_RACES):
				showNextRace(gameId, misc.VISIBLE_RACES - 1)
			
		updateHistory(userId, gameId, GAME_START, None)
	updateGameHistory(gameId, data)	
	return {'result': 'ok'}
	
def act_selectRace(data):
	sid, tokenBadgeId, coins, userId, gameId = extractValues('Users', 
		['Sid', 'CurrentTokenBadge', 'Coins', 'Id', 'GameId'], [data['sid']])
	if tokenBadgeId:
		raise BadFieldException('badStage')

	checkStage(GAME_SELECT_RACE, gameId)
	checkActivePlayer(gameId, userId)
	checkDefendingPlayerNotExists(gameId)

	position, raceId, specialPowerId, tokenBadgeId, bonusMoney = extractValues(
		'TokenBadges', ['Position', 'RaceId', 'SpecialPowerId','TokenBadgeId',
		'BonusMoney'], [data['position']])

	query('SELECT COUNT(*) From TokenBadges WHERE Position>%s', position)
	price = fetchone()[0]
	if coins < price : 
		raise BadFieldException('badMoneyAmount')

	updateHistory(userId, gameId, GAME_SELECT_RACE, tokenBadgeId)

	addUnits =  callRaceMethod(raceId, 'countAdditionalConquerUnits', userId, 
		gameId)
	tokensNum = races.racesList[raceId].initialNum + races.specialPowerList[
		specialPowerId].tokensNum
	query("""UPDATE Users SET CurrentTokenBadge=%s, Coins=Coins-%s+%s, 
		TokensInHand=%s WHERE Sid=%s""", tokenBadgeId, price, bonusMoney, 
		tokensNum + addUnits, sid)
	query("""UPDATE TokenBadges SET OwnerId=%s, InDecline=False, 
		TotalTokensNum=%s, Position=NULL WHERE TokenBadgeId=%s""", userId,
		tokensNum, tokenBadgeId)	

	updateRacesOnDesk(gameId, position)
	updateGameHistory(gameId, data)
	return {'result': 'ok', 'tokenBadgeId': tokenBadgeId }

def act_conquer(data):
	raceId, specialPowerId, tokenBadgeId, userId, gameId = getStandardFields(data, 
		GAME_CONQUER)

	regionId = data['regionId']

	if not query("""SELECT 1 From Games, Users, Regions WHERE Users.Id=%s AND 
		Users.GameId=Games.GameId AND Games.MapId=Regions.MapId AND 
		Regions.RegionId=%s""", userId, regionId):
		raise BadFieldException('badRegionId')

	ownerId, attackedTokenBadgeId, attackedTokensNum, attackedInDecline, regInfo = getRegionInfo(regionId, 
		gameId)
	if ownerId == userId and not attackedInDecline: 
		raise BadFieldException('badRegion')
	if ownerId:
		checkForFriends(userId, ownerId)

	f1 = callRaceMethod(raceId, 'tryToConquerRegion', regionId, tokenBadgeId)
	f2 = callSpecialPowerMethod(specialPowerId, 'tryToConquerRegion', regionId, 
		tokenBadgeId)	
	if not (f1 and f2):
		raise BadFieldException('badRegion')

	if (regInfo['holeInTheGround'] or regInfo['dragon'] or regInfo['hero']):
		raise BadFieldException('regionIsImmune')

	mountain = regInfo['mountain']
	encampment = regInfo['encampment']
	fortress = regInfo['fortress']

	attackedRace = None
	attackedSpecialPower = None
	if attackedTokenBadgeId:
		attackedRace, attackedSpecialPower = getRaceAndPowerIdByTokenBadge(
			attackedTokenBadgeId)
	additionalTokensNum = 0
	if attackedRace:
		additionalTokensNum = callRaceMethod(attackedRace, 
			'countAdditionalConquerPrice')
	unitPrice = max(misc.BASIC_CONQUER_COST + attackedTokensNum + mountain + 
		encampment + fortress + additionalTokensNum + callRaceMethod(raceId, 
		'countConquerBonus', regionId, tokenBadgeId) + callSpecialPowerMethod(
		specialPowerId, 'countConquerBonus', regionId, tokenBadgeId), 1)
		
	query('SELECT TokensInHand FROM Users WHERE Id=%s', userId)
	unitsNum = fetchone()[0]

	dice = -1
	query("""SELECT Dice FROM History WHERE HistoryId=(SELECT MAX(HistoryId) 
		FROM History) AND State=%s""", GAME_THROW_DICE)		
	row = fetchone()
	if row:
		dice = row[0]
		if dice:
			unitPrice -= dice
	elif unitsNum < unitPrice : 
		dice = throwDice()
		unitPrice -= dice
		
	if unitsNum < unitPrice:
		updateHistory(userId, gameId, GAME_UNSUCCESSFULL_CONQUER, tokenBadgeId)
		return {'result': 'badTokensNum', 'dice': dice}

	if attackedTokenBadgeId:
		attackedTokensNum += clearRegionFromRace(regionId, attackedTokenBadgeId)

	query("""UPDATE CurrentRegionState SET OwnerId=%s, TokensNum=%s, 
		InDecline=False, TokenBadgeId=%s WHERE RegionId=%s AND GameId=%s""", 
		userId, unitPrice, tokenBadgeId, regionId, gameId) 
	callRaceMethod(raceId, 'conquered', regionId, tokenBadgeId)
	query('UPDATE Users SET TokensInHand=TokensInHand-%s WHERE Id=%s', unitPrice,
		userId)

	updateHistory(userId, gameId, GAME_CONQUER, tokenBadgeId)
	updateConquerHistory(lastId(), tokenBadgeId, regionId, attackedTokenBadgeId if 
		attackedTokensNum else None, attackedTokensNum, dice, ATTACK_CONQUER)
	updateGameHistory(gameId, data)
	return {'result': 'ok', 'dice': dice} if dice != -1 else {'result': 'ok'}
		
def act_decline(data):
	sid, userId, freeUnits, tokenBadgeId, gameId = extractValues('Users', ['Sid',
		'Id', 'TokensInHand', 'CurrentTokenBadge', 'GameId'], [data['sid']])
	if not(tokenBadgeId):
		raise BadFieldException('badStage')

	checkStage(GAME_DECLINE, gameId)
	checkDefendingPlayerNotExists(gameId)
	checkActivePlayer(gameId, userId)

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	callSpecialPowerMethod(specialPowerId, 'tryToGoInDecline', gameId)
	callSpecialPowerMethod(specialPowerId, 'decline', userId)
	callRaceMethod(raceId, 'decline', userId)	
	query("""UPDATE Users SET DeclinedTokenBadge=%s, CurrentTokenBadge=NULL, 
		TokensInHand=0 WHERE Id=%s""", tokenBadgeId, userId)

	updateHistory(userId, gameId, GAME_DECLINE, tokenBadgeId)
	updateGameHistory(gameId, data)
	return {'result': 'ok'}

def act_redeploy(data):
	raceId, specialPowerId, tokenBadgeId, userId, gameId = getStandardFields(data, 
		GAME_REDEPLOY)

	query('SELECT TotalTokensNum FROM TokenBadges WHERE TokenBadgeId=%s', 
		tokenBadgeId)
	unitsNum = fetchone()[0]
	addUnits = callRaceMethod(raceId, 'countAdditionalRedeploymentUnits', 
		tokenBadgeId, gameId)
	unitsNum += addUnits

	if not unitsNum:
		raise BadFieldException('noTokensForRedeployment')
	query('UPDATE CurrentRegionState SET TokensNum=0 WHERE TokenBadgeId=%s', 
		tokenBadgeId)

	if not query("""SELECT RegionId, COUNT(*) FROM CurrentRegionState WHERE 
		TokenBadgeId=%s""", tokenBadgeId):
		raise BadFieldException('userHasNotRegions') ##better comment?
	regionId, regionsNum = fetchone()
	regions = list()
	for region in data['regions']:
		if not ('regionId' in region and 'tokensNum' in region):
			raise BadFieldException('badJson')
		if not isinstance(region['regionId'], int):
			raise BadFieldException('badRegionId')
		if not isinstance(region['tokensNum'], int):
			raise BadFieldException('badTokensNum')
			
		regionId = extractValues('CurrentRegionState', ['RegionId', 'GameId'], 
			[region['regionId'], gameId])[0]
		tokensNum = region['tokensNum']
		if not query("""SELECT 1 FROM CurrentRegionState WHERE RegionId=%s 
			AND TokenBadgeId=%s""", regionId, tokenBadgeId):
			raise BadFieldException('badRegion')

		if tokensNum > unitsNum:
			raise BadFieldException('notEnoughTokensForRedeployment')

		query("""UPDATE CurrentRegionState SET TokensNum=%s WHERE RegionId=%s 
			AND GameId=%s""", region['tokensNum'], region['regionId'], gameId)
		unitsNum -= tokensNum

	if unitsNum:
		query("""UPDATE CurrentRegionState SET TokensNum=TokensNum+%s WHERE 
			RegionId=%s AND GameId=%s""", unitsNum, regionId, gameId)

	query("""SELECT RegionId FROM CurrentRegionState WHERE TokenBadgeId=%s 
		AND TokensNum=0""", tokenBadgeId)
	regions = fetchall()
	for region in regions:
		callRaceMethod(raceId, 'declineRegion', region[0], gameId)
		callSpecialPowerMethod(specialPowerId, 'declineRegion', region[0], gameId)

	query("""UPDATE CurrentRegionState SET OwnerId=NULL, TokenBadgeId=NULL WHERE 
		TokensNum=0""")
	query("""UPDATE TokenBadges SET TotalTokensNum=TotalTokensNum+%s WHERE 
		TokenBadgeId=%s""", addUnits, tokenBadgeId)

	specAbilities = [
	{'name': 'encampments', 'cmd': 'setEncampments'},
	{'name': 'fortifield', 'cmd': 'setFortifield'},
	{'name': 'heroes', 'cmd': 'setHeroes'}]
	for specAbility in specAbilities:
		if specAbility['name'] in data:
			callSpecialPowerMethod(specialPowerId, specAbility['cmd'], 
				tokenBadgeId, data[specAbility['name']])
	
	updateHistory(userId, gameId, GAME_REDEPLOY, tokenBadgeId)
	updateGameHistory(gameId, data)
	return {'result': 'ok'}
		
def endOfGame(coins): 
	return {'result': 'ok', 'coins': coins}

def act_finishTurn(data):
	sid, userId, gameId, tokenBadgeId, freeUnits, priority = extractValues('Users', 
		 ['Sid', 'Id', 'GameId','CurrentTokenBadge', 'TokensInHand', 'Priority'], 
		 [data['sid']])

	checkStage(GAME_FINISH_TURN, gameId)
	checkDefendingPlayerNotExists(gameId)
	checkActivePlayer(gameId, userId)

	query('SELECT COUNT(*) FROM CurrentRegionState WHERE OwnerId=%s', userId)
	income = fetchone()[0]
	query('SELECT RaceId, SpecialPowerId FROM TokenBadges WHERE OwnerId=%s', userId)
	races = fetchall()
	for rec in races:
		income += callRaceMethod(rec[0], 'countAdditionalCoins', userId, gameId)
		income += callSpecialPowerMethod(rec[1], 'countAdditionalCoins', userId, 
			gameId, rec[0])

	query('UPDATE Users SET Coins=Coins+%s, TokensInHand=0 WHERE Sid=%s',  income, 
		sid)
	query('SELECT Coins FROM Users WHERE Id=%s', userId)
	coins = fetchone()[0]

	query('SELECT Id, CurrentTokenBadge FROM Users WHERE Priority>%s AND GameId=%s',
		priority, gameId)
	row = fetchone()
	if not row:
		query("""SELECT Id, CurrentTokenBadge FROM Users WHERE GameId=%s 
			ORDER BY Priority""", gameId)
		row = fetchone()
		query('UPDATE Games SET Turn=Turn+1 WHERE GameId=%s', gameId)
		query("""SELECT Maps.TurnsNum, Games.Turn FROM Maps, Games WHERE 
			Games.GameId=%s AND Maps.MapId=Games.MapId""", gameId)
		turnsNum, curTurn = fetchone()
		if turnsNum == curTurn:
			return endOfGame(coins)

	for rec in races:
		callRaceMethod(rec[0], 'updateBonusStateAtTheAndOfTurn', tokenBadgeId)
		callSpecialPowerMethod(rec[1], 'updateBonusStateAtTheAndOfTurn', 
			tokenBadgeId)

	updateHistory(userId, gameId, GAME_FINISH_TURN, tokenBadgeId)
	prepareForNextTurn(gameId, row[0], row[1])
	updateGameHistory(gameId, data)
	return {'result': 'ok', 'nextPlayer' : row[0],'coins': coins}

def act_defend(data):
	sid, userId, tokenBadgeId, gameId = extractValues('Users', ['Sid', 'Id', 
		'CurrentTokenBadge', 'GameId'], [data['sid']])
	if not(tokenBadgeId):
		raise BadFieldException('badStage')
	
	checkStage(GAME_DEFEND, gameId)
	regionId, tokensNum = checkForDefendingPlayer(gameId, tokenBadgeId)

	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)
	if not 'regions' in data:
		raise BadFieldException('badJson')

	#find not adjacent regions
	query("""SELECT b.RegionId FROM CurrentRegionState a, CurrentRegionState b 
		WHERE a.RegionId=%s AND a.TokenBadgeId=b.TokenBadgeId AND 
		a.TokenBadgeId=%s AND NOT EXISTS(SELECT 1 FROM AdjacentRegions WHERE 
		FirstRegionId=a.RegionId AND SecondRegionId=b.RegionId)""", 
		regionId, tokenBadgeId)
	notAdjacentRegions = fetchall()
	regions = list()
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

		nextRegion = region['regionId']
		
		if not query("""SELECT 1 FROM CurrentRegionState WHERE RegionId=%s 
			AND OwnerId=%s""", nextRegion, userId):
			raise BadFieldException('badRegion')
			
		if query("""SELECT 1 FROM AdjacentRegions a, Regions b, Regions c WHERE 
			a.FirstRegionId=b.RegionId AND a.SecondRegionId=c.RegionId AND 
			b.RegionId=%s AND c.RegionId=%s AND a.MapId=b.MapId AND 
			b.MapId=c.MapId AND c.MapId=%s""", regionId, nextRegion, 
			getMapIdByTokenBadge(tokenBadgeId)) and notAdjacentRegions:
			raise BadFieldException('badRegion')
		
		regions.append({'regionId': nextRegion, 'tokensNum': region['tokensNum']})
		tokensNum -= region['tokensNum']
		
	if tokensNum:
		raise BadFieldException('thereAreTokensInTheHand')

	for region in regions:
		query("""UPDATE CurrentRegionState SET TokensNum=TokensNum+%s WHERE 
			RegionId=%s AND GameId=%s""", region['tokensNum'], region['regionId'], 
			gameId)
		
	callRaceMethod(raceId, 'updateAttackedTokensNum', tokenBadgeId)
	updateHistory(userId, gameId, GAME_DEFEND, tokenBadgeId)
	updateGameHistory(gameId, data)
	return {'result': 'ok'}

def getStandardFields(data, t):
	sid, userId, gameId, tokenBadgeId = extractValues('Users', ['Sid', 'Id', 
		'GameId', 'CurrentTokenBadge'], [data['sid']])
	if not(tokenBadgeId):
		raise BadFieldException('badStage')

	checkStage(t, gameId)
	checkDefendingPlayerNotExists(gameId)
	checkActivePlayer(gameId, userId)
	
	raceId, specialPowerId = getRaceAndPowerIdByTokenBadge(tokenBadgeId)

	return raceId, specialPowerId, tokenBadgeId, userId, gameId
	
def act_dragonAttack(data):
	fields = getStandardFields(data, GAME_CONQUER)
	callSpecialPowerMethod(fields[1], 'dragonAttack', fields[2], 
		data['regionId'], data['tokensNum'])
	updateGameHistory(fields[4], data)
	return {'result': 'ok'}	

def act_enchant(data):
	fields = getStandardFields(data, GAME_CONQUER)
	callRaceMethod(fields[0], 'enchant', fields[2], data['regionId'])
	updateGameHistory(fields[4], data)
	return {'result': 'ok'}	

def act_throwDice(data):
	fields = getStandardFields(data, GAME_THROW_DICE)
	dice = data['dice'] if misc.TEST_MODE else callSpecialPowerMethod(fields[1], 
		'throwDice')
	updateHistory(fields[3], fields[4], GAME_THROW_DICE, fields[2], dice)
	updateGameHistory(fields[4], data)
	return {'result': 'ok', 'dice': dice}	

def act_getVisibleTokenBadges(data):
	gameId = extractValues('Games', ['GameId'], [data['gameId']])
	return {'result': 'ok', 'visibleTokenBadges': getVisibleTokenBadges(gameId)}

def act_selectFriend(data):
	fields = getStandardFields(data, GAME_CHOOSE_FRIEND)
	callSpecialPowerMethod(fields[1], 'selectFriend', fields[3], fields[4], 
		fields[2], data)
	updateGameHistory(fields[4], data)
	return {'result': 'ok'}

def prepareForNextTurn(gameId, newActPlayer, newTokenBadgeId):
	query('UPDATE Games SET ActivePlayer=%s WHERE GameId=%s', newActPlayer, gameId)
	clearGameStateAtTheEndOfTurn(gameId)
	query("""SELECT TokenBadges.TotalTokensNum, COUNT(*) FROM CurrentRegionState, 
		TokenBadges WHERE CurrentRegionState.OwnerId=%s AND 
		TokenBadges.OwnerId=CurrentRegionState.OwnerId""", newActPlayer)
	unitsNum, regionsNum = fetchone()
	if not unitsNum: unitsNum = 0

	if newTokenBadgeId:
		addUnits =  callRaceMethod(getRaceAndPowerIdByTokenBadge(newTokenBadgeId)[0],
			'countAdditionalConquerUnits', newActPlayer, gameId)

		query("""UPDATE Users SET TokensInHand=(SELECT TotalTokensNum FROM 
			TokenBadges WHERE TokenBadgeId=%s)-(SELECT COUNT(*) FROM 
			CurrentRegionState WHERE TokenBadgeId=%s)+%s WHERE Id=%s""",
			newTokenBadgeId, newTokenBadgeId, addUnits, newActPlayer)
			
		query('UPDATE CurrentRegionState SET TokensNum=1 WHERE TokenBadgeId=%s', 
			newTokenBadgeId)

