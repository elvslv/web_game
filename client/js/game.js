GAME_START = 0;
GAME_WAITING = 1;
GAME_PROCESSING = 2;
GAME_ENDED = 3;
GAME_FINISH_TURN = 4;
GAME_SELECT_RACE = 5;
GAME_CONQUER = 6;
GAME_DECLINE = 7;
GAME_REDEPLOY = 8;
GAME_THROW_DICE = 9;
GAME_DEFEND = 12;
GAME_CHOOSE_FRIEND = 13;
GAME_UNSUCCESSFULL_CONQUER = 14;
possiblePrevCmd = [];
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
	__constructor: function(id, adjacent, props, ownerId, tokenBadgeId, tokensNum, 
		holeInTheGround, encampment, dragon, fortress, hero, inDecline)
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
	adjacent: function(region)
	{
		return region.id in this.adjacent; 
	},
	isImmune: function(enchanting)
	{
		if (this.holeInTheGround || this.dragon || this.hero)
			return true;
		if (enchanting)
			if (this.encampment || !this.tokensNum || this.tokensNum > 1 || this.inDecline)
				return true;
		return false;
	}

});

Map = $.inherit(
{
	__constructor: function(id, playersNum, turnsNum, thmbSrc, pictureSrc, regions)
    {
		this.id = id;
		this.playersNum = playersNum;
		this.turnsNum = turnsNum;
		this.thmbSrc = thmbSrc;
		this.pictureSrc = pictureSrc;
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
	__constructor: function(id, name, descr, map, state, turn, activePlayerIndex, tokenBadges, players)
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
		self.tokenBadges = tokenBadges.copy()
	},
	getTokenBadge: function(pos)
	{
		return seld.tokenBades[pos];
	},
	isStateAllowed: function(state, attackType)
	{
		if (this.activePlayer != Client.currentUser.id)
			return (this.defendingPlayer == Client.currentUser.id || state == GAME_DEFEND);
		result = !(this.state in possiblePrevSmd[state]);
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
			this.totakTokensNum = totalTokensNum;
			this.specPowNum = specPowNum;
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
	}
});

createTokenBadge = function(tokenBadge)
{
	result = new TokenBadge(tokenBadge.tokenBadgeId, tokenBadge.raceName, tokenBadge.specialPowerName,
		tokenBadge.position, tokenBadge.bonusMoney, undefined, tokenBadge.totalTokensNum);
	return result;
}

