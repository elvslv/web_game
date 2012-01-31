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
	if (game().redeployStarted)
	{
		game().redeployStarted = false;
		$('#changeRedeployStatus').html('Start redeploy');
		$('#redeploy').hide();
		return;
	}
	game().redeployStarted = true;
	Graphics.resetHighlight(game().map);
	user().startRedeploy();
	$('#changeRedeployStatus').html('Cancel redeploy');
	$('#redeploy').show();
}

redeployClick = function()
{
	var table = {
			hero : Client.HERO_CODE,
			fortress : Client.FORTRESS_CODE,
			encampment : Client.ENCAMPMENTS_CODE,
		},
		cmds = ['action', 'sid', 'regions'],
		params = ['redeploy', user().sid, 
			convertRedeploymentRequest(game().redeployRegions,
				Client.REDEPLOYMENT_CODE)],
		specPower = user().specPower(),
		code = table[specPower.regPropName];
	if (code) {
		cmds.push(specPower.redeployReqName);
		params.push(convertRedeploymentRequest(
			game().redeployRegions[specPower.regPropName], code));
	}
	
	sendQuery(makeQuery(cmds, params), redeployResponse);
}

defendClick = function()
{
	sendQuery(makeQuery(['action', 'sid', 'regions'], 
		['defend', user().sid, convertRedeploymentRequest(game().redeployRegions, 
				Client.REDEPLOYMENT_CODE)]), defendResponse);
}

saveGameClick = function()
{
	sendQuery(makeQuery(['action', 'gameId', 'sid'],
		['saveGame', game().id, user().sid]), saveGameResponse);
}


regionClick = function(reg)
{
	return function(){
		$('#confirmInfo').empty();
		$('#confirmOutput span').empty();
		$('#confirmOutput').hide();
		$('#confirmInfo').append(reg.htmlRegionInfo());
		$('#confirm').dialog({
			height:250,
			title: 'region ' + reg.id,
			modal: true,
			buttons: [
				{
					id: 'btnConquer',
					text: 'Conquer',
					click: function() {
						sendQuery(makeQuery(['action', 'sid', 'regionId'], 
							['conquer', user().sid, reg.id]), conquerResponse);	
						$(this).dialog('close');
					}
				},
				{
					id: 'btnEnchant',
					text: 'Enchant',
					click: function() {
						sendQuery(makeQuery(['action', 'sid', 'regionId'], 
							['enchant', user().sid, reg.id]), enchantResponse);
						$(this).dialog('close');
					}
				},
				{
					id: 'btnCancel',
					text: 'Cancel',
					click: function() {
						$(this).dialog('close');
					}
				}				
			]
		});
		$('#confirm').dialog('open');
		if (!(canBeginConquer() && canConquer(reg)))
			$('#btnConquer').hide();
		if (!(canBeginEnchant() && canEnchant(reg)))
			$('#btnEnchant').hide();
	}
}

showVisibleTokenBadgesClick = function()
{
	$('#showVisibleTokenBadgesDialog').dialog('open');
}