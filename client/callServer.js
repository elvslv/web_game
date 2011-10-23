function sendQuery(query, callback)
{
	$.ajax({
		type: "POST",
		url: "http://localhost/small_worlds/",
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
		beforeSend: function()
		{
			$.blockUI(
			{
				message: '<img src="styles/images/busy.gif" />',
				css: 
				{
					width: '15px',  
					top:  ($(window).height() - 15) /2 + 'px', 
                	left: ($(window).width() - 15) /2 + 'px',
                	transparent: 0,
                	border: 'none',
                	backgroundColor: '#666666'
                }
		    });
		},
		complete: function()
		{
			$.unblockUI();
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

makeQuery = function(fields, values)
{
	result = {};
	for (var i = 0; i < fields.length; ++i)
		result[fields[i]] = values[i];
	return result;
}

