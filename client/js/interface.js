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
		'ok': function(){
			for (var i = 0; i < Client.mapList.length; ++i)
				Client.mapList[i].graphicsThmb.clear();
			$('#browseMapsForm').dialog('close');
		}
	}, 
	{
		'name': 'uploadMap',
		'title': 'Create new map',
		'ok':  function() 
		{
			var mapName = $('#mapName'),
				playersNum = $('#playersNum'),
				turnsNum = $('#turnsNum'),
				regionList = $('#regionList');
			query = makeQuery(['action', 'mapName', 'playersNum', 'turnsNum', 'regions', 'thumbnail', 
				'picture'], ['uploadMap', mapName.val(), parseInt(playersNum.val()), 
				parseInt(turnsNum.val()), regionList.val(), 'maps/mapThumb.jpg', 'maps/map.jpg']);
			sendQuery(query, uploadMapResponse);
		}
	},
	{
		'name': 'loadGameForm',
		'title': 'Load game',
		'ok': function()
		{
			if (!$('#gameActions').val().length)
				$('#loadGameOutput').html('List of actions can not be empty');
			else
				sendQuery(makeQuery(['action', 'sid', 'actions'],
					['loadGame', user().sid, $.evalJSON($('#gameActions').val())]),
					loadGameResponse);
		}
	},
	{
		'name': 'saveGameForm',
		'title': 'Save game',
		'ok': function()
		{
			$(this).dialog('close');
		}
	}
	];

Interface.updatePage = function()
{
	if (Client.currentUser && Client.currentUser.gameId)
		updateGameState();
	else
		updateGameList();
	//updateChat();
	window.setTimeout("Interface.updatePage()", 5000);
};



Interface.prepareForActions = function()
{
	Interface.prepareForSetReadinessStatus();
	Interface.prepareForRaceSelect();
	Interface.prepareForDecline();
	Interface.prepareForFinishTurn();
	Interface.prepareForSelectFriend();
	Interface.prepareForThrowDice();
	Interface.prepareForRedeploy();
	Interface.prepareForDefend();
	Interface.prepareForDragonAttack();
	Interface.prepareForConquest();
};


Interface.updateChatBox = function()
{		
	$('#messageBox').change(onMessageChange);
	$('#refreshChat')
		.button()
		.click(function() {
			updateChat();
		});
	$('#sendMessage')
		.button()
		.click(function() {
			sendQuery(makeQuery(['action', 'text', 'sid'], ['sendMessage', $('#messageBox').val(), 
				Client.currentUser.sid]), sendMessageResponse);
		});
	$('#refreshChat').show();
}

Interface.updateGameTab = function()
{
	if (Interface.needToCreateGameTab)
	{
		Interface.needToCreateGameTab = false;
		$('#tabs').tabs('add', '#ui-tabs-1', Client.currGameState.name, 1);
		$('#ui-tabs-1').append(HtmlBlocks.gameTab());
		$('#chatMainTab').empty();
		$('#chatGameTab').append(HtmlBlocks.chatBlock());
		$('#chatGameTab').css({width: '100%'});
		Interface.updateChatBox();
		$('#setRadinessStatusInGame').button().click(setReadinessStatusClick);
		$('#finishTurn').button().click(finishTurnClick);
		$('#throwDice').button().click(throwDiceClick);
		$('#changeRedeployStatus').button().click(changeRedeployStatusClick);
		$('#redeploy').button().click(redeployClick);
		$('#defend').button().click(defendClick);
		$('#saveGame').button().click(saveGameClick);
		Graphics = new RaphaelGraphics(game().map);
		Graphics.drawMap();
	}
	
	$('#usersInCurGame').empty();
	$('#usersInCurGameTemplate').tmpl(game().players,
	{

		color: function(id)
		{
			return 'background-color:' + (Graphics.colors ? 
				Graphics.colors[id] : 'white');
		},
		activePlayer: function()
		{
			return game().activePlayerIndex !== undefined &&
				game().players[game().activePlayerIndex].id;
		},
		defendingPlayer: function()
		{
			return game().defendingPlayerIndex !== undefined && 
				game().players[game().defendingPlayerIndex].id;
		},
		currentUser: function()
		{
			return Client.currentUser.id;
		},

		showTokensInHand : function()
		{
			return !(game().redeployStarted  || game().defendStarted);
		},

		freeTokens : function()
		{
			return user().freeTokens;
		}

		
	}).appendTo('#usersInCurGame');	
	Graphics.update(game().map);
	$('#visibleTokenBadges').empty();
	if (game().tokenBadges.length)
		$('#visibleTokenBadges').append('<p>Visible token badges: </p>');
	$('#visibleTokenBadgesTemplate').tmpl(Client.currGameState.tokenBadges).appendTo('#visibleTokenBadges');

	$('#leaveGame')
		.button()
		.click(function(){
			sendQuery(makeQuery(['action', 'sid'], ['leaveGame', user().sid]), 
				leaveGameResponse);
		});
	$('#leaveGame').show();
	$('#saveGame').show();
	Interface.prepareForActions();
}

