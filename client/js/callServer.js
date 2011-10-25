function sendQuery(query, callback)
{
	$.ajax({
		type: "POST",
		url: "/ajax",
		data: $.toJSON(query),
		success: function(result)
		{
			data = $.parseJSON(result);
			if (!data['result'])
			{
				alert("Unknown server response: " + data);
				return;
			}
			callback(data);
		},
		error: function(jqXHR, textStatus, errorThrown)
		{
			alert(e);
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
	sendQuery(makeQuery(['action', 'gameId'], ['getGameState', Client.currentUser.gameId], 
		getGameStateResponse))
}

makeQuery = function(fields, values)
{
	result = {};
	for (var i = 0; i < fields.length; ++i)
		result[fields[i]] = values[i];
	return result;
}

