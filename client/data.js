var sid = undefined;
var username = undefined;
var gameId = undefined;
var userId = undefined;
var mapId = undefined;
var gamesList = undefined;
var gameFields = ['gameId', 'gameName', 'gameDescr', 'mapId', 'playersNum', 'activePlayer', 'state', 'turn', 'players']
var gameFieldDescriptions = ['Game id', 'Game name', 'Game description', 'Map id', 'Number of players', 'Active player', 
'State', 'Turn', 'Players list']
var responseGameId = undefined;
var defaultResponseGame = {'playersNum': 1, 'activePlayer': 0, 'state': 1, 'turn': 0}
var responseGame = undefined;