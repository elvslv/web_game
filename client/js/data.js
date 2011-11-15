var Client = {};

Client.REDEPLOYMENT_CODE = -1;
Client.HERO_CODE = -2;
Client.FORTRESS_CODE = -3;
Client.ENCAMPMENTS_CODE = -4;


Client.currentUser = Object();

Client.currGameState = undefined;
	
Client.gameList = [];

	
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
