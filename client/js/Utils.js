Array.prototype.copy =
	function() {
		return [].concat(this);
	};
includes = function(data, array)
{
	for (var i = 0; i < array.length; ++i)
		if (array[i] == data)
			return true;
	return false;
}
