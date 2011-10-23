var Interface = {};

Interface.fillGameList = function() 
{
	$('#gameList').empty();
	if(Client.gameList.length)
	{
		$('#gameListInfo').html('Games:')
		$('#gameListTemplate').tmpl(Client.gameList, 
		{
			join: function(gameId)
			{
				'join'.concat(gameId)
			}
		}).appendTo('#gameList');
	}
	else
		$('#gameListInfo').html('There are no avaliable games');
	initGameList();
	delete Client.currentUser.gameIndex;
	for (var i = 0; i < Client.gameList.length; ++i)
	{
		if (Client.currentUser.gameId == Client.gameList[i].gameId)	
			Client.currentUser.gameIndex = i;
		$('#join' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				var gameId = Client.gameList[i].gameId;
				Client.currentUser.newGameId = gameId;
				sendQuery('{"action": "joinGame", "sid": ' + Client.currentUser.sid +
					', "gameId": ' + gameId + '}', joinGameResponse);
			});
		$('#leave' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery('{"action": "leaveGame", "sid": ' + Client.currentUser.sid +'}', 
					leaveGameResponse);
			});
		$('#setReadinesStatus' + Client.gameList[i].gameId).prop('isReady', 0);
		$('#setReadinesStatus' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				var gameId = Client.gameList[i].gameId;
				sendQuery('{"action": "setReadinessStatus", "sid": ' + Client.currentUser.sid +
					', "isReady": ' + (1 - $(this).prop('isReady')) + '}', setReadinessStatusResponse);
			});		

	}
	if (Client.currentUser && Client.currentUser.sid)
	{
		if (!Client.currentUser.gameId)
		{
			for (var i = 0; i < Client.gameList.length; ++i)
			{
				if (Client.gameList[i].state === 1)
					$('#join' + Client.gameList[i].gameId).show();
			}
		}
		else
		{
			if (Client.gameList[Client.currentUser.gameIndex].state === 1)
			{
				$('#setReadinesStatus' + Client.currentUser.gameId).prop('isReady', 
					Client.currentUser.isReady);
				$('#setReadinesStatus' + Client.currentUser.gameId).html(Client.currentUser.isReady ? 
					'I am not ready' : 'I am ready');
				$('#setReadinesStatus' + Client.currentUser.gameId).show();
			}
			$('#leave' + Client.currentUser.gameId).show();
		}
	}
}


Interface.changeOnGetMessages = function()
{
	$('#chat').empty();
	$('#chatTemplate').tmpl(Client.messages, {
		UTC: function(time){d = new Date(time * 1000); return d.toUTCString()}}).appendTo('#chat');
}

Interface.changeOnRegistration = function() 
{ 
	$('#username').val('');
	$('#password').val('');
	$('#registerLoginForm').dialog('close');
}

Interface.changeOnLogin = function() 
{
	$('#userInfo').text('Hi, ' + Client.currentUser.username + '!');
	$('#login, #register').hide();
	$('#logout, #createGame, #sendMessage').show();
	$('#registerLoginForm').dialog('close');
	Client.currentUser.isReady = undefined;
	Client.currentUser.gameId = undefined;
	if (Client.gameList)
	{
		for (var i = 0; i < Client.gameList.length; ++i)
		{
			for (var j = 0; j < Client.gameList[i].players.length; ++j)
				if (Client.gameList[i].players[j].userId === 
						Client.currentUser.userId)
				{
					Client.currentUser.isReady = Client.gameList[i].players[j].isReady;
					Client.currentUser.gameId = Client.gameList[i].gameId;
					break;
				}
			if (Client.currentUser.gameId)
			{
				$('#createGame').hide();
				break;
			}
		}
	}
	updateGameList();
}
		
Interface.changeOnLogout = function() 
{
	updateGameList();
	$('#userInfo').text("You're not logged in, please login or register");
	$('#username, #password').val('');
	$('#login, [id=register]').show();
	$('#logout, [id*=join], [id*=leave], #createGame, #sendMessage').hide();
}

Interface.changeOnJoin = function() 
{
	updateGameList();
	$('[id*=join], #createGame').hide();
	var gameId = Client.currentUser.gameId;
	$('#leave' + gameId + ', #setReadinesStatus' + gameId).show();
}

Interface.changeOnLeave = function() 
{
	updateGameList();
	$('[id*=join], #createGame').show();
	$('[id*=leave], #setReadinesStatus' + Client.currentUser.gameId).hide();
}

Interface.changeOnCreateGame = function(game)
{
	updateGameList();
	$('[id*=join], #createGame').hide();
	$('#leave' + Client.currentUser.gameId).show();
}

Interface.changeOnSetReadinessStatus = function()
{
	updateGameList();
	Client.currentUser.isReady = 1 - $('#setReadinesStatus' + 
		Client.currentUser.gameId).prop('isReady');
	$('#setReadinesStatus' + Client.currentUser.gameId).prop('isReady', 
		Client.currentUser.isReady).html(Client.currentUser.isReady ? 'I am not ready' : 
		'I am ready');
}

