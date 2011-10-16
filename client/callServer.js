function sendQuery(query, callback)
{
	$.ajax({
		type: "POST",
		url: "http://localhost/small_worlds/",
		data: query,
		success: function(result){
			data = $.parseJSON(result);
			if (!data['result'])
			{
				alert("Unknown server response: " + data);
				return;
			}
			callback(data);
		}
	});
}