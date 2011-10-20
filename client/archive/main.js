$(function() {
		sendQuery('{"action": "getGameList"}', getGameListResponse);
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
						mapId = $('#mapId');
					responseGame = defaultResponseGame;
					responseGame['gameName'] = gameName.val();
					responseGame['gameDescr'] = gameDescription.val();
					responseGame['mapId'] = mapId.val();
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
				$('#registerLoginForm').dialog('open');
			});
			
		$('#login')
			.button()
			.click(function() {
				$('#dialogInfo').text("Please enter username and password");
				$('#registerLoginForm').prop('register', false);
				$('#registerLoginForm').prop('login', true);
				$('#registerLoginForm').dialog('option', 'title', 'Login');
				$('#registerLoginForm').dialog('open');
			});
		$('#logout')
			.button()
			.click(function() {
				query = '{"action": "logout", "sid": ' + sid +'}';
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
	});