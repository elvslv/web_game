$(function() {
	updateGameList();
	updateChat();
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
			$('#registerLoginForm').prop('register', true);
			$('#registerLoginForm').dialog('option', 'title', 'Register');
			$('#username, #password').val('');
			$('#registerLoginForm').dialog('open');
		});
		
	$('#login')
		.button()
		.click(function() {
			$('#dialogInfo').text("Please enter username and password");
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
			sendQuery(makeQuery(['action'], ['getGameList']), getGameListResponse);
		});
	$('#getGameList').button(
	{
		icons: {primary:'ui-icon-refresh'},
		text: true
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
			sendQuery(makeQuery(['action', 'text', 'sid'], ['sendMessage', $('#messageBox').val(), 
				Client.currentUser.sid]), sendMessageResponse);
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
					})
				$('#mapPict' + Client.mapList[i].mapId).fancybox();
			}
			$('#browseMapsForm').dialog('open');
		});
	filenames = [];
	$('#createMap')
	.button()
	.click(function() {
		$('#uploadMap').dialog('open');
	});
	$('#createMap').show();
	$('#register').show();
	$('#login').show();
	$('#refreshChat').show();
	$('#getGameList').show();
	$('#submitThmb').click(function() {
		$(this.form).trigger('submit');
	}).trigger('click');
	$('#submitThmb')
	.submit(function(){
		var options = 
		{
			url: "upload_maps.php",
			dataType: "json", 
			success: function(result) 
			{
				data = $.parseJSON(result);
				if (data['result'] != 'ok')
				{
					alert(data['error']);
					return;
				}
				filenames.push(data['filename']);
			},
				
		};
		$("#thmbInput").ajaxForm(options);
		return false;
	})
});
