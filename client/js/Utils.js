Array.prototype.copy = function() 
{
		return [].concat(this);
};
		
includes = function(data, array)
{
	for (var i = 0; i < array.length; ++i)
		if (array[i] === data)
			return true;
	return false;
};

parseArray = function(array){
	if (!array || array == 'None') return false;
	return JSON.parse('{ "name" : ' + array + '}').name;
};

//converts [[1, 2], ...,[...]] to [{x : 1, y : 2}, ..., {...}]  

toPolygon = function(array){
	var i, poly = [];
	for (i = 0; i < array.length; i++) {
		poly.push(function(){
				return {
					x: array[i][0], y : array[i][1]
					}
				}());			
	}
	return poly;
};

//converts  [{x : 1, y : 2}, {x : 3, y : 4}, ..., {...}]   to   "M 1, 2L3, 4 ... Z"
getSvgPath = function(array){
	var i, res = 'M' + array[0].x + ',' + array[0].y;
	for (i = 1; i < array.length; i++) {
		res += 'L' + array[i].x + ',' + array[i].y; 
	}
	return res += 'Z';
};
//converts {"1" : 31, "2" : 54, ...} to [{"regionId" : 1", "tokensNum" : "999"}, ..., {...}]
convertRedeploymentRequest = function(array, type){
	var i, result = [];
	for (i in array) {
		if (!array[i] || typeof(array[i]) !== 'number') continue
			result.push(function(){
				return (type === Client.REDEPLOYMENT_CODE) ? 
					{
						regionId: parseInt(i), tokensNum : array[i]
					} :
					type ===  Client.ENCAMPMENTS_CODE ? 
					{
						regionId: parseInt(i), encampmentsNum : array[i]
					} :
					{
						regionId: parseInt(i)
					}		
			}());
		}
	console.log(result);
	return type === Client.FORTRESS_CODE ? result[0] : result;
};


