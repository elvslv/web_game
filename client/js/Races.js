BaseRace = $.inherit({
	__constructor: function(name, initialNum, maxNum)
	{
		this.name = name;
		this.initialNum = initialNum;
		this.maxNum = maxNum;
	},
	setId: function(id)
	{
		this.id = id;
	},
	canConquer: function(region, tokenBadge)
	{
		return !tokenBadge.regions().length &&
			(region.hasProperty('coast') || region.hasProperty('border'));
	},
	attackBonus: function(region, tokenBadge)
	{
		return 0;
	},
	decline: function(user)
	{
		user.declinedTokenBadge = user.currentTokenBadge;
		var regions = user.declinedTokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
		{
			regions[i].tokensNum = 1;
			regions[i].inDecline = True;
		}
		user.declinedTokenBadge.inDecline = True;
		user.declinedTokenBadge.totalTokensNum = regions.length;
		user.tokensInHand = 0;
	},
	turnEndReinforcements: function(user)
	{
		return 0;
	},
	turnStartReinforcements: function(user)
	{
		return 0;
	},
	needRedeployment: function()
	{
		return false;
	},
	incomeBonus: function(user)
	{
		return 0;
	},
	defenseBonus: function()
	{
		return 0;
	},
	updateBonusStateAtTheEndOfTurn: function(tokenBadgeId)
	{
		return;
	},
	conquered: function(regionId, tokenBadgeId)
	{
		return;
	},
	enchant: function(region)
	{
		return false;
	},
	canEnchant: function()
	{
		return false;
	},
	clearRegion: function(tokenBadge, region)
	{
		region.encampent = 0;
		region.fortress = false;
		region.dragon = false;
		region.holeInTheGround = false;
		region.hero = false;
		return -1;
	},
	sufferCasualties: function(tokenBadge)
	{
		tokenBadge.totalTokensNum -= 1;
		return -1;
	},
	getPic : function(declined)
	{
		n = this.name ? this.name + ' ' : ''; 
		return "css/images/races/" + n + "small" + 
			(declined ? " decline.jpg" : ".jpg"); 
	}
	

});
	
RaceHalflings = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Halflings', 6, 11);
	},
	conquered: function(region, tokenBadge)
	{
		regions = tokenBadge.regions();
		if (regions.length >= 2)
			return;
		for (var i = 0; i < regions.length; ++i)
			regions[i].holeInTheGround = true;
	},
	canConquer: function(region, tokenBadge)
	{
		return true;
	},
	getInitBonusNum: function()
	{
		return 2;
	},
	decline: function()
	{
		this.__base(user);
		var regions = user.currentTokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			regions[i].holeInTheGround = false;
	},
	clearRegion: function(tokenBadge, region)
	{
		region.holeInTheGround = false;
	}
});

RaceGiants = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Giants', 6, 11);
	},
	attackBonus: function(region, tokenBadge)
	{
		var res = 0, 
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('mountain') && region.adjacent(regions[i]))
			{
				res = -1;
				break;
			}
		return res;
	}
		
});

RaceTritons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Tritons', 6, 11);
	},
	attackBonus: function(region, tokenBadge)
	{
		return regions.hasProperty('coast') ? -1 : 0;
	}
});

RaceDwarves = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Dwarves', 3, 8);
	},
	incomeBonus: function(tokenBadge)
	{
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].mine)
				++res;
		return res;
	}
});

RaceHumans = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Humans', 5, 10);
	},
	incomeBonus: function(tokenBadge)
	{
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('farmland'))
				++res;
		return res;
	}
});

RaceOrcs = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Orcs', 5, 10);
	},
	incomeBonus: function(tokenBadge) //i suppose we don't need in these functions
	{
		return 0;//tokenBadge.inDecline ? 0 : tokenBadge.owner.getNonEmptyConqueredRegions();
	}
});

RaceWizards = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Wizards', 5, 10);
	},
	incomeBonus: function(tokenBadge)
	{
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('magic'))
				++res;
		return res;
	}
});

