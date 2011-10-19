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
					mapId = $('#mapId'),
					sid = Client.currentUser.sid;
				Client.currGameState.name = gameName.val();
				Client.currGameState.descr  = gameDescription.val();
				Client.currGameState.mapId = mapId.val();
				Client.currGameState.state = 1;
				query = '{"action": "createGame", "sid": ' + sid + ', "gameName": "' + gameName.val() + '", "gameDescr": "' + gameDescription.val() + '", "mapId": ' + mapId.val() + '}';
				sendQuery(query, createGameResponse);
			},
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
			$('#createGameForm').dialog('open');
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
});