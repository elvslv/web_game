$(function() {
	Interface.updatePage();
	$('#tabs').tabs();
	$('#tabs').tabs('add', '#ui-tabs-0', 'About', 0);
	$('#ui-tabs-0').append("<div style = \"background: url(styles/images/bg.jpg) no-repeat; background-position: 40% center;\">"+
		"<table id = \"tmain\" height = \"100%\" width = \"100%\" style=\"ui-widget\">"+
			"<tr>"+
				"<td rowspan = 4 valign = \"top\">"+
					"<table id = \"tableGames\" width = \"400px\">"+
						"<tr>"+
							"<td>"+
								"<button id = \"getGameList\" style = \"display: none\">Refresh game list</button>"+
							"</td>"+
						"</tr>"+
						"<tr>"+
							"<td>"+
								"<p id = \"gameListInfo\"></p>"+
							"</td>"+
						"</tr>"+
						"<tr>"+
							"<td>"+
								"<ul id = \"gameList\">"+
								"</ul>"	+
							"</td>"+
						"</tr>"+
						"<tr>" +
							"<td>" +
								"<button id = \"createGame\" style = \"display:none\">Create new game</button>"+
							"</td>"+
						"</tr>"+
						"<tr>"+
							"<td>"+
								"<button id = \"createMap\"style = \"display:none\">Create new map</button>"+
							"</td>"+
						"</tr>"+
					"</table>"+
				"</td>"+
				"<td rowspan = 4 valign = \"top\">"+
					"<p style = \"margin-left: -130px\">Here must be info about the game</p>"+
				"</td>"+
				"<td valign = \"top\" align = \"right\">"+
					"<p id = \"userInfo\">You're not logged in, please login or register</p>"+
					"<div>"+
						"<button id = \"register\" style = \"display: none\">Register</button>"+
						"<button id = \"login\" style = \"display: none\">Login</button>"+
						"<button id = \"logout\" style = \"display:none\">Logout</button>"+
					"</div>"+
				"</td>"+
			"</tr>"+
			"<tr>"+
				"<td rowspan=3 valign = \"top\">"+
					"<table width = \"300px\" valign = \"top\" align = \"right\" style = \"margin-top: 0px; height: 100%\">"+
						"<tr>"+
							"<td colspan = 2>"+
								"<div id = \"chat\" class = \"ui-widget-content ui-corner-all\" style = "+
									"\"overflow-y: auto; height: 100%; max-height: 300px\">"+
								"</div>"+
							"</td>"+
						"</tr>"+
						"<tr>"+
							"<td colspan = 2>"+
								"<textarea id = \"messageBox\" class = \"ui-widget-content ui-corner-all\" style = "+
									"\"width: 100%; overflow-y: auto; margin-top:0px; height: 100%\"></textarea>"+
							"</td>"+
						"</tr>"+
						"<tr>"+
							"<td>"+
								"<button id = \"sendMessage\" style = \"display: none\">Send message</button>"+
							"</td>"+
							"<td align = \"right\">"+
								"<button id = \"refreshChat\" style = \"display: none\">Refresh chat</button>"+
							"</td>"+
						"</tr>"+
					"</table>"+
				"</td>"+
			"</tr>"+
		"</table>"+
	"</div>");
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
	});
	$('#createMap').show();
	$('#register').show();
	$('#login').show();
	$('#refreshChat').show();
	$('#getGameList').show();
	$('#tabs').show();
});
