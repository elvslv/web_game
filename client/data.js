var Client = {};

Client.currentUser = {};

Client.gameList = [];
Client.newUser = function(name, id) {
	return {
		"username" : name,
		"userId" : id
	};
};

Client.currGameState = {
	"name" : '',
	"descr" : '',
	"mapId" : 0,
	"id" : 0,
	"state" : 0,
};


Client.states = [
	'start',
	'waiting',
	'??',
	'finished',
];
	
Client.gameProperties = [
	"gameName", "gameDescr", "mapId", "activePlayer", "state", "turn", 
	"turnsNum", "maxPlayersNum", "players"
];

Client.playerProperties = ["username", "isReady", "inGame"];

