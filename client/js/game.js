var GAME_START = 0,
	GAME_WAITING = 1,
	GAME_PROCESSING = 2,
	GAME_ENDED = 3,
	GAME_FINISH_TURN = 4,
	GAME_SELECT_RACE = 5,
	GAME_CONQUER = 6,
	GAME_DECLINE = 7,
	GAME_REDEPLOY = 8,
	GAME_THROW_DICE = 9,
	GAME_DEFEND = 12,
	GAME_CHOOSE_FRIEND = 13,
	GAME_UNSUCCESSFULL_CONQUER = 14,
	ATTACK_CONQUER = 0,
	ATTACK_DRAGON = 1,
	ATTACK_ENCHANT = 2;
	
var possiblePrevCmd = [];
possiblePrevCmd[GAME_FINISH_TURN] = [GAME_DECLINE, GAME_REDEPLOY, GAME_CHOOSE_FRIEND];
possiblePrevCmd[GAME_SELECT_RACE] = [GAME_START, GAME_FINISH_TURN];
possiblePrevCmd[GAME_CONQUER] = [GAME_CONQUER, GAME_SELECT_RACE, GAME_FINISH_TURN,
	GAME_THROW_DICE, GAME_DEFEND];
possiblePrevCmd[GAME_DECLINE] = [GAME_FINISH_TURN, GAME_REDEPLOY];
possiblePrevCmd[GAME_REDEPLOY] = [GAME_CONQUER, GAME_THROW_DICE, GAME_DEFEND, 
	GAME_UNSUCCESSFULL_CONQUER];
possiblePrevCmd[GAME_THROW_DICE] = [GAME_SELECT_RACE, GAME_FINISH_TURN, GAME_CONQUER, 
	GAME_DEFEND];
possiblePrevCmd[GAME_DEFEND] = [GAME_CONQUER];
possiblePrevCmd[GAME_CHOOSE_FRIEND] = [GAME_REDEPLOY];

Region = $.inherit({
	__constructor: function(id, adjacent, props, ownerId, tokenBadgeId, tokensNum, holeInTheGround,
		encampment, dragon, fortress, hero, inDecline, raceCoords, powerCoords, coords)
	{
		this.id = id;							
		this.adjacent = adjacent.copy();
		this.props = props.copy();
		this.ownerId = ownerId;
		this.tokenBadgeId = tokenBadgeId;
		this.tokensNum = tokensNum;
		this.holeInTheGround = holeInTheGround;
		this.encampment = encampment;
		this.dragon = dragon; 
		this.fortress = fortress; 
		this.hero = hero;
		this.inDecline = inDecline;
		this.raceCoords = parseArray(raceCoords);
		this.powerCoords = parseArray(powerCoords);
		this.coords = toPolygon(parseArray(coords));
	},
	htmlRegionInfo: function()
	{
		result = 'Properties:';
		for (var i = 0; i < this.props.length; ++i)
			result += '<p>' + this.props[i] + '</p>';
		if (this.ownerId)
			result += '<p>Owner: ' + this.ownerId + '</p>';
		if (this.tokensNum)
			result += '<p>Number of tokens: ' + this.tokensNum + '</p>';
		if (this.holeInTheGround)
			result += '<p>Hole in the ground</p>';
		if (this.encampment)
			result += '<p>Encampment</p>';
		if (this.dragon)
			result += '<p>Dragon</p>';
		if (this.fortress)
			result += '<p>Fortress</p>';
		if (this.hero)
			result += '<p>Hero</p>';
		if (this.inDecline)
			result += '<p>Declined</p>';
		return result;
	},
	hasProperty: function(prop)
	{
		for (var i = 0; i < this.props.length; ++i)
			if (this.props[i] == prop)
				return true;
		return false;
	},
	getNeighbors: function()
	{
		return  this.adjacent; 
	},
	isAdjacent: function(region)
	{
		return includes(region.id, this.adjacent); 
	},
	isImmune: function(enchanting)
	{
		return this.holeInTheGround || this.dragon || this.hero ||
			(enchanting && 
				(this.encampment || !this.tokensNum || 
				this.tokensNum > 1 || this.inDecline));
	},
	getTokenBadge : function()
	{
		return game().tokenBadgesInGame[this.tokenBadgeId];
	},

	getOwner : function()
	{
		return game().players[this.ownerId];
	}
		
});