RaceAmazons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Amazons', 6, 15);
	},
	turnStartReinforcements: function(user)
	{
		return 4;
	},
	needRedeployment: function()
	{
		return true;
	}
});


RaceSkeletons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Skeletons', 6, 18);
	},
	turnEndReinforcements: function(user) //this function too
	{
		return 0; //user.getNonEmptyConqueredRegions() / 2;
	}
});

RaceElves = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Elves', 6, 11);
	},
	sufferCasualties: function(tokenBadge)
	{
		return 0;
	},
	clearRegion: function(tokenBadge, region)
	{
		return 0;
	}
});

RaceRatmen = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Ratmen', 8, 13);
	}
});
		
RaceTrolls = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Trolls', 5, 10);
	},
	defenseBonus: function()
	{
		return 1;
	}
});

RaceSorcerers = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Sorcerers', 5, 18);
	},
	enchant: function(region)
	{
		tokenBadge = user().currentTokenBadge;
		return (!(region.isImmune(true) || 
			!(this.canConquer(region, tokenBadge) && 
			getSpecPowByName(tokenBadge.specPowName).canConquer(region, tokenBadge)) ||
			region.tokenBadgeId == tokenBadge.id || 
			!region.tokenBadgeId ||
			!region.tokensNum ||
			region.tokensNum > 1 ||
			region.inDecline ||
			tokenBadge.totalTokensNum == this.maxNum));
	},
	canEnchant: function()
	{
		return true;
	}
});

var racesList = [
	new RaceAmazons(),
	new RaceDwarves(),
	new RaceElves(),
//	RaceGhouls(),
	new RaceGiants(),
	new RaceHalflings(),
	new RaceHumans(),
	new RaceOrcs(),
	new RaceRatmen(),
	new RaceSkeletons(),
	new RaceSorcerers(),
	new RaceTritons(),
	new RaceTrolls(),
	new RaceWizards(),
	new BaseRace()
];

for (var i = 0; i < racesList.length; ++i)
	racesList[i].setId(i);

BaseSpecialPower = $.inherit({
	__constructor: function(name, tokensNum, bonusNum)
	{
		this.name = name;
		this.tokensNum = tokensNum;
		this.bonusNum = bonusNum;
	},
	setId: function(id)
	{
		this.specialPowerId = id;
	},
	canConquer: function(region, tokenBadge)
	{
		return tokenBadge.isNeighbor(region) && !region.hasProperty('sea');
	},
	attackBonus: function(regionId, tokenBadgeId)
	{
		return 0;
	},
	incomeBonus: function(tokenBadge)
	{
		return 0;
	},
	canDecline: function(user)
	{
		return (Client.currGameState.state == GAME_FINISH_TURN);
	},
	decline: function(user)
	{
		return;
	},
	updateBonusStateAtTheEndOfTurn: function(tokenBadgeId)
	{
		return;
	},
	turnFinished: function(tokenBadgeId)
	{
		return;
	},
	dragonAttack: function(region)
	{
		return false;
	},
	clearRegion: function(tokenBadge, region)
	{
		return;
	},
	throwDice: function()
	{
		return false;
	},
	setEncampments: function(region)
	{
		return false;
	},
	canBeginSettingEncampments: function()
	{
		return false;
	},
	setFortress: function(region)
	{
		return false;
	},
	selectFriend: function(user, data)
	{
		return false;
	},
	setHero: function(region)
	{
		return false;
	},
	canBeginSetHero: function()
	{
		return false;
	},
	canBeginSetFortress: function()
	{
		return false;
	},
	canChooseFriend: function()
	{
		return false;
	},
	canBeginDragonAttack: function()
	{
		return false;
	}
});

SpecialPowerAlchemist = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Alchemist', 4);
	},
	incomeBonus: function(tokenBadge)
	{
		return tokenBadge.inDecline ? 0 : 2;
	}
});

SpecialPowerBerserk = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Berserk', 4);
	},
	throwDice: function()
	{
		return true;
	}
});

