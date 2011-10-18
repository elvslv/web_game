function registerResponse(data)
{
	switch(data['result'])
	{
		case 'badPassword':
			$('#dialogInfo').text('Invalid password');
			break;
		case 'badUsername':
			$('#dialogInfo').text('Invalid username');
			break;
		case 'badJson': //may it be???
			$('#dialogInfo').text('Invalid data');
			break;
		case 'usernameTaken':
			$('#dialogInfo').text('User with the same name have already registered');
			break;
		case 'ok':
			alert("You're were registered, congratulations!");
			Interface.changeOnRegistration();
			break;
		default:
			$('#dialogInfo').text('Unknown server response' + data);
	}
}

function loginResponse(data)
{
	var sid, username;
	switch(data['result'])
	{
		case 'badUsernameOrPassword':
			$('#dialogInfo').text('Invalid username or password');
			break;
		case 'badJson': //may it be???
			$('#dialogInfo').text('Invalid data');
			break;
		case 'ok':
			sid = data['sid'];
			userId = data['userId'];
			username = $('#username').val();
			Client.currentUser = Client.newUser(username, id);
			Client.currentUser.sid = sid;
			Interface.changeOnLogin();
			break;
		default:
			$('#dialogInfo').text('Unknown server response' + data);
	}
}

function logoutResponse(data)
{
	switch(data['result'])
	{
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'ok':
			delete Client.currentUser;
			Interface.changeOnLogout();
			break;
		default:
			alert('Unknown server response' + data);
	}
}

function getGameListResponse(data)
{
	if (data['result'] != 'ok' || !data['games'])
	{
		alert("Unknown server response: " + data);
		return;
	}
	Client.gameList = data['games'];
	Interface.fillGameList();
}

function joinGameResponse(data)
{
	switch(data['result'])
	{
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'badGameId': //may it be???
			alert('Invalid game id');
			break;
		case 'badGameState': 
			alert('You can not join game that have been already started or finished');
			break;
		case 'alreadyInGame': 
			alert("You're already in game");
			break;
		case 'tooManyPlayers': 
			alert('There is no free space on map');
			break;
		case 'ok':
			Client.currentUser.gameId = Client.currGameState.id;
			delete Client.currGameState.id;
			Interface.changeOnJoin();
			break;
		default:
			alert('Unknown server response');
	}
}

function leaveGameResponse(data)
{
	switch(data['result'])
	{
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'notInGame': //may it be???
			alert("You're not playing");
			break;
		case 'ok':
			delete Client.currentUser.gameId;
			Interface.changeOnLeave();
			break;
		default:
			alert('Unknown server response');
	}
}

function createGameResponse(data)
{
	var game;
	switch(data['result'])
	{
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'badMapId': 
			alert('Invalid map id');
			break;
		case 'badGameName': 
		case 'gameNameTaken': 
			alert('Invalid game name');
			break;
		case 'badGameDescription': 
			alert('Invalid game description');
			break;
		case 'alreadyInGame': 
			alert("You're already playing");
			break;
		case 'ok':
			game = Client.newGame(data['gameId']);
			Client.currentUser.gameId = game.gameId;
			Client.gameList.push(game);
			Interface.changeOnCreateGame(game);
			$('#createGameForm').dialog('close');
			break;
		default:
			alert('Unknown server response');
	}
}