Map = $.inherit(
{
	__constructor: function(id, playersNum, turnsNum, thmbSrc, pictureSrc, regions)
    {
		this.id = id;
		this.playersNum = playersNum;
		this.turnsNum = turnsNum;
		this.thumbnail = thmbSrc;
		this.picture = pictureSrc;
		this.regions = regions.copy();
    },
    getRegion: function(id)
	{
		for (var i = 0; i < this.regions.length; ++i)
			if (this.regions[i].id == id)
				return this.regions[i];

		//what should we do if we didn't find region?
	}
});

Game = $.inherit({
	__constructor: function(id, name, descr, map, state, turn, activePlayerIndex, tokenBadges, players, 
		tokenBadgesInGame)
	{
		this.id = id;
		this.name = name;
		this.descr = descr;
		this.map = map;
		this.state = state;
		this.turn = turn;
		this.activePlayerIndex = activePlayerIndex;
		this.tokenBadges = tokenBadges.copy();
		this.players = players.copy();
		this.tokenBadgesInGame = tokenBadgesInGame.copy();
		this.redeployStarted = false;
	},
	setState: function(state)
	{
		this.state = state;
	},
	setTurn: function(turn)
	{
		this.turn = turn;
	},
	setActivePlayer: function(activePlayerIndex)
	{
		this.activePlayerIndex = activePlayerIndex;
	},
	setTokenBadges: function(tokenBadges)
	{
		this.tokenBadges = tokenBadges.copy()
	},
	getTokenBadge: function(pos)
	{
		return this.tokenBades[pos];
	},
	isStateAllowed: function(state, attackType)
	{
		if (this.activePlayer != Client.currentUser.id)
			return (this.defendingPlayer == Client.currentUser.id || state == GAME_DEFEND);
		result = !(includes(this.state, possiblePrevSmd[state]));
		//add checking of attacking type
		
	},
	setDefendingPlayer: function(playerId)
	{
		this.defendingPlayer = playerId;
	},
	setActivePlayer: function(playerId)
	{
		this.activePlayer = playerId;
	},
	//must add defending info in protocol
	
});

TokenBadge = $.inherit({
		__constructor: function(id, raceName, specPowName, pos, bonusMoney, inDecline,
			totalTokensNum, specPowNum)
		{
			this.id = id;
			this.raceName = raceName;
			this.specPowName = specPowName;
			this.pos = pos;
			this.bonusMoney = bonusMoney;
			this.inDecline = inDecline;
			this.totalTokensNum = totalTokensNum;
			this.specPowNum = specPowNum;
		},
		regions: function()
		{	
			result = [];
			for (var i = 0; i < Client.currGameState.map.regions.length; ++i)
				if (Client.currGameState.map.regions[i].tokenBadgeId == this.id)
					result.push(Client.currGameState.map.regions[i]);
			return result;	
		},
		isNeighbor: function(region)
		{
			var regions = this.regions();
			for (var i = 0; i < regions.length; ++i)
				for (var j = 0; j < regions[i].adjacent.length; ++j)
					if (regions[i].adjacent[j] == region.id)
						return true; 
			return false;
		},
		hasNotAdjacentRegions: function(region)
		{
			var regions = this.regions();
			for (var i = 0; i < regions.length; ++i)
			{
				for (var j = 0; j < regions[i].adjacent.length; ++j)
					if (regions[i].adjacent[j] == region.id)
						break; 
				if (j == regions[i].adjacent.length)
					return true;
			}
		},
		getRace : function()
		{
			return getRaceByName(this.raceName);
		},
		getPower : function()
		{
			return getSpecPowByName(this.specPowName);
		}
			
});


