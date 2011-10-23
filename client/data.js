var Client = {};

Client.currentUser = {};

Client.gameList = [];
Client.newUser = function(name, id) {
	return {
		"username" : name,
		"userId" : id
	};
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

Client.messages = [];

Client.mapList = [];

Client.uploaderParams = [
	{name: 'uploadThumbnail', maxSize: 500 * 1024}, 
	{name: 'uploadPicture', maxSize: 5 * 1024 * 1024}]
