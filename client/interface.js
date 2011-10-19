var Interface = {};

Interface.fillGameList = function() 
{
	$('#gameList').empty();
	if(Client.gameList)
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
	for (var i = 0; i < Client.gameList.length; ++i)
	{
		$('#join' + Client.gameList[i].gameId).prop('gameId', Client.gameList[i].gameId);
		$('#join' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				Client.currGameState.id = $(this).prop('gameId');
				sendQuery('{"action": "joinGame", "sid": ' + Client.currentUser.sid +
					', "gameId": ' + $(this).prop('gameId') + '}', joinGameResponse);
			});
		$('#leave' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery('{"action": "leaveGame", "sid": ' + Client.currentUser.sid +'}', 
					leaveGameResponse);
			});
		$('#setReadinesStatus' + Client.gameList[i].gameId).prop('isReady', 0);
		$('#setReadinesStatus' + Client.gameList[i].gameId).prop('gameId', 
			Client.gameList[i].gameId);
		$('#setReadinesStatus' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				gameId = $(this).prop('gameId');
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
			if (Client.currGameState.state === 1)
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


Interface.changeOnRegistration = function() 
{ 
	$('#username').val('');
	$('#password').val('');
	$('#registerLoginForm').dialog('close');
}

Interface.changeOnLogin = function() 
{
	$('#userInfo').text('Hi, ' + Client.currentUser.username + '!');
	$('#login').hide();
	$('#logout').show();
	$('#register').hide();
	$('#createGame').show();
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
					setGame(Client.currentUser.gameId);
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
	/*if (Client.currentUser.gameId)
	{
		$('#setReadinessStatus' + Client.currentUser.gameId).prop('isReady', 
			Client.currentUser.isReady);
		$('#setReadinesStatus' + Client.currentUser.gameId).html(Client.currentUser.isReady ? 
		'I am not ready' : 'I am ready');
		$('[id*=join]').hide();
		$('#leave' + Client.currentUser.gameId).show();
		$('#setReadinesStatus' + Client.currentUser.gameId).show();
		$('#createGame').hide();
	}
	else
	{
		$('[id*=join]').show();
		$('[id*=leave]').hide();
		$('[id=register]').hide();
	}*/
}
		
Interface.changeOnLogout = function() 
{
	updateGameList();
	$('#userInfo').text("You're not logged in, please login or register");
	$('#username').val('');
	$('#password').val('');
	$('#login').show();
	$('#logout').hide();
	$('[id=register]').show();
	$('[id*=join]').hide();
	$('[id*=leave]').hide();
	$('#createGame').hide();

}

Interface.changeOnJoin = function() 
{
	updateGameList();
	$('[id*=join]').hide();
	$('#leave' + Client.currentUser.gameId).show();
	$('#setReadinesStatus' + Client.currentUser.gameId).show();
	$('#createGame').hide();
}

Interface.changeOnLeave = function() 
{
	updateGameList();
	$('[id*=join]').show();
	$('[id*=leave]').hide();
	$('#setReadinesStatus' + Client.currentUser.gameId).hide();
	$('#createGame').show();
}

Interface.changeOnCreateGame = function(game)
{
	updateGameList();
	$('[id*=join]').hide();
	$('#leave' + Client.currentUser.gameId).show();
	$('#createGame').hide();
}

Interface.changeOnSetReadinessStatus = function()
{
	updateGameList();
	Client.currentUser.isReady = 1 - $('#setReadinesStatus' + 
		Client.currentUser.gameId).prop('isReady');
	$('#setReadinesStatus' + Client.currentUser.gameId).prop('isReady', 
		Client.currentUser.isReady);
	$('#setReadinesStatus' + Client.currentUser.gameId).html(Client.currentUser.isReady ? 
		'I am not ready' : 'I am ready');
}