SpecialPowerBivouacking = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Bivouacking', 5, 5);
	},
	decline: function(user)
	{
		this.__base(user);
		var regions = user.regions();
		for (var i = 0; i < regions.length; ++i)
			regions[i].encampment = false;
	},
	canBeginSettingEncampments: function()
	{
		return true;
	},
	setEncampments: function(region) //should be rewritten for one encampent?
	{
		return region.tokenBadgeId === tokenBadge.id; // Why does it function 
	}													//named like it has a side-effect
});														//even though it just checks
														//something instead

SpecialPowerCommando = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Commando', 4);
	},
	attackBonus: function(region, tokenBadge)
	{
		return -1
	}
});

SpecialPowerDiplomat = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Diplomat', 5, 1);
	},
	selectFriend: function(friend)
	{
		if (friend.id == user().id || !(includes(friend,  Client.currGameState.players)))
			return false;
		return true;
		//should we remember info about previous conquers?
	},
	canChooseFriend: function()
	{
		return true;
	}
});

SpecialPowerDragonMaster = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('DragonMaster', 5, 1);
	},
	dragonAttack: function(region)
	{
		tokenBadge = user().currentTokenBadge;
		if (region.isImmune())
			return false;
		if (!(getRaceByName(user().currentTokenBadge.raceName).canConquer(region, tokenBadge) 
			&& this.canConquer(region, tokenBadge)))
			return false;
		if (region.tokenBadgeId && region.tokenBadgeId == tokenBadge.id)
			return false;
		return true;
	},
	clearRegion: function(tokenBadge, region)
	{
		tokenBadge.specPowNum -= 1;
		region.dragon = false;
	},
	decline: function(user)
	{
		this.__base(user);
		var regions = user.regions();
		for (var i = 0; i < regions.length; ++i)
			region.dragon = false;
	},
	canBeginDragonAttack: function()
	{
		return true;
	}
});

SpecialPowerFlying = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Flying', 5);
	},
	canConquer: function(region, tokenBadge)
	{
		return !tokenBadge.isNeighbor(region) && !region.hasProperty('sea');

	}
});

SpecialPowerForest = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Forest', 4);
	},
	incomeBonus: function(tokenBadge)
	{
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('forest'))
				++res;
		return res;
	}
});

SpecialPowerFortified = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Fortified', 3, 6);
		this.maxNum = 6;
	},
	canBeginSetFortress: function()
	{
		return true;
	},
	incomeBonus: function(tokenBadge)
	{
		if (tokenBadge.inDecline)
			return 0;
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].fortress)
				++res;
		return res;
	},
	clearRegion: function(tokenBadge, region)
	{
		if (region.fortress)
			tokenBadge.specPowNum = max(tokenBadge.specPowNum - 1, 0)
	},
	setFortress: function(region)
	{
		if (region.tokenBadgeId != user().currentTokenBadge.id 
			|| region.fortress)
			return false;

		var regions = user().currentTokenBadge.regions(),
			cnt = 0;
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].fortress)
				++cnt;
		if (cnt >= this.maxNum)
			return false;

		return true;
	}
	
});

SpecialPowerHeroic = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Heroic', 5, 2);
	},
	setHero: function(region)
	{
		var f1 = region.tokenBadgeId == user().currentTokenBadge.id,
			f2 = game().heroesRegions.length < 2,
			f3 = !(game().heroesRegions[0] && 
				region.id == game().heroesRegions[0]['regionId'] || 
				game().heroesRegions[1] &&
				region.id == game().heroesRegions[1]['regionId'])
		
		return f1 && f2 && f3;
	},
	canBeginSetHero: function()
	{
		return true;
	},
	decline: function(user)
	{
		this.__base(self, user);
		var regions = user.regions();
		for (var i = 0; i < regions.length; ++i)
			regions[i].hero = false;
	},
	clearRegion: function(tokenBadge, region)
	{
		tokenBadge.specPowNum -= 1;
		region.hero = false;
	}
});