User = $.inherit({
	__constructor: function(id, username, sid, gameId, isReady, coins, tokensInHand, priority, inGame, 
		currentTokenBadge, declinedTokenBadge)
	{
		this.id = id;
		this.username = username;
		this.sid = sid;
		this.gameId = gameId; 
		this.isReady = isReady;
		this.currentTokenBadge = currentTokenBadge;
		this.declinedTokenBadge = declinedTokenBadge;
		this.coins = coins;
		this.tokensInHand = tokensInHand;
		this.priority = priority;
		this.inGame = inGame;
		
	},
	//add info for friends in protocol!
	killRaceInDecline: function()
	{
		for (var i = 0; i < Client.currGameState.map.regions.length; ++i)
		{
			if (Client.currGameState.map.regions[i].ownerId = this.id)
			{
				Client.currGameState.map.regions[i].owner = undefined;
				Client.currGameState.map.regions[i].inDecline = false;
			}
		}
	},
	regions: function()
	{	
		var result = [];
		for (var i = 0; i < Client.currGameState.map.regions; ++i)
			if (Client.currGameState.map.regions[i].ownerId == this.id)
				result.push(Client.currGameState.map.regions[i]);
		return result;	
	},
	startRedeploy: function()
	{
		var regions = this.currentTokenBadge.regions(),
			specPower = this.specPower(),
			init = function(elt, obj){	
				return elt === undefined ? (obj ? {} : 0) : elt;
			},
			cur, regs;
											
		this.freeTokens = this.currentTokenBadge.totalTokensNum;
		this.freePowerTokens = specPower.bonusNum;
		
		game().redeployRegions = {};
		rdRegs = game().redeployRegions;
		for (var i = 0; i < regions.length; ++i)
		{
			cur = regions[i];
			rdRegs[cur.id] = init(rdRegs[cur.id]);
			rdRegs[specPower.regPropName] = init(rdRegs[specPower.regPropName], true);
			rdRegs[specPower.regPropName][cur.id] = 
				init(rdRegs[specPower.regPropName][cur.id]);
			rdRegs[cur.id] = cur.tokensNum;
			this.freeTokens -= cur.tokensNum;
			this.freePowerTokens -= cur[specPower.regPropName];
			if (specPower.needRedeploy())
				rdRegs[specPower.regPropName][cur.id] =
					cur[specPower.regPropName];
			
		}
		this.freeTokens += getRaceByName(this.currentTokenBadge.raceName).turnEndReinforcements(this);
		this.freeTokens = Math.max(this.freeTokens, 0);
		Graphics.drawFreeBadges();
	
	},

	specPower : function()
	{
		return user().currentTokenBadge && 
			user().currentTokenBadge.getPower();
	},

	race : function()
	{
		return user().currentTokenBadge && 
			user().currentTokenBadge.getRace();
	}
	
});

createTokenBadge = function(tokenBadge)
{
	return new TokenBadge(tokenBadge.tokenBadgeId, tokenBadge.raceName, tokenBadge.specialPowerName,
		tokenBadge.position, tokenBadge.bonusMoney, undefined, tokenBadge.totalTokensNum);
};