Interface.prepareForSetReadinessStatus = function()
{
	if (Client.currGameState.state == GAME_WAITING)
	{
		$('#setRadinessStatusInGame').prop('isReady', Client.currentUser.isReady);
		$('#setRadinessStatusInGame').html(Client.currentUser.isReady ? 'I am not ready' : 
			'I am ready');
		$('#setRadinessStatusInGame').show();
	}
	else
		$('#setRadinessStatusInGame').hide();
}

Interface.prepareForRaceSelect = function()
{
	if (canSelectRaces())
		for (var i = 0; i < game().tokenBadges.length; ++i)
			if (canSelectRace(i))
			{
				$('#select' + i)
					.button({icons: { primary: "ui-icon-check" }})
					.click(function(j){
						return function(){
							sendQuery(makeQuery(['action', 'sid', 'position'], 
								['selectRace', Client.currentUser.sid, j]), selectRaceResponse);					
						}
				}(i));
				$('#select' + i).show();	
			}
}

Interface.prepareForDecline = function()
{
	if (canDecline())
	{
		$('#decline')
			.button()
			.click(function(){
				sendQuery(makeQuery(['action', 'sid'], ['decline', Client.currentUser.sid]),
					declineResponse);
			});
		$('#decline').show();
	}
}

Interface.prepareForFinishTurn = function()
{
	if (canFinishTurn())
		$('#finishTurn').show();
	else
		$('#finishTurn').hide();
}

Interface.prepareForDefend = function()
{
	if (canBeginDefend())
		$('#defend').show();
	else
		$('#defend').hide();
}

Interface.prepareForDragonAttack = function()
{
	if (canBeginDragonAttack())
		user().freePowerTokens = user().specPower().bonusNum;
}

Interface.prepareForConquest = function()
{
	var reg, i;
	if (canBeginConquer()){
		if (!game().conquestStarted){
			for (i = 0; i < game().map.regions.length; i++){
				reg = game().map.regions[i];
				reg.conquerable = canConquer(reg);
			}
			game().conquestStarted = true;
		}
	} else
		game().conquestStarted = false;	
}

Interface.prepareForSelectFriend = function()
{
	if (!canChooseFriend())
		return;
	var cnt = 0;
	for (var i = 0; i < game().players.length; ++i)
		if (selectFriend(game().players[i]))
		{
			$('#selectFriend' + game().players[i].id)
				.button()
				.click(function(j){
					return function(){
						sendQuery(makeQuery(['action', 'sid', 'friendId'], 
							['selectFriend', user().sid, j]), selectFriendResponse);
					}
				}(game().players[i].id));	
			$('#selectFriend' + game().players[i].id).show();
		}
}

