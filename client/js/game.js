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
	GAME_LAST_ATTACK = 14,
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
	GAME_LAST_ATTACK];
possiblePrevCmd[GAME_THROW_DICE] = [GAME_SELECT_RACE, GAME_FINISH_TURN, GAME_CONQUER, 
	GAME_DEFEND];
possiblePrevCmd[GAME_DEFEND] = [GAME_CONQUER, GAME_LAST_ATTACK];
possiblePrevCmd[GAME_CHOOSE_FRIEND] = [GAME_REDEPLOY];

Region = $.inherit({
	__constructor: function(id, adjacent, props, ownerId, tokenBadgeId, tokensNum, holeInTheGround,
		encampment, dragon, fortress, hero, inDecline, raceCoords, powerCoords, coords, 
		landscape, bonus, hratio, vratio)
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
		this.raceCoords = raceCoords;
		this.powerCoords = powerCoords;
		this.landscape = landscape;
		this.bonus = bonus;
		this.coords = toPolygon(coords, hratio, vratio);
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
			result += '<p>Encampments: ' + this.encampment + '</p>';
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
		return this.props.some(function(x){return x === prop});
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
			if (this.regions[i].id === id)
				return this.regions[i];

		//what should we do if we didn't find region?
	},

	sortedRegions : function()
	{
		return this.regions.copy().sort(function(a, b) {return a.ownerId > b.ownerId;});
	}
});

