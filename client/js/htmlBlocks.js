HtmlBlocks = {};

HtmlBlocks.mainTab = function()
{ 
	return "<div style = \"background: url(css/images/bg.jpg) no-repeat; background-position: 40% center;\">"+
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
					"<td rowspan=3 valign = \"top\" id = \"chatMainTab\" style = \"width: 300px;\">"+	
					"</td>"+
				"</tr>"+
			"</table>"+
		"</div>";
}

HtmlBlocks.chatBlock = function()
{
	return "<table width = \"100%\" valign = \"top\" align = \"right\" style = \"margin-top: 0px; height: 100%\">"+
			"<tr>"+
				"<td colspan = 2>"+
					"<div id = \"chat\" class = \"ui-widget-content ui-corner-all chat\" >"+
					"</div>"+
				"</td>"+
			"</tr>"+
			"<tr>"+
				"<td colspan = 2>"+
					"<textarea id = \"messageBox\" class = \"ui-widget-content ui-corner-all messageBox\"" +
					"onKeyUp = \"onMessageChange();\"></textarea>"+
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
		"</table>";
}

HtmlBlocks.gameTab = function()
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
			'<tr>' +
				'<td>' +
					'<button id = "changeRedeployStatus" style = "display: none">Start redeploy</button>' +
				'</td>' +
				'<td>' +
					'<button id = "redeploy" style = "display: none" align = "left">redeploy</button>' +
				'</td>' +
			'</tr>' +
			'<tr>' +
				'<td colspan = "2">' +
					'<button id = "defend" style = "display: none">Defend</button>' +
				'</td>' +
			'</tr>' +
			'<tr>' +
				'<td colspan = "2" id = "chatGameTab" style = "width: 100%">' +
				'</td>' +
			'</tr>' +
		'</table>';
}

