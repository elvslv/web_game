function fillGameList()
{
	var sid = Client.currentUser.sid, gameId = Client.currentUser.gameId;
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
		if (sid)
		{
			if (!gameId)
				$('[id*=join]').show();
			else
				$('#leave' + gameId).show();
		}

	}
//	initGameList();
}
function changeOnLogin()
{
	$('#userInfo').text('Hi, ' + Client.currentUser.name + '!');
	$('#login').hide();
	$('#logout').show();
	$('#createGame').show();
	$('#registerLoginForm').dialog('close');
	$('[id*=join]').show();
	$('[id*=leave]').hide();
}

function changeOnLogout()
{
	$('[id*=join]').hide();
	$('[id*=leave]').hide();
	$('#createGame').hide();

}

function changeOnJoin()
{
	$('[id*=join]').hide();
	$('#leave' + gameId).show();
	$('#createGame').hide();
}

function changeOnLeave()
{
	$('[id*=join]').show();
	$('[id*=leave]').hide();
	$('#createGame').show();
}

function makeGame(data)
{
	var newGame = {};
	for (prop in Client.gameProperties)
		if (data.hasItsOwnProperty(prop)) {
			newGame.prop = data.prop
		}
	gamesList.push(newGame);
	return newGame;
}

function changeOnCreateGame(game)
{
	var newGame = addGame(game); //must be rewritten!!!
	fillGameList();
	Client.currentUser.game = newGame;
	$('[id*=join]').hide();
	$('#leave' + gameId).show();
	$('#createGame').hide();
}