Game = $.inherit({
	__constructor: function(id, name, descr, map, state, turn, activePlayerIndex, tokenBadges, players, 
		tokenBadgesInGame, dragonAttacked)
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
		this.dragonAttacked = dragonAttacked;
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
		
	}	
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
			var id = this.id;
			return game().map.regions.filter(function(x){
				return x.tokenBadgeId === id;
				});
		},
		isNeighbor: function(region)
		{
			return this.regions().some(function(x){return x.isAdjacent(region);});
		},
		hasNotAdjacentRegions: function(region)
		{
			return this.regions().some(function(x){return !x.isAdjacent(region);});
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
	{	var id = this.id;
		return game().map.regions.filter(function(x){return x.ownerId === id;});	
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
		this.freePowerTokens = this.specPower().redeployReqName && specPower.bonusNum;
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
				rdRegs[specPower.regPropName][cur.id] = 0 +	cur[specPower.regPropName];
			
		}
		this.freeTokens = Math.max(this.freeTokens, 0);
		if (this.race().deleteAdditionalUnits)
			this.race().deleteAdditionalUnits();
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

createMap = function(mapState, hratio, vratio)
{
	var regions = [];
	for (var i = 0; i < mapState.regions.length; ++i)
	{
		var curReg = mapState.regions[i].currentRegionState;
		regions.push(new Region(i + 1, mapState.regions[i].adjacentRegions, 
			mapState.regions[i].constRegionState, curReg ? curReg.ownerId : undefined, 
			curReg ? curReg.tokenBadgeId : undefined, curReg ? curReg.tokensNum : undefined, 
			curReg ? curReg.holeInTheGround : undefined, curReg ? curReg.encampment : undefined,
			curReg ? curReg.dragon : undefined, curReg ? curReg.fortress : undefined, 
			curReg ? curReg.hero : undefined, curReg ? curReg.inDecline : undefined, 
			mapState.regions[i].raceCoords, mapState.regions[i].powerCoords, 
			mapState.regions[i].coordinates, mapState.regions[i].landscape,
			mapState.regions[i].bonus, hratio, vratio));
	}
	return new Map(mapState.mapId, mapState.playersNum, mapState.turnsNum, mapState.thumbnail, mapState.picture, 
		regions);
};

createGameByState = function(gameState)
{
	if (gameState.ended == true)
	{
		Client.currGameState = undefined;
		Client.currentUser.gameId = undefined;
		Interface.changeOnLeave();
		msg = '***FINISH GAME***\n';
		statistics = gameState['statistics'];
		statistics.sort(function(a, b) { 
			return (a.coins > b.coins || a.coins == b.coins && a.regions > b.regions) ? -1 : 1});
		for (var  i = 0; i < statistics.length; ++i)
			msg += 'Name: ' + statistics[i]['name'] + ', coins: ' + 
				statistics[i]['coins'] + ', regions: ' + statistics[i]['regions'] + '\n';
		msg += '**************\n';
		alert(msg);
		return;
	}
	var mapState = gameState.map,
		conqueredRegion,
		defendingPlayerIndex,
		encampmentsRegions = [],
		map;
	
	if (!Client.currGameState)
	{
		map = createMap(mapState);
		for (var i = 0; i < mapState.regions.length; ++i)
			if (gameState.defendingInfo && i + 1 == gameState.defendingInfo.regionId)
				conqueredRegion = map.regions[i];
		}
	else
	{
		var regionFields = ['ownerId','tokenBadgeId', 'tokensNum', 'holeInTheGround', 'encampment',
			'dragon', 'fortress', 'hero', 'inDecline']
		for (var i = 0; i < mapState.regions.length; ++i)
		{
			for (var j = 0; j < regionFields.length; ++j)
				game().map.regions[i][regionFields[j]] = mapState.regions[i].currentRegionState[regionFields[j]];
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
		player,
		inGame = false;
	for (var i = 0; i < gameState.players.length; ++i)
	{
		if (gameState.players[i].userId == gameState.activePlayerId)
			activePlayerIndex = i;
		inGame = inGame || gameState.players[i].userId === user().id;
		player = (gameState.players[i].userId === user().id) ? user(): 
			new User(gameState.players[i].userId, gameState.players[i].username, undefined, gameState.gameId);
		for (var j = 0; j < userFields.length; ++j)
			player[userFields[j]] = gameState.players[i][userFields[j]];
		if (gameState.players[i].currentTokenBadge)
		{
			player.currentTokenBadge = createTokenBadge(
				gameState.players[i].currentTokenBadge);
			player.currentTokenBadge.inDecline = false;
			tokenBadgesInGame[player.currentTokenBadge.id] = player.currentTokenBadge;
		} else
			player.currentTokenBadge = undefined;
		if (gameState.players[i].declinedTokenBadge)
		{
			player.declinedTokenBadge = createTokenBadge(
				gameState.players[i].declinedTokenBadge);
			player.declinedTokenBadge.inDecline = true;
			tokenBadgesInGame[player.declinedTokenBadge.id] = player.declinedTokenBadge;
		} else
			player.declinedTokenBadge = undefined;
		if (gameState['friendsInfo'] && gameState['friendsInfo']['friendId'] == player.id)
			player.friendId = gameState['friendsInfo']['diplomatId']
		players.push(player);
		if (gameState.defendingInfo && player.id === gameState.defendingInfo.playerId){
			defendingPlayerIndex = i;
		}
	}
	if (!inGame)
		$('#leaveGame, #saveGame').hide();
	var result;
	if (!Client.currGameState)
	{
		result = new Game(gameState.gameId, gameState.gameName, gameState.gameDescription, map, 
			(gameState.state !== GAME_WAITING) ? gameState.lastEvent : gameState.state,
			gameState.currentTurn, activePlayerIndex, tokenBadges, players, tokenBadgesInGame,
			gameState.dragonAttacked)
	}
	else
	{
		game().tokenBadges = tokenBadges.copy();
		game().dragonAttacked = gameState.dragonAttacked;
	        game().enchanted = gameState.enchanted;
		game().tokenBadgesInGame = tokenBadgesInGame.copy();
		game().players = players.copy();
		game().activePlayerIndex = activePlayerIndex;
		game().state = gameState.state !== GAME_WAITING ? 
			gameState.lastEvent : gameState.state;
		game().turn = gameState.currentTurn;
		result = Client.currGameState;
	}											//Redo as quickly as possible
	result.defendingPlayerIndex = defendingPlayerIndex;
	if (defendingPlayerIndex !== undefined && !(game() && game().defendStarted)){
		result.defendingPlayerIndex = defendingPlayerIndex;
		result.redeployRegions = {};
		result.conqueredRegion = conqueredRegion;
	        user().freeTokens = user().tokensInHand;
		if (user().id === result.players[defendingPlayerIndex].id){
			Graphics.update(result.map);
			result.defendStarted = true;
		}
			
	} 
	if (!(game() && (game().redeployStarted || game().defendStarted)))
		user().freeTokens = user().tokensInHand;
	$('#turn').html('Turn: ' + result.turn);
	return result;
};

alreadyAttacked = function(attackType)
{
	switch(attackType)
	{
		case ATTACK_DRAGON:
			return game().dragonAttacked;
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
				result = !(tokenBadge && 
					game().state !== GAME_REDEPLOY && game().state !== GAME_CHOOSE_FRIEND);
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
	return isActivePlayer() && user().currentTokenBadge && getSpecPowByName(user().currentTokenBadge.specPowName).canDecline(user());
}

canFinishTurn = function()
{
	return isActivePlayer() && checkStage(GAME_FINISH_TURN);
}

canBeginConquer = function()
{
	return isActivePlayer() && user().currentTokenBadge &&
		checkStage(GAME_CONQUER) && user().tokensInHand > 0 && 
		!game().redeployStarted;
}

canConquer = function(region)
{
	return (region.ownerId !== user().id  || 
		region.ownerId === user().id && region.inDecline) && 
	!(user().friendId && region.ownerId === user().friendId) &&
	(user().race().canConquer(region, user().currentTokenBadge) &&
	 user().specPower().canConquer(region,user().currentTokenBadge)) 
	 	&& !region.isImmune(false);
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
	return isActivePlayer() && user().currentTokenBadge && checkStage(GAME_CONQUER, ATTACK_DRAGON) &&
		user().tokensInHand > 0 && user().specPower().dragonAttack() &&
		!user().currentTokenBadge.regions().some(function (x){return x.dragon});	
}


canBeginRedeploy = function()
{
	return isActivePlayer() && user().currentTokenBadge && 
		checkStage(GAME_REDEPLOY) && 
		user().currentTokenBadge.regions().length > 0 && 
		user().currentTokenBadge.totalTokensNum;
}

canRedeploy = function(region)
{
	var regions = user().currentTokenBadge.regions();
	return regions.some(function(x){return x.id === region.id;});
}

canBeginDefend = function()
{
	return (isDefendingPlayer() && user().currentTokenBadge && checkStage(GAME_DEFEND));
}

canDefend = function(region)
{
    return region.tokenBadgeId == user().currentTokenBadge.id && !(game().conqueredRegion.isAdjacent(region) && 
		user().currentTokenBadge.hasNotAdjacentRegions(game().conqueredRegion))
}

