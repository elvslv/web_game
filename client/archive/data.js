var Client = {}

Client.currentUser = {}
Client.newUser = function(name, id) {
	return {
		"name" : name,
		"id" : id
	};
}

	
Client.gameProperties = [
	'gameId', 'gameName', 'gameDescr', 
	'mapId', 'playersNum', 'activePlayer', 
	'state', 'turn', 'players'
];

Client.gameList = [];
Client.defaultResponseGame = {
	'playersNum': 1, 
	'activePlayer': 0, 
	'state': 1, 
	'turn': 0
};


//var gameFieldDescriptions = ['Game id', 'Game name', 'Game description', 'Map id', 'Number of players', 'Active player', 
//'State', 'Turn', 'Players list']
var responseGameId = undefined;
var responseGame = undefined;
