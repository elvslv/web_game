function sendQuery(query, callback, readonly, param)
{
	$.ajax({
		type: "POST",
		url: "/ajax",
		data: $.toJSON(query),
		success: function(data)
		{
			if (!data['result'])
			{
				console.error("Unknown server response: " + data);
				return;
			}
			switch(data['result'])
			{
				case 'badJson': //may it be???
				case 'badReadinessStatus':
					console.error('Invalid data');
					break;
				case 'badUserSid':
					gotBadUserSid();
					break;
				case 'badGameId': //may it be???
					console.error('Invalid game id');
					break;
				case 'badMapId': 
					console.error('Invalid map id');
					break;
				case 'badPosition': 
					console.error('Invalid position');
					break;
				case 'badStage':
					alert('Bad stage'); 
					break;
				case 'badRegion':
					alert('Bad region'); 
					break;
				case 'badFriendId':
					console.error('Invalid friend id'); 
					break;
				case 'badRegionId':
					console.error('Invalid region id'); 
					break;
				default:
					callback(data, param);
			}
		},
		error: function(jqXHR, textStatus, errorThrown)
		{
			console.error(errorThrown);
		},
		beforeSend: function()
		{
			if (!readonly)
			{
				$.blockUI(
				{
					message: '<img src="css/images/ajax-loader.gif" />',
					css:
					{
						width: '24px',
						top: '15px',
						left: '15px',
						transparent: 0,
						border: 'none',
						backgroundColor: '#666666'
					}
				});
			}
		},
		complete: function()
		{
			if(!readonly)
				$.unblockUI();
		}
		
	});
}

updateGameList = function()
{
	sendQuery(makeQuery(['action'], ['getGameList']), getGameListResponse, true);
}

updateChat = function()
{
	sendQuery(makeQuery(['action', 'since'], ['getMessages', Client.messages.length], true), 
		getMessagesResponse);
}

updateMapList = function(beforeCreateGame)
{
	sendQuery(makeQuery(['action'], ['getMapList']), function(data) 
	{
		getMapListResponse(data, beforeCreateGame)
	}, true);
}

updateGameState = function()
{
	sendQuery(makeQuery(['action', 'gameId'], ['getGameState', Client.currentUser.gameId]), 
		getGameStateResponse, true)
}

makeQuery = function(fields, values)
{
	var result = {};
	for (var i = 0; i < fields.length; ++i)
		result[fields[i]] = values[i];
	return result;
}

