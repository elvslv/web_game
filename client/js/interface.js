var Interface = {};

Interface.needToCreateGameTab = false;

Interface.gameTab = function()
{
	return '<table>' +
		'<tr>' +
			'<td>' +
				'<button id = "leaveGame">leave</button>' +
			'</td>' +
			'<td rowspan = "12" valign = "top">' +
				'<div style = "margin-left: 250px; position: relative">' +
					'<div id = "imgdiv" style = "position: absolute;">' +
					'</div>' +
					'<img id = "imgmap" src = "' + game().map.picture + '" usemap = "#map">' +
					'<map name = "map" id = "map" valign = "top">' +
					'</map>' +
				'<div>' +
			'</td>' +
		'</tr>' +
		'<tr>' +
			'<td colspan = "2">' +
				'<button id = "setRadinessStatusInGame" style = "display: none"></button>' +
			'</td>' +
		'</tr>' +
		'<tr>' +
			'<td colspan = "2">' +
				'Players:' +
			'</td>' +
		'</tr>' +
		'<tr>' +
			'<td colspan = "2" id = "usersInCurGame">' +
				//'{{tmpl(players, $item.opts) "#usersInCurGameTemplate"}}' +
			'</td>' +
		'</tr>' +
		(tokenBadges.length 
		?
			'<tr>' +
				'<td colspan = "2">' +
					'Visible token badges:' +
				'</td>' +
			'</tr>' +
			'<tr>' +
				'<td colspan = "2" id = "visibleTokenBadges">' +
					//'{{tmpl(tokenBadges, $item.opts) "#visibleTokenBadgesTemplate"}}' +
				'</td>' +
			'</tr>' 
		: 
			'') +
		'<tr>' +
			'<td colspan = "2">' +
				'<button id = "finishTurn" style = "display: none">Finish turn</button>' +
			'</td>' +
		'</tr>' +
		'<tr>' +
			'<td>' +
				'<select id = "possibleFriends" style = "display: none">' +
				'</select>' +
			'</td>' +
			'<td>' +
				'<button id = "selectFriend" style = "display: none">Select friend</button>' +
			'</td>' +
		'</tr>' +
		'<tr>' +
			'<td colspan = "2">'  +
				'<button id = "throwDice" style = "display: none">Throw dice</button>' +
			'</td>' +
		'</tr>' +
	'</table>';
}

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
	//updateChat();
	window.setTimeout("Interface.updatePage()", 5000);
}



Interface.prepareForActions = function()
{
	Interface.prepareForSetReadinessStatus();
	Interface.prepareForRaceSelect();
	Interface.prepareForDecline();
	Interface.prepareForFinishTurn();
	Interface.prepareForSelectFriend();
	Interface.prepareForThrowDice();
}

