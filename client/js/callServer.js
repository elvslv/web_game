function sendQuery(query, callback)
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
					callback(data);
			}
		},
		error: function(jqXHR, textStatus, errorThrown)
		{
			console.error(errorThrown);
		}
		
	});
}

updateGameList = function()
{
	sendQuery(makeQuery(['action'], ['getGameList']), getGameListResponse);
}

updateChat = function()
{
	sendQuery(makeQuery(['action', 'since'], ['getMessages', Client.messages.length]), 
		getMessagesResponse);
}

updateMapList = function(beforeCreateGame)
{
	sendQuery(makeQuery(['action'], ['getMapList']), function(data) 
	{
		getMapListResponse(data, beforeCreateGame)
	});
}

updateGameState = function()
{
	sendQuery(makeQuery(['action', 'gameId'], ['getGameState', Client.currentUser.gameId]), 
		getGameStateResponse)
}

makeQuery = function(fields, values)
{
	result = {};
	for (var i = 0; i < fields.length; ++i)
		result[fields[i]] = values[i];
	return result;
}

