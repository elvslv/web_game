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
			$('#dialogInfo').text('Unknown server response' + data.toString());
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
			Client.currentUser = Client.newUser(username, userId, sid);
			Interface.changeOnLogin();
			break;
		default:
			$('#dialogInfo').text('Unknown server response' + data.toString());
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
			alert('Unknown server response' + data.toString());
	}
}

function getGameListResponse(data)
{
	if (data['result'] != 'ok' || !data['games'])
	{
		alert("Unknown server response: " + data.toString());
		return;
	}
	Client.gameList = data['games'];
	Interface.fillGameList();
}

function getMapListResponse(data, beforeCreateGame)
{
	if (data['result'] != 'ok' || !data['maps'])
	{
		alert("Unknown server response: " + data.toString());
		return;
	}
	Client.mapList = data['maps'];
	$('#mapChooseTemplate').tmpl(Client.mapList).appendTo('#mapList');
	if (beforeCreateGame)
		$('#createGameForm').dialog('open');
}



/*

##  Client.lastGame is a temporary variable used
##  in stuff like createGame and joinGame when we need
##  to know the last data user entered. There's no real need to update it.
##  It was only used when checking game state and there was a way to get rid of this 

function setGame(gameId)
{
	fields = ['gameId', 'gameName', 'mapId', 'activePlayerId', 'state', 'turn', 'turnsNum', 
		'maxPlayersNum']
	for (var i = 0; i < Client.gameList.length; ++i)
	{
		if (Client.gameList[i].gameId == gameId)
		{
			
			for (var j = 0; j < fields.length; ++j)
				Client.lastGame[fields[j]] = Client.gameList[i][fields[j]]
		}
	}
}
*/

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
			Client.currentUser.gameId = Client.lastGame.id;
		//	setGame(Client.currentUser.gameId)
			Interface.changeOnJoin();
			break;
		default:
			alert("Unknown server response: " + data.toString());
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
			Client.currentUser.gameId = null;
			Interface.changeOnLeave();
			break;
		default:
			alert("Unknown server response: " + data.toString());
	}
}

function createGameResponse(data)
{
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
			Client.currentUser.gameId = data.gameId;
		//	setGame(Client.currentUser.gameId);
			Interface.changeOnCreateGame(data);
			$('#createGameForm').dialog('close');
			break;
		default:
			alert('Unknown server response' + data.toString());
	}
}

function setReadinessStatusResponse(data)
{
	switch(data['result'])
	{
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'badJson': //may it be???
		case 'badReadinessStatus': 
			alert('Invalid data');
			break;
		case 'notInGame': 
			alert("You're not playing");
			break;
		case 'badGameState': 
			alert('You can not join game that have been already started or finished');
			break;
		case 'ok':
			Interface.changeOnSetReadinessStatus();
			break;
		default:
			alert('Unknown server response' + data.toString());
	}
}
function getMessagesResponse(data)
{
	switch(data['result'])
	{
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'ok':
			Client.messages = Client.messages.concat(data['messages']);
			Interface.changeOnGetMessages();
			break;
		default:
			alert('Unknown server response' + data);
	}
}
function sendMessageResponse(data)
{
	switch(data['result'])
	{
		case 'badJson': //may it be???
			alert('Invalid data');
			break;
		case 'badUserSid':
			alert('Invalid sid'); //?!!!
			break;
		case 'ok':
			$('#messageBox').val('');
			updateChat();
			break;
		default:
			alert('Unknown server response' + data);
 	}
}