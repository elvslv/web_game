var Interface = {};

Interface.fillGameList = function() {
	var gamesList = Client.gameList;
	$('#gameList').empty();
	for (var i = 0; i < gamesList.length; ++i)
	{
		$('#gameList').append('<li id = "game' + gamesList[i].gameId + '"><a href="#">' + gamesList[i].gameName + '</a></li>');
		$('#game' + gamesList[i].gameId).append('<ul id = "game' + gamesList[i].gameId + 'Descr"></ul>')
		game = $('#game' + gamesList[i].gameId  + 'Descr');
		for (var j = 0; j < Client.gameProperties.length - 1; ++j)
		{
			if (Client.gameProperties[j] !== 'gameDescr' || gamesList[i].gameDescr) {
				val = Client.gameProperties[j] === 'state' ? 
					Client.states[gamesList[i][Client.gameProperties[j]]] : 
					gamesList[i][Client.gameProperties[j]];
				game.append('<p>' + Client.gameProperties[j] + ': ' + val + '</p>');
			}
		}
		game.append('<button id = "join' + gamesList[i].gameId + '" style = "display: none">Join</button>');
		$('#join' + gamesList[i].gameId).prop('gameId', gamesList[i].gameId);
		$('#join' + gamesList[i].gameId)
			.button()
			.click(function()
			{
				Client.currGameState.id = $(this).prop('gameId');
				sendQuery('{"action": "joinGame", "sid": ' + Client.currentUser.sid +', "gameId": ' + $(this).prop('gameId') + '}', joinGameResponse);
			});
		game.append('<button id = "leave' + gamesList[i].gameId + '" style = "display: none">Leave</button>');
		$('#leave' + gamesList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery('{"action": "leaveGame", "sid": ' + Client.currentUser.sid +'}', leaveGameResponse);
			});
		if (Client.currentUser.sid && gamesList[i].playersNum > 1)		
		{
			if (!Client.currentUser.gameId)
				$('#join' + Client.currentUser.gameId).show();
			else
				$('#leave' + Client.currentUser.gameId).show();
		}

	}
	initGameList();
}


Interface.changeOnRegistration = function() { 
	$('#username').val('');
	$('#password').val('');
	$('#registerLoginForm').dialog('close');
}

Interface.changeOnLogin = function() {
	$('#userInfo').text('Hi, ' + Client.currentUser.username + '!');
	$('#login').hide();
	$('#logout').show();
	$('#createGame').show();
	$('#registerLoginForm').dialog('close');
	$('[id*=join]').show();
	$('[id*=leave]').hide();
	$('[id=register]').hide();
}

Interface.changeOnLogout = function() {
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

Interface.changeOnJoin = function() {
	$('[id*=join]').hide();
	$('#leave' + Client.currentUser.gameId).show();
	$('#createGame').hide();
}

Interface.changeOnLeave = function() {
	$('[id*=join]').show();
	$('[id*=leave]').hide();
	$('#createGame').show();
}

Interface.changeOnCreateGame = function(game) {
	Interface.fillGameList();
	$('#createGame').hide();
}