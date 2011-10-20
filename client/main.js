$(function() {
	updateGameList();
	updateChat();
	$("#registerLoginForm").dialog(
	{
		autoOpen: false,
		height: 300,
		width: 350,
		modal: true,
		buttons: {
			Ok: function() 
			{
				var name = $('#username'),
					password = $('#password'),
					query = '{"action": ' + ($('#registerLoginForm').prop('register') ? '"register"' : '"login"') + ', "username":"' + name.val() + '", "password": "' + password.val() + '"}';
				sendQuery(query, function(data){
					if ($('#registerLoginForm').prop('register'))
						registerResponse(data);
					else
						loginResponse(data);
				});
			},
			Cancel: function() 
			{
				$(this).dialog('close');
			}
		}
	});
	$("#createGameForm").dialog(
	{
		autoOpen: false,
		height: 300,
		width: 350,
		modal: true,
		title: 'Create new game',
		buttons: {
			Ok: function() 
			{
				var gameName = $('#gameName'),
					gameDescription = $('#gameDescription'),
					mapId = Client.mapList[$('#mapList').prop('selectedIndex')].mapId,
					sid = Client.currentUser.sid;
				Client.currGameState.name = gameName.val();
				Client.currGameState.descr  = gameDescription.val();
				Client.currGameState.mapId = mapId
				Client.currGameState.state = 1;
				query = '{"action": "createGame", "sid": ' + sid + ', "gameName": "' + 
					gameName.val() + '", "gameDescr": "' + gameDescription.val() + '", "mapId": ' +
					mapId + '}';
				sendQuery(query, createGameResponse);
			},
			Cancel: function() 
			{
				$(this).dialog('close');
			}
		}
	});
	$("#browseMapsForm").dialog(
	{
		autoOpen: false,
		height: 300,
		width: 350,
		modal: true,
		title: 'Maps',
		buttons: {
			Cancel: function() 
			{
				$(this).dialog('close');
			}
		}
	});
	$('#register')
		.button()
		.click(function() {
			$('#dialogInfo').text('Please enter username and password');
			$('#registerLoginForm').prop('register', true);
			$('#registerLoginForm').prop('login', false);
			$('#registerLoginForm').dialog('option', 'title', 'Register');
			$('#username').val('');
			$('#password').val('');
			$('#registerLoginForm').dialog('open');
		});
		
	$('#login')
		.button()
		.click(function() {
			$('#dialogInfo').text("Please enter username and password");
			$('#registerLoginForm').prop('register', false);
			$('#registerLoginForm').prop('login', true);
			$('#registerLoginForm').dialog('option', 'title', 'Login');
			$('#username').val('');
			$('#password').val('');
			$('#registerLoginForm').dialog('open');
		});
	$('#logout')
		.button()
		.click(function() {
			query = '{"action": "logout", "sid": ' + Client.currentUser.sid +'}';
			sendQuery(query, logoutResponse);
		});
	$('#getGameList')
		.button()
		.click(function() {
			query = '{"action": "getGameList"}';
			sendQuery(query, getGameListResponse);
		});
	$('#getGameList').button(
	{
		icons: {primary:'ui-icon-refresh'},
		text: false
	});
	$('#createGame')
		.button()
		.click(function() {
			updateMapList(true);
		});
	$('#refreshChat')
		.button()
		.click(function() {
			updateChat();
		});
	$('#sendMessage')
		.button()
		.click(function() {
			sendQuery('{"action": "sendMessage", "text": "' + $('#messageBox').val() + 
				'", "sid": ' + Client.currentUser.sid+'}', sendMessageResponse);
		});
	$('#browseMaps')
		.button()
		.click(function() {
			$('#mapListTemplate').tmpl(Client.mapList).appendTo('#browseMapsList');
			for (var i = 0; i < Client.mapList.length; ++i)
			{
				$('#chooseMap' + Client.mapList[i].mapId).prop('mapId', Client.mapList[i].mapId);
				$('#chooseMap' + Client.mapList[i].mapId)
					.button()
					.click(function() {
						$('#map' + $(this).prop('mapId')).prop('selected', true);
						$('#browseMapsForm').dialog('close');
					})
				$('#mapPict' + Client.mapList[i].mapId).fancybox();
			}
			$('#browseMapsForm').dialog('open');
		});
		
});