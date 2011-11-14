onMessageChange = function()
{
	if (Client.currentUser.id && $('#messageBox').val().length > 0)
		$('#sendMessage').show();
	else
		$('#sendMessage').hide();
}

setReadinessStatusClick = function()
{
	sendQuery(makeQuery(['action', 'sid', 'isReady'], ['setReadinessStatus', 
		Client.currentUser.sid, (1 - $(this).prop('isReady'))]), 
		setReadinessStatusResponse);
}

finishTurnClick = function()
{
	sendQuery(makeQuery(['action', 'sid'], ['finishTurn', user().sid]), finishTurnResponse);
}

throwDiceClick = function()
{
	sendQuery(makeQuery(['action', 'sid'], ['throwDice', user().sid]), throwDiceResponse);
}

changeRedeployStatusClick = function()
{
	if (Client.currGameState.redeployStarted)
	{
		Client.currGameState.redeployStarted = false;
		$('#changeRedeployStatus').html('Start redeploy');
		$('#redeploy').hide();
		return;
	}
	Client.currGameState.redeployStarted = true;
	Client.currGameState.regions = [];
	user().startRedeploy();
	$('#changeRedeployStatus').html('Cancel redeploy');
	$('#redeploy').show();
}

redeployClick = function()
{
	var cmds = ['action', 'sid', 'regions'];
	var params = ['redeploy', user().sid, game().redeployRegions];
	if (game().encampmentsRegions.length)
	{
		cmds.push('encampments');
		params.push(game().encampmentsRegions);
	}
	if (game().heroesRegions.length)
	{
		cmds.push('heroes');
		params.push(game().heroesRegions);
	}
	if (game().fortressRegion)
	{
		cmds.push('fortified');
		params.push({'regionId': game().fortressRegion});
	}
	sendQuery(makeQuery(cmds, params), redeployResponse);
}

defendClick = function()
{
	game().defendStarted = false;
	sendQuery(makeQuery(['action', 'sid', 'regions'],['defend', user().sid, 
		game().defendRegions]), defendResponse);
}

saveGameClick = function()
{
	sendQuery(makeQuery(['action', 'gameId', 'sid'],
		['saveGame', game().id, user().sid]), saveGameResponse);
}


btnSetHeroClick = function(j)
{
	if ($('#btnSetHero').html() == 'Set hero')
	{
		game().heroesRegions.push({'regionId': j});
		$('#btnSetHero').html('Remove hero');
		game().map.regions[j - 1].hero = true;
		game().map.regions[j - 1].drawTokenBadge();
	}
	else
	{
		if (game().heroesRegions[0] && 
			game().heroesRegions[0]['regionId'] == j)
			if (game().heroesRegions[1])
				game().heroesRegions[0] = game().heroesRegions[1];
			else 
				game().heroesRegions = [];
		else
			game().heroesRegions.pop();
		game().map.regions[j - 1].hero = false;
		game().map.regions[j - 1].drawTokenBadge();
		$('#btnSetHero').html('Set hero');
	}
}

btnSetFortressClick = function(j)
{
	if ($('#btnSetFortress').html() == 'Set fortress')
	{
		game().fortressRegion = j;
		$('#btnSetFortress').html('Remove fortress');
		game().map.regions[j - 1].fortress = true;
		game().map.regions[j - 1].drawTokenBadge();
	}
	else
	{
		game().fortressRegion = undefined;
		$('#btnSetFortress').html('Set fortress');
		game().map.regions[j - 1].fortress = false;
		game().map.regions[j - 1].drawTokenBadge();
	}
}

