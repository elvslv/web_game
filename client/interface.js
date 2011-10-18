function fillGameList()
{
	$('#gameList').empty();
	for (var i = 0; i < gamesList.length; ++i)
	{
		$('#gameList').append('<li id = "game' + gamesList[i]['gameId'] + '"><a href="#">' + gamesList[i]['gameName'] + '</a></li>');
		$('#game' + gamesList[i]['gameId']).append('<ul id = "game' + gamesList[i]['gameId'] + 'Descr"></ul>')
		game = $('#game' + gamesList[i]['gameId']  + 'Descr');
		for (var j = 0; j < gameFields.length - 1; ++j)
		{
			if (gameFields[i] != 'gameDescr' || gameFields[i]['gameDescr'] != undefined)
				game.append('<p>' + gameFieldDescriptions[j] + ': ' + gamesList[i][gameFields[j]] + '</p>');
		}
		game.append('<div id = "players' + gamesList[i]['gameId'] +'">Players:</div>');
		for (var j = 0; j < gamesList[i].players.length; ++j)
		{
			$('#players' + gamesList[i]['gameId']).append('<p>' + 
				playerFieldDescription[j] + ': ' + gamesList[i]['players'][playerFields[j]] + '</p>');
		}
		game.append('<button id = "join' + gamesList[i]['gameId'] + '" style = "display: none">Join</button>');
		$('#join' + gamesList[i]['gameId']).prop('gameId', gamesList[i]['gameId']);
		$('#join' + gamesList[i]['gameId'])
			.button()
			.click(function()
			{
				responseGameId = $(this).prop('gameId');
				sendQuery('{"action": "joinGame", "sid": ' + sid +', "gameId": ' + $(this).prop('gameId') + '}', joinGameResponse);
			});
		game.append('<button id = "leave' + gamesList[i]['gameId'] + '" style = "display: none">Leave</button>');
		$('#leave' + gamesList[i]['gameId'])
			.button()
			.click(function()
			{
				sendQuery('{"action": "leaveGame", "sid": ' + sid +'}', leaveGameResponse);
			});
		game.append('<button id = "setReadinesStatus' + gamesList[i]['gameId'] + 
			'" style = "display: none">I am ready</button>');
		$('#setReadinesStatus' + gamesList[i]['gameId']).prop('isReady', 0);
		$('#setReadinesStatus' + gamesList[i]['gameId'])
			.button()
			.click(function()
			{
				sendQuery('{"action": "setReadinessStatus", "sid": ' + sid + ', "isReady": ' + 
					(1 - $('#setReadinesStatus' + gamesList[i]['gameId']).prop('isReady', 0)) 
					+ '}', setRadinessStatusResponse);
			});		
		if (sid)
		{
			if (!gameId)
				$('[id*=join]').show();
			else
			{
				$('#leave' + gameId).show();
				$('#setReadinesStatus' + gameId).show();
			}
		}

	}
	initGameList();
}

function changeOnLogin()
{
	$('#userInfo').text('Hi, ' + username + '!');
	$('#login').hide();
	$('#logout').show();
	$('#createGame').show();
	$('#registerLoginForm').dialog('close');
	isReady = undefined;
	gameId = undefined;
	if (gamesList)
		for (var i = 0; i < gamesList.length; ++i)
		{
			for (var j = 0; j < gamesList[i].players; ++j)
				if (gamesList[i].players[j].userId == userId)
				{
					isReady = gamesList[i].players[j].isReady;
					gameId = gamesList[i].gameId;
					break;
				}
			if (gameId)
				break;
		}

	if (gameId)
	{
		$('#setReadinessStatus' + gameId).prop('isReady', !isReady);
		changeOnJoin();
	}
	else
	{
		$('[id*=join]').show();
		$('[id*=leave]').hide();
	}
		
}

function changeOnLogout()
{
	$('#userInfo').text("You're not logged in, please login or register");
	$('#login').show();
	$('#logout').hide();
	$('[id*=join]').hide();
	$('[id*=leave]').hide();
	$('#createGame').hide();

}

function changeOnJoin()
{
	$('[id*=join]').hide();
	$('#leave' + gameId).show();
	$('#setReadinesStatus' + gameId).show();
	$('#createGame').hide();
}

function changeOnLeave()
{
	$('[id*=join]').show();
	$('[id*=leave]').hide();
	$('#setReadinesStatus' + gameId).hide();
	$('#createGame').show();
}

function addGame(game)
{
	newGame = {};
	for (var i = 0; i < gameFields.length; ++i)
		if (game[gameFields[i]] != undefined)
		{
			newGame[gameFields[i]] = game[gameFields[i]]
		}
	gamesList.push(newGame);
}

function changeOnCreateGame(game)
{
	addGame(game); //must be rewritten!!!
	fillGameList();
	gameId = game['gameId'];
	$('[id*=join]').hide();
	$('#leave' + gameId).show();
	$('#createGame').hide();
}

function changeOnSetReadinessStatus()
{
	isReady = 1 - $('#setReadinesStatus' + gameId).prop('isReady');
	$('#setReadinesStatus' + gameId).prop('isReady', isReady);
	$('#setReadinesStatus' + gameId).html(isReady ? 'I am not ready' : 'I am ready');
}