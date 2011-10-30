var Client = {};

Client.currentUser = Object();

Client.gameList = [];

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

Client.uploaderParams = [
	{name: 'uploadThumbnail', maxSize: 500 * 1024}, 
	{name: 'uploadPicture', maxSize: 5 * 1024 * 1024}]