changeConfirmDialogForRedeploy = function(j)
{
	if (game().redeployStarted && canRedeploy(game().map.regions[j - 1]))
	{
		curTokensNum = game().map.regions[j - 1].tokensNum;
		for (var k = 0; k < game().redeployRegions.length; ++k)
			if (game().redeployRegions[k]['regionId'] == j)
				curTokensNum = game().redeployRegions[k]['tokensNum'];
		for (var k = 0; k <= user().freeTokens + curTokensNum; ++k)
			$('#possibleTokensNumForRedeploy').append('<option' + ((k == curTokensNum) 
			? ' selected' : '') + '>' + k + '</option>');
		$('#possibleTokensNumForRedeploy').change(function(){
			tokensNum = parseInt($('#possibleTokensNumForRedeploy option:selected').val());
			user().freeTokens += curTokensNum - tokensNum;
			var l;
			for ( l = 0; l < game().redeployRegions.length; ++l)
			{
				if (game().redeployRegions[l]['regionId'] == j)
				{
					game().redeployRegions[l]['tokensNum'] = tokensNum;
					break;
				}
			}
			if (l == game().redeployRegions.length)
				game().redeployRegions.push({'regionId': j, 'tokensNum': tokensNum});
			game().map.regions[j - 1].tokensNum = tokensNum;
			game().map.regions[j - 1].drawTokenBadge();
		});
		$('#possibleTokensNumForRedeploy').show();
		$('#lblPossibleTokensNumForRedeploy').show();
	}
}

changeConfirmDialogForDefend = function(j)
{
	if (canBeginDefend() && canDefend(game().map.regions[j - 1]))
	{
		var curTokensNum = 0;
		for (l = 0; l < game().defendRegions.length; ++l)
			if (game().defendRegions[l]['regionId'] == j)
			{
				curTokensNum = game().defendRegions[l]['tokensNum'];
				break;
			}
		for (var k = 0; k <= game().freeTokensForDefend + curTokensNum; ++k)
			$('#possibleTokensNumForDefend').append('<option' + 
			((k == curTokensNum) ? ' selected' : 
			'') + '>' + k + '</option>');
		$('#possibleTokensNumForDefend').change(function(){
			tokensNum = parseInt($('#possibleTokensNumForDefend option:selected').val());
			var l;
			for (l = 0; l < game().defendRegions.length; ++l)
			{
				if (game().defendRegions[l]['regionId'] == j)
				{
					game().freeTokensForDefend += game().defendRegions[l]['tokensNum'] - 
						tokensNum;
					game().defendRegions[l]['tokensNum'] = tokensNum;
					break;
				}
			}
			if (l == game().defendRegions.length)
			{
				game().freeTokensForDefend -= tokensNum;
				game().defendRegions.push({'regionId': j, 'tokensNum': tokensNum});
			}
			game().defendStarted = true;
			game().map.regions[j - 1].tokensNum += tokensNum - curTokensNum;
			game().map.regions[j - 1].drawTokenBadge();
		});
		$('#possibleTokensNumForDefend').show();
		$('#lblPossibleTokensNumForDefend').show();
	}
}

changeConfirmDialogForEncampments = function(j)
{
	if (canBeginSettingEncampments() && canSetEncampments(game().map.regions[j - 1]))
	{
		var curEncampmentsNum = 0;
		for (l = 0; l < game().encampmentsRegions.length; ++l)
			if (game().encampmentsRegions[l]['regionId'] == j)
			{
				curEncampmentsNum = game().encampmentsRegions[l]['encampmentsNum'];
				break;
			}
		for (var k = 0; k <= game().freeEncampments + curEncampmentsNum; ++k)
			$('#possibleEncampmentsNum').append('<option' + 
			((k == game().map.regions[j - 1].encampmentsNum) ? ' selected' : 
			'') + '>' + k + '</option>');
		$('#possibleEncampmentsNum').change(function(){
			encampmentsNum = parseInt($('#possibleEncampmentsNum option:selected').val());
			var l;
			for (l = 0; l < game().encampmentsRegions.length; ++l)
			{
				if (game().encampmentsRegions[l]['regionId'] == j)
				{
					game().freeEncampments += game().encampmentsRegions[l]['encampmentsNum'] - 
						encampmentsNum;
					game().encampmentsRegions[l]['encampmentsNum'] = encampmentsNum;
					break;
				}
			}
			if (l == game().encampmentsRegions.length)
			{
				game().freeEncampments -= encampmentsNum;
				game().encampmentsRegions.push({'regionId': j, 'encampmentsNum': encampmentsNum});
			}
			game().map.regions[j - 1].encampment = encampmentsNum;
			game().map.regions[j - 1].drawTokenBadge();
		});
		$('#possibleEncampmentsNum').show();
		$('#lblPossibleEncampmentsNum').show();
	}
}