SpecialPowerHill = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Hill', 4);
	},
	incomeBonus: function(tokenBadge)
	{
		if (tokenBadge.inDecline)
			return 0;
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('hill'))
				++res;
		return res;
	}
});

SpecialPowerMerchant = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Merchant', 2);
	},
	incomeBonus: function(tokenBadge)
	{
		return Client.currentUser.regions().length; //we can calc it only for current user, so it isn't wrong
	}
});

SpecialPowerMounted = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Mounted', 5);
	},
	attackBonus: function(region, tokenBadge)
	{
		return region.hasProperty('farmland') || region.hasProperty('hill') ? -1 : 0	
	}
});

SpecialPowerMerchant = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Merchant', 2);
	},
	incomeBonus: function(tokenBadge)
	{
		return 0;
	}
});

SpecialPowerPillaging = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Pillaging', 5);
	},
	incomeBonus: function(tokenBadge)
	{
		return 0; 
	}
});

SpecialPowerSeafaring = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Seafaring', 5);
	},
	canConquer: function(region, tokenBadge)
	{
		return tokenBadge.isNeighbor(region);
	}
});

SpecialPowerStout = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Stout', 4);
	},
	canDecline: function(user)
	{
		return true; 
	}
});


SpecialPowerSwamp = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Swamp', 4)
	},
	incomeBonus: function(tokenBadge)
	{
		if (tokenBadge.inDecline)
			return 0;
		var res = 0,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('swamp'))
				++res;
		return res;
	}
});

SpecialPowerUnderworld = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Underworld', 5)
	},
	canConquer: function(region, tokenBadge)
	{
		if (this.__base(region, tokenBadge))
			return true;
		var cav = false,
			regions = tokenBadge.regions();
		for (var i = 0; i < regions.length; ++i)
			if (regions[i].hasProperty('cavern'))
			{
				cav = true;
				break;
			}
		return (cav && region.hasProperty('cavern'));
	},
	attackBonus: function(region, tokenBadge)
	{
		return region.hasProperty('cavern') ? -1 : 0;
	}
});


SpecialPowerWealthy = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Wealthy', 4, 1)
	},
	incomeBonus: function(tokenBadge)
	{
		if (tokenBadge.specPowNum == 1)
		{
			tokenBadge.specPowNum = 0;
			return 7;
		}
		return 0;
	}
});

var specialPowerList = [
	new SpecialPowerAlchemist(),
	new SpecialPowerBerserk(),
	new SpecialPowerBivouacking(),
	new SpecialPowerCommando(),
	new SpecialPowerDiplomat(),
	new SpecialPowerDragonMaster(),
	new SpecialPowerFlying(),
	new SpecialPowerForest(),
	new SpecialPowerFortified(),
	new SpecialPowerHeroic(),
	new SpecialPowerHill(),
	new SpecialPowerMerchant(),
	new SpecialPowerMounted(),
	new SpecialPowerPillaging(),
	new SpecialPowerSeafaring(), 
//	SpecialPowerSpirit(),
	new SpecialPowerStout(),
	new SpecialPowerSwamp(),
	new SpecialPowerUnderworld(),
	new SpecialPowerWealthy()
];
for (var i = 0; i < specialPowerList.length; ++i)
	specialPowerList[i].setId(i);

getSpecPowId = function(name)
{
	for (var i = 0; i < specialPowerList.length; ++i)
		if (specialPowerList[i].name == name)
			return i;
}

getSpecialPower = function(id)
{
	return specialPowerList[id];
}

getSpecPowByName = function(name)
{
	return specialPowerList[getSpecPowId(name)];
}

getRaceId = function(name)
{
	for (var i = 0; i < racesList.length; ++i)
		if (racesList[i].name == name)
			return i;
}

getRace = function(id)
{
	return racesList[id];
}

getRaceByName = function(name)
{
	return racesList[getRaceId(name)];
}

getBaseRace = function() 
{
	return getRaceByName();
}