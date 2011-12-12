BaseRace = $.inherit({
	__constructor: function(name, initialNum, maxNum)
	{
		this.name = name;
		this.initialNum = initialNum;
		this.maxNum = maxNum;
		this.race = true;
	},
	setId: function(id)
	{
		this.id = id;
	},
	canConquer: function(region, tokenBadge)
	{
		return (!tokenBadge.regions().length &&  
			region.hasProperty('border')) || tokenBadge.regions().length;
	},
	enchant: function(region)
	{
		return false;
	},
	canEnchant: function()
	{
		return false;
	},
	getPic : function(declined)
	{
		n = this.name ? this.name + ' ' : ''; 
		return "client/css/images/races/" + n + "small" + 
			(declined ? " decline.jpg" : ".jpg"); 
	},
	canDrop : function(region)
	{
		return canRedeploy(region);
	},
	onDropSuccess : function(oldReg, newReg)
	{
		var init = function(elt, obj){	
			return elt === undefined ? (obj ? {} : 0) : elt;
		}, rdRegs = game().redeployRegions;
		newReg.ui.addUnit(this);
		rdRegs[newReg.id] = init(rdRegs[newReg.id]);
		rdRegs[newReg.id]++;
		if (oldReg) 
			rdRegs[oldReg.id]--;
		else 
			user().freeTokens--;
	
	},
	canStartRedeploy : function()
	{
		return true;
	}

});
	
RaceHalflings = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Halflings', 6, 11);
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
	}
});

RaceGiants = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Giants', 6, 11);
	}
		
});

RaceTritons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Tritons', 6, 11);
	}
});

RaceDwarves = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Dwarves', 3, 8);
	}
});

RaceHumans = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Humans', 5, 10);
	}
});

RaceOrcs = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Orcs', 5, 10);
	}
});

RaceWizards = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Wizards', 5, 10);
	}
});

RaceAmazons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Amazons', 6, 15);
	},
	deleteAdditionalUnits : function()
	{
		console.log(user().tokensInHand);
		var n = 4 - user().tokensInHand,
			regions = user().regions(),
			loop = function(needCheck){
				var i, lbl;
				for (i = 0; i < regions.length; i++){
					if (n <=0 ) return true;
					console.log(n);
					lbl = regions[i].ui.race.num;
					if (!needCheck || lbl.n > 1){
						game().redeployRegions[regions[i].id]--;
						n--;
						lbl.n--;
						if (!lbl.n) {
							Graphics.deleteBadge(regions[i].ui.race, regions[i]);
						} else
							lbl.attr({"text" : lbl.n});
					}
				}
				return false;
			}, m;
		if (user().tokensInHand > 4){
			m = --Graphics.freeTokens.ui.race.num.n;
			Graphics.freeTokens.ui.race.num.attr({text : m});
		} else
			Graphics.deleteBadge(Graphics.freeTokens.ui.race, Graphics.freeTokens);
		loop(true);
		while (n) loop(false);
	}
	
	
});


RaceSkeletons = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Skeletons', 6, 18);
	}
});

RaceElves = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Elves', 6, 11);
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
	}
});

RaceSorcerers = $.inherit(BaseRace, {
	__constructor: function()
	{
		this.__base('Sorcerers', 5, 18);
	},
	enchant: function(region)
	{
		console.log('enchantment');
		var tokenBadge = user().currentTokenBadge;
		return (!(region.isImmune(true) || 
			!(this.canConquer(region, tokenBadge) && 
			getSpecPowByName(tokenBadge.specPowName).canConquer(region, tokenBadge)) ||
			region.tokenBadgeId === tokenBadge.id || 
			!region.tokenBadgeId ||
			!region.tokensNum ||
			region.tokensNum > 1 ||
			region.inDecline ||
			tokenBadge.totalTokensNum === this.maxNum));
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
	__constructor: function(name, tokensNum, bonusNum, regPropName, redeployReqName)
	{
		this.name = name;
		this.tokensNum = tokensNum;
		this.bonusNum = bonusNum;
		this.power = true;
		this.regPropName = regPropName;
		this.redeployReqName = redeployReqName;
	},
	setId: function(id)
	{
		this.specialPowerId = id;
	},
	canConquer: function(region, tokenBadge)
	{
		return (tokenBadge.isNeighbor(region) || !tokenBadge.regions().length)&& !region.hasProperty('sea');	
	},
	canDecline: function(user)
	{
		return Client.currGameState.state === GAME_FINISH_TURN;
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
	selectFriend: function(user, data)
	{
		return false;
	},
	canChooseFriend: function()
	{
		return false;
	},
	canActAfterRedeployment : function()
	{
		return false;
	},
	getPic : function()
	{
		return this.regPropName && "client/css/images/specialPowers/" + this.regPropName.toLowerCase() + ".jpg"; 
	},
	canDrop: function(region) 
	{
		return canRedeploy(region) && 
			(!game().redeployRegions[this.regPropName] || 
				!game().redeployRegions[this.regPropName][region.id]); 
	},

	onDropSuccess : function(oldReg, newReg)
	{
		var init = function(elt, obj){	
			return elt === undefined ? (obj ? {} : 0) : elt;
		}, rdRegs = game().redeployRegions;
		newReg.ui.addUnit(this);
		rdRegs[this.regPropName] = init(rdRegs[this.regPropName], true);
		rdRegs[this.regPropName][newReg.id] = init(rdRegs[this.regPropName][newReg.id]);
		rdRegs[this.regPropName][newReg.id]++;
		if (oldReg) 
			game().redeployRegions[this.regPropName][oldReg.id]--;
		else 
			user().freePowerTokens--;
	
	},
	canStartRedeploy : function()
	{
		return true;
	},

	needRedeploy : function()
	{
		return false;
	}

});

SpecialPowerAlchemist = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Alchemist', 4);
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
		this.__base('Bivouacking', 5, 5, 'encampment', 'encampments');
	},
	needRedeploy : function()
	{
		return true;
	},
	canDrop : function(region)
	{
		return canRedeploy(region);
	}

});														
														