changeConfirmDialogForHeroes = function(j)
{
	if (canBeginSetHero())
	{
		if (game().heroesRegions[0] && 
			game().heroesRegions[0]['regionId'] == j || 
			game().heroesRegions[1] && 
			game().heroesRegions[1]['regionId'] == j)
			$('#btnSetHero').html('Remove hero');
		else if (canSetHero(game().map.regions[j - 1]))
			$('#btnSetHero').html('Set hero');
		else
			$('#btnSetHero').hide();
	}
	else
		$('#btnSetHero').hide();
}

changeConfirmDialogForFortress = function(j)
{
	if (canBeginSetFortress())
	{
		if (game().fortressRegion == j)
			$('#btnSetFortress').html('Remove fortress');
		else if (!game().fortressRegion && 
			canSetFortress(game().map.regions[j - 1]))
			$('#btnSetFortress').html('Set fortress');
		else
			$('#btnSetFortress').hide();
	}
	else
		$('#btnSetFortress').hide();
}

regionClick = function(j)
{
	return function(){
		$('#confirmInfo').empty();
		$('#confirmOutput span').empty();
		$('#confirmOutput').hide();
		$('#confirmInfo').append(game().map.regions[j - 1].htmlRegionInfo());
		$('#confirmInfo').append(
			'<laber id = "lblPossibleTokensNumForRedeploy" '+
			'for="possibleTokensNumForRedeploy" style = "display: none">Redeploy</label>' +
			'<select id = "possibleTokensNumForRedeploy" style = "display: none">' +
			'</select><br>');
		$('#confirmInfo').append(
			'<laber id = "lblPossibleTokensNumForDefend" '+ 
			'for="possibleTokensNumForDefend" style = "display: none">Defend</label>' +
			'<select id = "possibleTokensNumForDefend" style = "display: none"></select><br>');
		$('#confirmInfo').append(
			'<laber id = "lblPossibleEncampmentsNum"' +
			'for="possibleEncampmentsNum" style = "display: none">Set encampments</label>' +
			'<select id = "possibleEncampmentsNum" style = "display: none"></select><br>');
		$('#confirm').dialog({
			height:250,
			title: 'region ' + j,
			modal: true,
			buttons: [
				{
					id: 'btnConquer',
					text: 'Conquer',
					click: function() {
						sendQuery(makeQuery(['action', 'sid', 'regionId'], 
							['conquer', user().sid, j]), conquerResponse);	
						$(this).dialog('close');
					}
				},
				{
					id: 'btnEnchant',
					text: 'Enchant',
					click: function() {
						sendQuery(makeQuery(['action', 'sid', 'regionId'], 
							['enchant', user().sid, j]), enchantResponse);
						$(this).dialog('close');
					}
				},
				{
					id: 'btnDragonAttack',
					text: 'Dragon attack',
					click: function() {
						sendQuery(makeQuery(['action', 'sid', 'regionId'], 
							['dragonAttack', user().sid, j]), dragonAttackResponse);
						$(this).dialog('close');
					}
				},
				{
					id: 'btnCancel',
					text: 'Cancel',
					click: function() {
						$(this).dialog('close');
					}
				},
				{
					id: 'btnSetHero',
					click: btnSetHeroClick						
				},
				{
					id: 'btnSetFortress',
					text: 'Set fortress',
					click: btnSetFortressClick
				}
			]
		});
		$('#confirm').dialog('open');
		if (!(canBeginConquer() && canConquer(game().map.regions[j - 1])))
			$('#btnConquer').hide();
		if (!(canBeginEnchant() && canEnchant(game().map.regions[j - 1])))
			$('#btnEnchant').hide();
		if (!(canBeginDragonAttack() && canDragonAttack(game().map.regions[j - 1])))
			$('#btnDragonAttack').hide();
		changeConfirmDialogForRedeploy(j);
		changeConfirmDialogForDefend(j);
		changeConfirmDialogForEncampments(j);
		changeConfirmDialogForHeroes(j);
		changeConfirmDialogForFortress(j);
	}
}
