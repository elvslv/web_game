Array.prototype.copy = function() {
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
}

toPolygon = function(array){
	var i, poly = [], curr = {};
	for (i = 0; i < array.length; i++) {
		poly.push(function(){
				return {
					x: array[i][0], y : array[i][1]
					}
				}());			
	}
	return poly;
};

getSvgPath = function(array){
	var i, res = 'M' + array[0].x + ',' + array[0].y;
	for (i = 1; i < array.length; i++) {
		res += 'L' + array[i].x + ',' + array[i].y; 
	}
	return res += 'Z';
};
	
