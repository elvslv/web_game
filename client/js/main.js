$(function() {
	$('#tabs').tabs();
	$('#tabs').tabs('add', '#ui-tabs-0', 'About', 0);
	var mainBlock = HtmlBlocks.mainTab();
	$('#ui-tabs-0').append(mainBlock);
	$('#chatMainTab').append(HtmlBlocks.chatBlock());
	Interface.updateChatBox();
	Interface.updatePage();
	for (var i = 0; i < Interface.dialogs.length; ++i)
	{
		dialog = $('#' + Interface.dialogs[i].name);
		dialog.dialog(Interface.defaultDialogOptions);
		dialog.dialog('option', 'title', Interface.dialogs[i].title);
		dialog.dialog('option', 'buttons', {
			'Ok': Interface.dialogs[i].ok, 
			'Cancel': function(){$(this).dialog('close')}
		});
		if (Interface.dialogs[i]['width'])
			dialog.dialog('option', 'width', Interface.dialogs[i].width);
		if (Interface.dialogs[i]['height'])
			dialog.dialog('option', 'height', Interface.dialogs[i].height);
	}
	$('#register')
		.button()
		.click(function() {
			$('#dialogInfo').text('Please enter username and password');
			$('#registerLoginOutput span').empty();
			$('#registerLoginOutput').hide();
			$('#registerLoginForm').prop('register', true);
			$('#registerLoginForm').dialog('option', 'title', 'Register');
			$('#username, #password').val('');
			$('#registerLoginForm').dialog('open');
		});
		
	$('#login')
		.button()
		.click(function() {
			$('#dialogInfo').text("Please enter username and password");
			$('#registerLoginOutput span').empty();
			$('#registerLoginOutput').hide();
			$('#registerLoginForm').prop('register', false);
			$('#registerLoginForm').dialog('option', 'title', 'Login');
			$('#username, #password').val('');
			$('#registerLoginForm').dialog('open');
		});
	$('#logout')
		.button()
		.click(function() {
			sendQuery(makeQuery(['action', 'sid'], ['logout', Client.currentUser.sid]), logoutResponse);
		});
	$('#aiCnt').spinner({min: 0, max: 5});
	$('#mapList').change(function(){
		$('#aiCnt').spinner('option', 'max', 
			Client.mapList[$('#mapList').prop('selectedIndex')].playersNum);
	});
	$('#createGame')
		.button()
		.click(function() {
			$('#createGameOutput span').empty();
			$('#createGameOutput').hide();
			updateMapList(true);
		});
	$('#browseMaps')
		.button()
		.click(function() {
			$('#browseMapsList').empty();
			$('#mapListTemplate').tmpl(Client.mapList).appendTo('#browseMapsList');
			for (var i = 0; i < Client.mapList.length; ++i)
			{
				$('#chooseMap' + Client.mapList[i].mapId).prop('mapId', Client.mapList[i].mapId);
				$('#chooseMap' + Client.mapList[i].mapId)
					.button()
					.click(function() {
						$('#map' + $(this).prop('mapId')).prop('selected', true);
						$('#browseMapsForm').dialog('close');
					});
				Client.mapList[i].graphicsThmb = Graphics.makePreview(createMap(Client.mapList[i],
					100 / Graphics.gameField.mapWidth, 100 /  Graphics.gameField.mapHeight),  
						'mapPict' + Client.mapList[i].mapId,
					100, 100);
				$('#mapPict' +  Client.mapList[i].mapId)
					.click(function(j){
						return function()
						{
							$('#mapPreview').empty();
							Client.mapList[j].graphics = Graphics.makePreview(createMap(Client.mapList[j]), 
								'mapPreview', Graphics.gameField.mapWidth, Graphics.gameField.mapHeight);
							$('#mapPreview').modal({zIndex: 3000});
							$('#mapPreview')
								.click(function(){$.modal.close()})
						}
					}(i));
			}
			$('#browseMapsForm').dialog('open');
		});
	filenames = [];
	$('#createMap')
		.button()
		.click(function() {
			$('#uploadMapOutput span').empty();
			$('#uploadMapOutput').hide();
			$('#uploadMap').dialog('open');
		});
	$('#loadGame').button().click(function(){
		$('#loadGameForm').dialog('open');
	});
	$('#createMap').show();
	$('#register').show();
	$('#login').show();
	$('#refreshChat').show();
	$('#tabs').show();
	//sendQuery({'action': 'login', 'username': 'user', 'password': '123456'},
	//		loginResponse, false, true);
});
