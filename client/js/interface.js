var Interface = {};

Interface.needToCreateGameTab = false;

Interface.defaultDialogOptions = {
	'autoOpen': false,
	'height': 300,
	'width': 350,
	'modal': true
};

Interface.dialogs = [
	{
		'name': 'registerLoginForm', 
		'title': '', 
		'ok': function() 
		{
			var name = $('#username'),
				password = $('#password'),
				query = makeQuery(['action', 'username', 'password'], 
					[$('#registerLoginForm').prop('register') ? 'register' : 'login', name.val(), 
					password.val()]);
			sendQuery(query, function(data){
				if ($('#registerLoginForm').prop('register'))
					registerResponse(data);
				else
					loginResponse(data);
			});
		}
	}, 
	{
		'name': 'createGameForm',
		'title': 'Create new game',
		'ok': function() 
		{
			var gameName = $('#gameName'),
				gameDescription = $('#gameDescription'),
				mapId = Client.mapList[$('#mapList').prop('selectedIndex')].mapId,
				sid = Client.currentUser.sid,
				query = makeQuery(['action', 'sid', 'gameName', 'gameDescr', 'mapId'],
					['createGame', sid, gameName.val(), gameDescription.val(), mapId]);
			sendQuery(query, createGameResponse);
		}
	}, 
	{
		'name': 'browseMapsForm',
		'title': 'Maps',
		'ok': function(){}
	}, 
	{
		'name': 'uploadMap',
		'title': 'Create new map',
		'ok':  function() 
		{
			$('#submitThmb').click();
			var mapName = $('#mapName'),
				playersNum = $('#playersNum'),
				turnsNum = $('#turnsNum'),
				regionList = $('#regionList');
			query = makeQuery(['action', 'mapName', 'playersNum', 'turnsNum', 'regions', 'thumbnail', 
				'picture'], ['uploadMap', mapName.val(), playersNum.val(), turnsNum.val(), regionList.val(),
				filenames[0], filenames[1]]);
			sendQuery(query, uploadMapResponse);
		}
	}];

Interface.updatePage = function()
{
	if (Client.currentUser && Client.currentUser.gameId)
		updateGameState();
	else
		updateGameList();
	updateChat();
	window.setTimeout("Interface.updatePage()", 5000);
}

Interface.updateGameTab = function()
{
	if (Interface.needToCreateGameTab)
	{
		Interface.needToCreateGameTab = false;
		$('#tabs').tabs('add', '#ui-tabs-1', Client.currGameState.gameName, 1);
	}
	$('#ui-tabs-1').empty();
	$('#currentGameTemplate').tmpl(Client.currGameState,
		{
			opts: 
			{
				activePlayer: Client.currGameState.activePlayer
			}
		}).appendTo('#ui-tabs-1');
	$('#setRadinessStatusInGame').prop('isReady', Client.currentUser.isReady);
	$('#setRadinessStatusInGame').html(Client.currentUser.isReady ? 'I am not ready' : 
		'I am ready');
	$('#leaveGame')
		.button()
		.click(function(){
			sendQuery(makeQuery(['action', 'sid'], ['leaveGame', Client.currentUser.sid]), 
				leaveGameResponse);
		});
	$('#setRadinessStatusInGame')
		.button()
		.click(function(){
			sendQuery(makeQuery(['action', 'sid', 'isReady'], ['setReadinessStatus', 
				Client.currentUser.sid, (1 - $(this).prop('isReady'))]), setReadinessStatusResponse);
			;
		});
	$('#setRadinessStatusInGame, #leaveGame').show();
}


Interface.fillGameList = function(games) 
{
	if (Client.currentUser && Client.currentUser.gameId)
		return;
	showingGames = [];
	for (var i = 0; i < Client.gameList.length; ++i)
		if ($('#gameList:nth-child(' + (i + 1) + ') ul').is(':visible'))
			showingGames.push(Client.gameList[i].gameId);
	showingGames = showingGames.sort();
	Client.gameList = games;
	$('#gameList, #gameListInfo').empty();
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
	if (Client.currentUser && Client.currentUser.gameIndex)
		delete Client.currentUser.gameIndex;
	var lastSortIndex = 0;
	for (var i = 0; i < Client.gameList.length; ++i)
	{
		while ((lastSortIndex < showingGames.length) && 
			(showingGames[lastSortIndex] < Client.gameList[i].gameId))
			++lastSortIndex;
		if ((lastSortIndex < showingGames.length) && 
			(showingGames[lastSortIndex] === Client.gameList[i].gameId))
			$('#gameList:nth-child(' + (i + 1) + ') ul').show();
		
		if (Client.currentUser.gameId == Client.gameList[i].gameId)	
			Client.currentUser.gameIndex = i;
		$('#join' + Client.gameList[i].gameId)
			.button()
			.click(function(j)
			{
				return function()
				{
					var gameId = Client.gameList[j].gameId;
					Client.newGameId = gameId;
					sendQuery(makeQuery(['action', 'sid', 'gameId'], ['joinGame', Client.currentUser.sid, gameId]), 
						joinGameResponse);
				}
			}(i));
		$('#leave' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery(makeQuery(['action', 'sid'], ['leaveGame', Client.currentUser.sid]), 
					leaveGameResponse);
			});
		$('#setReadinesStatus' + Client.gameList[i].gameId).prop('isReady', 0);
		$('#setReadinesStatus' + Client.gameList[i].gameId)
			.button()
			.click(function()
			{
				sendQuery(makeQuery(['action', 'sid', 'isReady'], ['setReadinessStatus', 
					Client.currentUser.sid, (1 - $(this).prop('isReady'))]), setReadinessStatusResponse);
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
	$('#username, #password').val('');
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
				$('#gameList').hide();
				Interface.createGameTab();
				break;
			}
		}
	}
}
		
Interface.createGameTab = function(gameName)
{
	Interface.needToCreateGameTab = true;
}

Interface.removeGameTab = function()
{
	$('#tabs').tabs('remove', 1);
}

Interface.changeOnJoinGame = function()
{
	$('#createGame').hide();
	$('#gameList').hide();
	Client.currentUser.isReady = false;
	Interface.createGameTab();
}

Interface.changeOnJoin = function() 
{
	Interface.changeOnJoinGame();
}

Interface.changeOnLogout = function() 
{
	$('#userInfo').text("You're not logged in, please login or register");
	$('#username, #password').val('');
	$('#login, [id=register]').show();
	$('#logout, [id*=join], [id*=leave], #createGame, #sendMessage').hide();
	Interface.removeGameTab();
}

Interface.changeOnLeave = function() 
{
	$('[id*=join], #createGame').show();
	$('[id*=leave], #setReadinesStatus' + Client.currentUser.gameId).hide();
	Interface.removeGameTab();
}

Interface.changeOnCreateGame = function()
{
	Client.currentUser.isReady = false;
	Interface.changeOnJoinGame();
}

Interface.changeOnSetReadinessStatus = function()
{
	Client.currentUser.isReady = 1 - $('#setReadinesStatus' + 
		Client.currentUser.gameId).prop('isReady');
	title = Client.currentUser.isReady ? 'I am not ready' : 
		'I am ready';
	$('#setReadinesStatus' + Client.currentUser.gameId).prop('isReady', 
		Client.currentUser.isReady).html(title);
	if ($('#setRadinessStatusInGame'))
		$('#setRadinessStatusInGame').prop('isReady', Client.currentUser.isReady).html(title);
}