Interface.updateGameTab = function()
{
	if (Interface.needToCreateGameTab)
	{
		Interface.needToCreateGameTab = false;
		$('#tabs').tabs('add', '#ui-tabs-1', Client.currGameState.name, 1);
		$('#ui-tabs-1').append(Interface.gameTab());
		$('#setRadinessStatusInGame')
			.button()
			.click(function(){
				sendQuery(makeQuery(['action', 'sid', 'isReady'], ['setReadinessStatus', 
					Client.currentUser.sid, (1 - $(this).prop('isReady'))]), 
					setReadinessStatusResponse);
			});
		$('#finishTurn')
			.button()
			.click(function(){
				sendQuery(makeQuery(['action', 'sid'], ['finishTurn', user().sid]), 
					finishTurnResponse);
			});
		$('#selectFriend')
			.button()
			.click(function(){
				sendQuery(makeQuery(['action', 'sid', 'friendId'], 
					['selectFriend', user().sid, $('#possibleFriends option:selected').val()]), 
					selectFriendResponse);				
			});
		$('#throwDice')
			.button()
			.click(function(){
				sendQuery(makeQuery(['action', 'sid'], ['throwDice', user().sid]), 
					throwDiceResponse);
			});
		$('#regionsTemplate').tmpl(Client.currGameState.map.regions,
		{
			opts: 
			{
				coords: function(regionId)
				{
					return '"' + game().map.regions[regionId - 1].x_race + ', ' + game().map.regions[regionId - 1].y_race + ', ' + '50"';
				}
			}
		}).appendTo('#map');
		$('#imgmap').maphilight();
		for (var i = 0; i < game().map.regions.length; ++i)
		{
			$('#region' + (i + 1)).click(function(j){
				return function(){
					$('#confirmInfo').empty();
					$('#confirmInfo').append(game().map.regions[j - 1].htmlRegionInfo());
					$('#confirm').dialog({
						height:250,
						title: 'region ' + j,
						modal: true,
						buttons: [
						{
							id: 'btnConquer',
							text: 'Conquer',
							click: function() {
								sendQuery(makeQuery(['action', 'sid', 'regionId'], 
									['conquer', user().sid, j]), conquerResponse);	
								$(this).dialog('close');
							}
						},
						{
							id: 'btnEnchant',
							text: 'Enchant',
							click: function() {
								sendQuery(makeQuery(['action', 'sid', 'regionId'], 
									['enchant', user().sid, j]), enchantResponse);
								$(this).dialog('close');
							}
						},
						{
							id: 'btnDragonAttack',
							text: 'Dragon attack',
							click: function() {
								sendQuery(makeQuery(['action', 'sid', 'regionId'], 
									['dragonAttack', user().sid, j]), dragonAttackResponse);
								$(this).dialog('close');
							}
						},
						{
							id: 'btnCancel',
							text: 'Cancel',
							click: function() {
								$(this).dialog('close');
							}
						}
						]});
					$('#confirm').dialog('open');
					if (!(canBeginConquer() && canConquer(game().map.regions[j - 1])))
						$('#btnConquer').hide();
					if (!(canBeginEnchant() && canEnchant(game().map.regions[j - 1])))
						$('#btnEnchant').hide();
					if (!(canBeginDragonAttack() && canDragonAttack(game().map.regions[j - 1])))
						$('#btnDragonAttack').hide();				
				}
			}(i + 1));
		}
	}
	
	$('#usersInCurGame').empty();
	$('#usersInCurGameTemplate').tmpl(Client.currGameState.players,
	{
		
		activePlayer: function()
		{
			return Client.currGameState.activePlayerIndex != undefined ? Client.currGameState.players[Client.currGameState.activePlayerIndex].id : 
				undefined;
		},
		currentUser: function()
		{
			return Client.currentUser.id
		}
	}).appendTo('#usersInCurGame');	
	
	$('#visibleTokenBadges').empty();
	$('#visibleTokenBadgesTemplate').tmpl(Client.currGameState.tokenBadges).appendTo('#visibleTokenBadges');

	$('#leaveGame')
		.button()
		.click(function(){
			sendQuery(makeQuery(['action', 'sid'], ['leaveGame', Client.currentUser.sid]), 
				leaveGameResponse);
		});
	$('#leaveGame').show();
	$('#imgdiv').empty();
	for (var i = 0; i < game().map.regions.length; ++i)
		game().map.regions[i].drawTokenBadge();
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
	{
		$('#finishTurn').show();
	}
}

Interface.prepareForSelectFriend = function()
{
	if (!canChooseFriend())
		return;
	var cnt = 0;
	for (var i = 0; i < game().players.length; ++i)
		if (selectFriend(game().players[i]))
		{
			$('#possibleFriends').append('<option value = ' + i + '>' + game().players[i].name + 
				'</option>');
			++cnt;
		}
	if (cnt)
	{
		$('#possibleFriends').show();
		$('#selectFriend').show();
	}
}

Interface.prepareForThrowDice = function()
{
	if (canThrowDice())
	{
		$('#throwDice').show();
	}
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
		
Interface.createGameTab = function(gameName)
{
	$('#gameListInfo').html('');
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

