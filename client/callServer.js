function sendQuery(query, callback)
{
	$.ajax({
		type: "POST",
		url: "http://localhost/small_worlds/",
		data: query,
		success: function(result){
			data = $.parseJSON(result);
			if (!data['result'])
			{
				alert("Unknown server response: " + data);
				return;
			}
			callback(data);
		}
	});
}

updateGameList = function()
{
	sendQuery('{"action": "getGameList"}', getGameListResponse);
}

updateChat = function()
{
	sendQuery('{"action": "getMessages", "since": ' + Client.messages.length + '}', 
		getMessagesResponse);
}

updateMapList = function(beforeCreateGame)
{
	sendQuery('{"action": "getMapList"}', function(data) 
	{
		getMapListResponse(data, beforeCreateGame)
	});
}