createGameByState = function(gameState)
{
	var mapState = gameState.map,
		conqueredRegion,
		defendingPlayerIndex,
		encampmentsRegions = [],
		victimTokensNum = gameState.defendingInfo && gameState.defendingInfo.tokensNum;
	
	if (!Client.currGameState)
	{
		var regions = [];
		for (var i = 0; i < mapState.regions.length; ++i)
		{
			var curReg = mapState.regions[i].currentRegionState;
			regions.push(new Region(i + 1, mapState.regions[i].adjacentRegions, 
				mapState.regions[i].constRegionState, 
				curReg.ownerId, curReg.tokenBadgeId, curReg.tokensNum, curReg.holeInTheGround, curReg.encampment,
				curReg.dragon, curReg.fortress, curReg.hero, curReg.inDecline, 
				mapState.regions[i].raceCoords, mapState.regions[i].powerCoords, 
				mapState.regions[i].coordinates));

			if (gameState.defendingInfo && i + 1 == gameState.defendingInfo.regionId)
				conqueredRegion = regions[i];
		}
		var map = new Map(mapState.mapId, mapState.playersNum, mapState.turnsNum, mapState.thumbnail, mapState.picture, 
			regions);
	}
	else
	{
		var regionFields = ['ownerId','tokenBadgeId', 'tokensNum', 'holeInTheGround', 'encampment',
		'dragon', 'fortress', 'hero', 'inDecline']
		for (var i = 0; i < mapState.regions.length; ++i)
		{
			for (var j = 0; j < regionFields.length; ++j)
				Client.currGameState.map.regions[i][regionFields[j]] = mapState.regions[i].currentRegionState[regionFields[j]];
			if (gameState.defendingInfo && 
				game().map.regions[i].id === gameState.defendingInfo.regionId)
				conqueredRegion = game().map.regions[i];
		}
	}
	var tokenBadges = [], tokenBadge,
		visibleBadges = gameState.visibleTokenBadges;
	for (var i = 0; i < visibleBadges.length; ++i)
	{
		tokenBadge = new TokenBadge(0, visibleBadges[i].raceName, visibleBadges[i].specialPowerName, i, visibleBadges[i].bonusMoney)
		tokenBadges.push(tokenBadge);
	}	
	var tokenBadgesInGame = [],
		players = [], activePlayerIndex,
		userFields = ['isReady', 'coins', 'tokensInHand', 'priority', 'inGame'],
		player;
	for (var i = 0; i < gameState.players.length; ++i)
	{
		if (gameState.players[i].id == gameState.activePlayerId)
			activePlayerIndex = i;
		player = (gameState.players[i].id == Client.currentUser.id) ? player = Client.currentUser : 
			new User(gameState.players[i].id, gameState.players[i].name, undefined, gameState.gameId);
		for (var j = 0; j < userFields.length; ++j)
			player[userFields[j]] = gameState.players[i][userFields[j]];
		if (gameState.players[i].currentTokenBadge)
		{
			player.currentTokenBadge = createTokenBadge(
				gameState.players[i].currentTokenBadge);
			player.currentTokenBadge.inDecline = false;
			tokenBadgesInGame[player.currentTokenBadge.id] = player.currentTokenBadge;
		}
		if (gameState.players[i].declinedTokenBadge)
		{
			player.declinedTokenBadge = createTokenBadge(
				gameState.players[i].declinedTokenBadge);
			player.declinedTokenBadge.inDecline = true;
			tokenBadgesInGame[player.declinedTokenBadge.id] = player.declinedTokenBadge;
		}
		if (gameState['friendsInfo'] && gameState['friendsInfo']['slaveId'] == player.id)
			player.friendId = gameState['friendsInfo']['masterId']
			
		players.push(player);
		if (gameState.defendingInfo && player.id == gameState.defendingInfo.playerId){
			defendingPlayerIndex = i;
		}
		console.log(defendingPlayerIndex);
	}
	var result;
	if (!Client.currGameState)
	{
		result = new Game(gameState.gameId, gameState.gameName, gameState.gameDescription, map, 
			(gameState.state == GAME_START) ? gameState.lastEvent : gameState.state,
			gameState.currentTurn, activePlayerIndex, tokenBadges, players, tokenBadgesInGame)
	}
	else
	{
		game().tokenBadges = tokenBadges.copy();
		game().tokenBadgesInGame = tokenBadgesInGame.copy();
		game().players = players.copy();
		game().activePlayerIndex = activePlayerIndex;
		game().state = gameState.state === GAME_START ? 
			gameState.lastEvent : gameState.state;
		result = Client.currGameState;
	}											//Redo as quickly as possible
	if (defendingPlayerIndex !== undefined && !(game() && game().defendStarted)){
		result.defendingPlayerIndex = defendingPlayerIndex;
		result.defendStarted = true;
		result.players[defendingPlayerIndex].freeTokens = victimTokensNum;
		result.redeployRegions = {};
		result.conqueredRegion = conqueredRegion;
	}
	return result;
};

alreadyAttacked = function(attackType)
{
	switch(attackType)
	{
		case ATTACK_DRAGON:
			break;
		case ATTACK_ENCHANT:
			break;
	}
	return false;
}

checkStage = function(newState, attackType)
{
	var result = includes(Client.currGameState.state, possiblePrevCmd[newState]);
	if (result)
	{
		switch(newState)
		{
			case GAME_FINISH_TURN:
				tokenBadge = user().currentTokenBadge;
				result = !(tokenBadge && getRaceByName(tokenBadge.raceName).needRedeployment() && 
					game().state != GAME_REDEPLOY && game().state != GAME_CHOOSE_FRIEND);
				break;
			case GAME_CONQUER:
				//check for dice!!!
				if (alreadyAttacked(attackType))
					result = false;
				break;
			case GAME_CHOOSE_FRIEND:
				//check if can select friend 
				break;
		}
	}
	return result;
}

