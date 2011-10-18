var Interface = {};

Interface.fillGameList = function() 
{
	var gamesList = Client.gameList;
	$('#gameList').empty();
	$('#gameListInfo').html('There are no avaliable games');
	for (var i = 0; i < gamesList.length; ++i)
	{
		if (gamesList[i].state == 3/*finished*/)
			continue;
		$('#gameListInfo').html('Games:');
		$('#gameList').append('<li id = "game' + gamesList[i].gameId + '"><a href="#">' + 
			gamesList[i].gameName + '</a></li>');
		$('#game' + gamesList[i].gameId).append('<ul id = "game' + gamesList[i].gameId + 
			'Descr"></ul>')
		game = $('#game' + gamesList[i].gameId  + 'Descr');
		for (var j = 0; j < Client.gameProperties.length - 1; ++j)
		{
			if (Client.gameProperties[j] !== 'gameDescr' || gamesList[i].gameDescr) 
			{
				val = Client.gameProperties[j] === 'state' ? 
					Client.states[gamesList[i][Client.gameProperties[j]]] : 
					gamesList[i][Client.gameProperties[j]];
				game.append('<p>' + Client.gameProperties[j] + ': ' + val + '</p>');
			}
		}
		game.append('<p>Players:</p><div id = "players' + gamesList[i].gameId +'" class="user"></div>');
		for (var j = 0; j < gamesList[i].players.length; ++j)
			for (var k = 0; k < Client.playerProperties.length; ++k)	
				$('#players' + gamesList[i].gameId).append('<p>' + Client.playerProperties[k] + 
					': ' + gamesList[i].players[j][Client.playerProperties[k]] + '</p>');
		game.append('<button id = "join' + gamesList[i].gameId + 
			'" style = "display: none">Join</button>');
		$('#join' + gamesList[i].gameId).prop('gameId', gamesList[i].gameId);
		$('#join' + gamesList[i].gameId)
			.button()
			.click(function()
			{
				Client.currGameState.id = $(this).prop('gameId');
				sendQuery('{"action": "joinGame", "sid": ' + Client.currentUser.sid +
					', "gameId": ' + $(this).prop('gameId') + '}', joinGameResponse);
			});
		game.append('<button id = "leave' + gamesList[i].gameId + 
			'" style = "display: none">Leave</button>');
		$('#leave' + gamesList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery('{"action": "leaveGame", "sid": ' + Client.currentUser.sid +'}', 
					leaveGameResponse);
			});
		game.append('<button id = "setReadinesStatus' + gamesList[i].gameId + 
			'" style = "display: none">I am ready</button>');
		$('#setReadinesStatus' + gamesList[i].gameId).prop('isReady', 0);
		$('#setReadinesStatus' + gamesList[i].gameId).prop('gameId', gamesList[i].gameId);
		$('#setReadinesStatus' + gamesList[i].gameId)
			.button()
			.click(function()
			{
				gameId = $(this).prop('gameId');
				sendQuery('{"action": "setReadinessStatus", "sid": ' + Client.currentUser.sid +
					', "isReady": ' + (1 - $(this).prop('isReady')) + '}', setReadinessStatusResponse);
			});		
		if (Client.currentUser && Client.currentUser.sid)
		{
			if (!Client.currentUser.gameId)
				$('[id*=join]').show();
			else
			{
				if (Client.currGameState.state == 1)
				{
					$('#setReadinesStatus' + gamesList[i].gameId).prop('isReady', 
						Client.currentUser.isReady);
					$('#setReadinesStatus' + Client.currentUser.gameId).html(Client.currentUser.isReady ? 
						'I am not ready' : 'I am ready');
					$('#setReadinesStatus' + Client.currentUser.gameId).show();
				}
				$('#leave' + Client.currentUser.gameId).show();
			}
		}

	}
	initGameList();
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
				if (Client.gameList[i].players[j].userId == 
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
	Client.currentUser.gameId = game['gameId'];
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