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
			'Cancel': function(){$(this).dialog('close')
		}});
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
	$('#getGameList')
		.button()
		.click(function() {
			sendQuery(makeQuery(['action'], ['getGameList']), getGameListResponse, true);
		});
	$('#getGameList').button(
	{
		icons: {primary:'ui-icon-refresh'},
		text: true
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
				Client.mapList[i].graphics = new RaphaelGraphics(createMap(Client.mapList[i], 
					100 / defaultWidth, 100 / defaultHeight), 'mapPict' + Client.mapList[i].mapId,
					100, 100)
				Client.mapList[i].graphics.drawMapThmb();
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
	$('#getGameList').show();
	$('#tabs').show();
});
