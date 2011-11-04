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
	