createGameByState = function(gameState)
{
	if (!Client.currGameState) //we must create map, regions, tokenBadges
	{
		mapState = gameState['map'];
		regions = [];
		for (var i = 0; i < mapState.regions.length; ++i)
		{
			curReg = mapState.regions[i].currentRegionState;
			region.push(new Region(i + 1, mapState.regions[i].adjacentRegions, mapState.regions[i].constRegionState, 
				curReg.ownerId, curReg.tokenBadgeId, curReg.tokensNum, curReg.holeInTheGround, curReg.encampment,
				curReg.dragon, curReg.fortress, curReg.hero, curReg.inDecline));
		}
		map = new Map(mapState.mapId, mapState.playersNum, mapState.turnsNum, mapState.thmbSrc, mapState.pictureSrc, 
			regions);
		tokenBadges = [];
		visibleBadges = gameState.visibleTokenBadges;
		for (var i = 0; i < visibleBadges.length; ++i)
		{
			tokenBadge = new TokenBadge(0, visibleBadges[i].raceName, visibleBadges[i].specialPowerName, i, visibleBadges[i].bonusMoney)
			tokenBadges.push(tokenBadge);
		}
		players = [];
		activePlayerIndex = undefined;
		userFields = ['isReady', 'coins', 'tokensInHand', 'priority', 'inGame'];
		for (var i = 0; i < gameState.players.length; ++i)
		{
			if (gameState.players[i].id == gameState.activePlayerId)
				activePlayerIndex = i;
			if (gameState.players[i].id == Client.currentUser.id)
			{
				player = Client.currentUser;
			}
			else
				player = new User(gameState.players[i].id, gameState.players[i].name, undefined, gameState.gameId);
			for (var j = 0; j < userFields.length; ++j)
				player[userFields[j]] = gameState.players[i][userFields[j]];
			if (player.id == Client.currentUser.id)
			{
				if (!Client.currentUser.currentTokenBadge &&  gameState.players[i].currentTokenBadge || 
					Client.currentUser.currentTokenBadge && Client.currentUser.currentTokenBadge.id != 
					gameState.players[i].currentTokenBadge.tokenBadgeId)
				{
					Client.currentUser.currentTokenBadge = createTokenBadge(
						gameState.players[i].currentTokenBadge);
					Client.currentUser.currentTokenBadge.inDecline = false;
				}
				if (!Client.currentUser.declinedTokenBadge && gameState.players[i].declinedTokenBadge||
					Client.currentUser.declinedTokenBadge && Client.currentUser.declinedTokenBadge.id != 
					gameState.players[i].declinedTokenBadge.tokenBadgeId)
				{
					Client.currentUser.declinedTokenBadge = createTokenBadge(
						gameState.players[i].declinedTokenBadge);
					Client.currentUser.declinedTokenBadge.inDecline = true;
				}
			}
			players.push(player);
				
		}
		result = new Game(gameState.gameId, gameState.gameName, gameState.gameDescription, map, gameState.state,
			gameState.currentTurn, activePlayerIndex, tokenBadges, players);
		return result;
	}
	mapState = gameState['map'];
	regionFields = ['ownerId','tokenBadgeId', 'tokensNum', 'holeInTheGround', 'encampment',
			'dragon', 'fortress', 'hero', 'inDecline']
	for (var i = 0; i < mapState.regions.length; ++i)
		for (var j = 0; j < regionFields.length; ++j)
			Client.currGameState.map.regions[i][regionFields[j]] = mapState.regions[i][regionFields[j]];
	tokenBadges = [];
	visibleBadges = gameState.visibleTokenBadges;
	for (var i = 0; i < visibleBadges.length; ++i)
	{
		tokenBadge = new TokenBadge(0, visibleBadges[i].raceName, visibleBadges[i].specialPowerName, i, visibleBadges[i].bonusMoney)
		tokenBadges.push(tokenBadge);
	}	
	Client.currGameState.tokenBadges = tokenBadges.copy();
	players = [];
	activePlayerIndex = undefined;
	userFields = ['isReady', 'coins', 'tokensInHand', 'priority', 'inGame'];
	for (var i = 0; i < gameState.players.length; ++i)
	{
		if (gameState.players[i].id == gameState.activePlayerId)
			activePlayerIndex = i;
		player = (gameState.players[i].id == Client.currentUser.id) ? player = Client.currentUser : 
			new User(gameState.players[i].id, gameState.players[i].name, undefined, gameState.gameId);
		for (var j = 0; j < userFields.length; ++j)
			player[userFields[j]] = gameState.players[i][userFields[j]];
		if (player.id == Client.currentUser.id)
		{
			if (!Client.currentUser.currentTokenBadge &&  gameState.players[i].currentTokenBadge || 
				Client.currentUser.currentTokenBadge && Client.currentUser.currentTokenBadge.id != 
				gameState.players[i].currentTokenBadge.tokenBadgeId)
			{
				Client.currentUser.currentTokenBadge = createTokenBadge(
					gameState.players[i].currentTokenBadge);
				Client.currentUser.currentTokenBadge.inDecline = false;
			}
			if (!Client.currentUser.declinedTokenBadge && gameState.players[i].declinedTokenBadge||
				Client.currentUser.declinedTokenBadge && Client.currentUser.declinedTokenBadge.id != 
				gameState.players[i].declinedTokenBadge.tokenBadgeId)
			{
				Client.currentUser.declinedTokenBadge = createTokenBadge(
					gameState.players[i].declinedTokenBadge);
				Client.currentUser.declinedTokenBadge.inDecline = true;
			}
		}
		players.push(player);
	}
	Client.currGameState.players = players.copy();
	Client.currGameState.activePlayerIndex = activePlayerIndex;
	return Client.currGameState;
}