SpecialPowerCommando = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Commando', 4);
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
	},
	canActAfterRedeployment : function()
	{
		return true;
	}
});

SpecialPowerDragonMaster = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('DragonMaster', 5, 1, 'dragon');
	},
	canDrop: function(region)
	{
		var tokenBadge = user().currentTokenBadge;
		return !region.isImmune() && canConquer(region, tokenBadge) &&
			!(region.tokenBadgeId && region.tokenBadgeId === tokenBadge.id)
	},
	decline: function(user)
	{
		this.__base(user);
		var regions = user.regions();
		for (var i = 0; i < regions.length; ++i)
			if (region.dragon){
				region.dragon = false;
				region.ui.power.remove();
				delete region.ui.power;
			}
	},
	onDropSuccess : function(oldReg, newReg)
	{
		sendQuery(makeQuery(['action', 'sid', 'regionId'], 
				['dragonAttack', user().sid, newReg.id]), dragonAttackResponse);
	
	},
	dragonAttack : function()
	{
		return true;
	},
	canStartRedeploy : function()
	{
		return false;
	},

	needRedeploy : function()
	{
		return false;
	}

});

SpecialPowerFlying = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Flying', 5);
	},
	canConquer: function(region, tokenBadge)
	{
		var f1 = tokenBadge.isNeighbor(region),
			f2 = tokenBadge.regions().length,
			f3 = region.hasProperty('sea');
		return ((!f1 && f2) || !f2) && !f3;
	}
});

SpecialPowerForest = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Forest', 4);
	}
});

SpecialPowerFortified = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Fortified', 3, 6, 'fortress', 'fortified');
	},
	canStartRedeploy : function(reg)
	{
		if (reg) return !reg.fortress;
		var count = 0;
		for (prop in  game().redeployRegions[this.regPropName]){
			if (game().redeployRegions[this.regPropName].hasOwnProperty(prop) &&
				game().redeployRegions[this.regPropName][prop] > 0)
				count++;
		}
		return count < 1;
	}, 

	needRedeploy : function()
	{
		return false;
	},

	canDrop : function(region)
	{
		return canRedeploy(region) && !region.fortress;
	}
	
});

SpecialPowerHeroic = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Heroic', 5, 2, 'hero', 'heroes');
	},

	needRedeploy : function()
	{
		return true;
	}

});

SpecialPowerHill = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Hill', 4);
	}
});

SpecialPowerMerchant = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Merchant', 2);
	}
});

SpecialPowerMounted = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Mounted', 5);
	}
});

SpecialPowerMerchant = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Merchant', 2);
	}
});

SpecialPowerPillaging = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Pillaging', 5);
	}
});

SpecialPowerSeafaring = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Seafaring', 5);
	},
	canConquer: function(region, tokenBadge)
	{
		return (tokenBadge.isNeighbor(region) && tokenBadge.regions().length) || !tokenBadge.regions().length 
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
	},

	canActAfterRedeployment : function()
	{
		return true;
	}
});


SpecialPowerSwamp = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Swamp', 4)
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
		return tokenBadge.regions().some(function(x){
			return x.hasProperty('cavern')
				}) && region.hasProperty('cavern');
	}
});


SpecialPowerWealthy = $.inherit(BaseSpecialPower, {
	__constructor: function()
	{
		this.__base('Wealthy', 4, 1)
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