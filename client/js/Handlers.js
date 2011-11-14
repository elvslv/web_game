onMessageChange = function()
{
	if (Client.currentUser.id && $('#messageBox').val().length > 0)
		$('#sendMessage').show();
	else
		$('#sendMessage').hide();
}