isDefendingPlayer = function()
{
	return (game().defendingPlayerIndex !== undefined && 
		game().players[game().defendingPlayerIndex].id === user().id); 
}

isActivePlayer = function()
{
	return game().defendingPlayerIndex === undefined && 
		game().activePlayerIndex !==  undefined && 
		game().players[game().activePlayerIndex].id == user().id; 
}

canSelectRaces = function()
{
	return isActivePlayer() && !user().currentTokenBadge && 
		checkStage(GAME_SELECT_RACE);
}

canSelectRace = function(i)
{
	return user().coins >= 5 - i;
}

canDecline = function()
{
	return isActivePlayer() && user().currentTokenBadge && 
		getSpecPowByName(user().currentTokenBadge.specPowName).canDecline(user());
}

canFinishTurn = function()
{
	return isActivePlayer() && checkStage(GAME_FINISH_TURN);
}

canBeginConquer = function()
{
	return isActivePlayer() && user().currentTokenBadge &&
		checkStage(GAME_CONQUER) && user().tokensInHand > 0;
}

canConquer = function(region)
{
	return (region.ownerId !== user().id  || 
		region.ownerId === user().id && region.inDecline) && 
	!(user().friendId && region.id === user().friendId) &&
	(getRaceByName(user().currentTokenBadge.raceName)
		.canConquer(region, user().currentTokenBadge) ||
	getSpecPowByName(user().currentTokenBadge.specPowName)
		.canConquer(region,user().currentTokenBadge)) && !region.isImmune(false);
}

canChooseFriend = function()
{
	var result = user().currentTokenBadge != undefined && checkStage(GAME_CHOOSE_FRIEND);
	if (result)
	{
		specialPower = getSpecPowByName(user().currentTokenBadge.specPowName);
		result = specialPower.canChooseFriend();
	}
	return result;
}

selectFriend = function(user)
{
	var specialPower = getSpecPowByName(Client.currentUser.currentTokenBadge.specPowName);
	return specialPower.selectFriend(user);
}

canThrowDice = function()
{
	return isActivePlayer() && checkStage(GAME_THROW_DICE) && 
		user().currentTokenBadge !== undefined && 
		getSpecPowByName(user().currentTokenBadge.specPowName).throwDice();
}

canBeginEnchant = function()
{
	var result = (isActivePlayer() && user().currentTokenBadge && checkStage(GAME_CONQUER, ATTACK_ENCHANT)) ;
	if (result)
	{
		race = getRaceByName(user().currentTokenBadge.raceName);
		result = race.canEnchant();
	}
	return result;
}

canEnchant = function(region)
{
	return getRaceByName(user().currentTokenBadge.raceName).enchant(region);
	
}

canBeginDragonAttack = function()
{
	var result = (isActivePlayer() && user().currentTokenBadge && checkStage(GAME_CONQUER, ATTACK_DRAGON) &&
		user().tokensInHand > 0) ;	//how so
	if (result)
	{
		specialPower = getSpecPowByName(user().currentTokenBadge.specPowName);
		result = specialPower.canBeginDragonAttack();
	}
	return result;
}

canDragonAttack = function(region)
{
	return getSpecPowByName(user().currentTokenBadge.specPowName).dragonAttack(region);
	
}

canBeginRedeploy = function()
{
	return isActivePlayer() && user().currentTokenBadge && 
		checkStage(GAME_REDEPLOY) && 
		user().currentTokenBadge.regions().length > 0 && 
		user().currentTokenBadge.totalTokensNum + 
		getRaceByName(user().currentTokenBadge.raceName).turnEndReinforcements(user()) > 0;
}

canRedeploy = function(region)
{
	var regions = user().currentTokenBadge.regions();
	for (var i = 0; i < regions.length; ++i)
		if (regions[i].id == region.id)
			return true;
	return false;
}

canBeginDefend = function()
{
	return (isDefendingPlayer() && user().currentTokenBadge && checkStage(GAME_DEFEND));
}

canDefend = function(region)
{
	return region.ownerId == user().id && !(game().conqueredRegion.isAdjacent(region) && 
		user().currentTokenBadge.hasNotAdjacentRegions(game().conqueredRegion))
}

