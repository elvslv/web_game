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
	"id" : 0
};


Client.newGame = function(id) {
	var playersNum = 1,
		state = 'waiting';
	return {
		"gameName" : Client.currGameState.name,
		"gameId"   : id,
		"state" : state,
		"turn"  : 0,
		"playersNum" : playersNum,
		"gameDescr" : Client.currGameState.descr,
		"mapId" : Client.currGameState.mapId
	};
};

Client.states = [
	'start',
	'waiting',
	'??',
	'finished',
];
	
Client.gameProperties = [
	"gameId", "gameName", "gameDescr", 
	"mapId", "playersNum", "activePlayer", 
	"state", "turn", "players"
];