Interface.prepareForRedeploy = function()
{
	if (!canBeginRedeploy())
	{
		$('#changeRedeployStatus').hide();
		$('#redeploy').hide();
		Client.currGameState.redeployStarted = false;
		return;
	}
	$('#changeRedeployStatus').show();
}

Interface.prepareForThrowDice = function()
{
	if (canThrowDice())
		$('#throwDice').show();
	else
		$('#throwDice').hide();
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
		$('#gameListInfo').html('Games:');
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
		for (var j = 0; j < Client.gameList[i].players.length; ++j)
			if (Client.gameList[i].players[j].userId === 
					Client.currentUser.id)
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
		while ((lastSortIndex < showingGames.length) && 
			(showingGames[lastSortIndex] < Client.gameList[i].gameId))
			++lastSortIndex;
		if ((lastSortIndex < showingGames.length) && 
			(showingGames[lastSortIndex] === Client.gameList[i].gameId))
			$('#gameList:nth-child(' + (i + 1) + ') ul').show();
		
		if (Client.currentUser.gameId === Client.gameList[i].gameId)	
			Client.currentUser.gameIndex = i;
		$('#join' + Client.gameList[i].gameId)
			.button()
			.click(function(j)
			{
				return function()
				{
					var gameId = Client.gameList[j].gameId;
					Client.newGameId = gameId;
					sendQuery(makeQuery(['action', 'sid', 'gameId'], ['joinGame', 
						Client.currentUser.sid, gameId]), joinGameResponse);
				}
			}(i));
	}
	if (Client.currentUser && Client.currentUser.sid)
	{
		if (!Client.currentUser.gameId)
		{
			for (var i = 0; i < Client.gameList.length; ++i)
			{
				if (Client.gameList[i].state === GAME_WAITING)
					$('#join' + Client.gameList[i].gameId).show();
			}
		}
	}
	Interface.checkForExistingGame();
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

Interface.checkForExistingGame = function()
{
	if (Client.gameList)
	{
		for (var i = 0; i < Client.gameList.length; ++i)
		{
			for (var j = 0; j < Client.gameList[i].players.length; ++j)
				if (Client.gameList[i].players[j].userId === 
						Client.currentUser.id)
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

Interface.changeOnLogin = function() 
{
	$('#userInfo').text('Hi, ' + Client.currentUser.username + '!');
	$('#login, #register').hide();
	$('#logout, #createGame, #loadGame').show();
	$('#registerLoginForm').dialog('close');
	Client.currentUser.isReady = undefined;
	Client.currentUser.gameId = undefined;
}
		
Interface.createGameTab = function(gameName)
{
	$('#gameListInfo').html('');
	Interface.needToCreateGameTab = true;
}

Interface.removeGameTab = function()
{
	$('#chatGameTab').empty();
	$('#chatMainTab').empty();
	$('#chatMainTab').append(HtmlBlocks.chatBlock());
	Interface.updateChatBox();
	$('#tabs').tabs('remove', 1);
}

Interface.changeOnJoinGame = function()
{
	$('#createGame').hide();
	$('#gameList').hide();
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
	$('#logout, [id*=join], [id*=leave], #createGame, #sendMessage, #loadGame').hide();
	Interface.removeGameTab();
}

Interface.changeOnLeave = function() 
{
	$('[id*=join], #createGame').show();
	Interface.removeGameTab();
}

Interface.changeOnCreateGame = function()
{
	Client.currentUser.isReady = false;
	Interface.changeOnJoinGame();
}

Interface.changeOnSetReadinessStatus = function()
{
	Client.currentUser.isReady = 1 - Client.currentUser.isReady;
	title = Client.currentUser.isReady ? 'I am not ready' : 
		'I am ready';
	if ($('#setRadinessStatusInGame'))
		$('#setRadinessStatusInGame').prop('isReady', Client.currentUser.isReady).html(title);
}

