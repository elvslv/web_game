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
			$('#registerLoginForm').dialog('close');
			break;
		default:
			$('#dialogInfo').text('Unknown server response');
	}
}

function loginResponse(data)
{
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
			username = $('#username').val();
			changeOnLogin();
			break;
		default:
			$('#dialogInfo').text('Unknown server response');
	}
}

function logoutResponse(data)
{
	switch(data['result'])
	{
		case 'badSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'ok':
			sid = undefined;
			username = undefined;
			$('#userInfo').text("You're not logged in, please login or register");
			$('#login').show();
			$('#logout').hide();
			break;
		default:
			alert('Unknown server response');
	}
}

function getGameListResponse(data)
{
	if (data['result'] != 'ok' || !data['games'])
	{
		alert("Unknown server response: " + data);
		return;
	}
	gamesList = data['games'];
	fillGameList();
}

function joinGameResponse(data)
{
	switch(data['result'])
	{
		case 'badSid':
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
			alert('You have been already joined to game');
			break;
		case 'tooManyPlayers': 
			alert('There is no free space on map');
			break;
		case 'ok':
			gameId = responseGameId;
			responseGameId = undefined;
			changeOnJoin();
			break;
		default:
			alert('Unknown server response');
	}
}

function leaveGameResponse(data)
{
	switch(data['result'])
	{
		case 'badSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'notInGame': //may it be???
			alert("You're not playing");
			break;
		case 'ok':
			gameId = undefined;
			responseGameId = undefined;
			changeOnLeave();
			break;
		default:
			alert('Unknown server response');
	}
}

function createGameResponse(data)
{
	response = responseGame;
	responseGame = undefined;
	switch(data['result'])
	{
		case 'badSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'badMapId': 
			alert('Invalid map id');
			break;
		case 'badGameName': 
			alert('Invalid game name');
			break;
		case 'badGameDescription': 
			alert('Invalid game description');
			break;
		case 'alreadyInGame': 
			alert('You have been already joined to game');
			break;
		case 'ok':
			changeOnCreateGame(response);
			$('#createGameForm').dialog('close');
			break;
		default:
			alert('Unknown server response');
	}
}