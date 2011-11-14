var Client = {};

Client.RACE_CODE = 15;
Client.SPECIAL_POWER_CODE = 16;


Client.currentUser = Object();

Client.currGameState = undefined;
	
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

user = function()
{
	return Client.currentUser;
}

game = function()
{
	return Client.currGameState;
}
