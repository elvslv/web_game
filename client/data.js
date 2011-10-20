var Client = {};

Client.currentUser = {};

Client.gameList = [];
Client.newUser = function(name, id, sid) {
	return {
		"username" : name,
		"userId" : id,
		"sid" : sid,
	};
};

Client.lastGame = {
	"name" : '',
	"descr" : '',
	"mapId" : 0,
	"id" : 0,
	"state" : 0,
};


Client.newGame = function(id) {
	return {
		"gameName" : Client.lastGame.name,
		"gameId"   : id,
		"state" : 'waiting',
		"turn"  : 0,
		"playersNum" : 1,
		"gameDescr" : Client.lastGame.descr,
		"mapId" : Client.lastGame.mapId
	};
};

Client.states = [
	'start',
	'waiting',
	'processing',
	'finished',
];
	
Client.gameProperties = [
	"gameName", "gameDescr", "mapId", "activePlayer", "state", "turn", 
	"turnsNum", "maxPlayersNum", "players"
];

Client.playerProperties = ["username", "isReady", "inGame"];

Client.messages = [];

Client.mapList = [];
