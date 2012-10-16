console.log("script.js loaded")

function captionHandlerHoverIn(e) {
	caption = document.getElementById('caption');
	caption.style.background = 'white';
}

function captionHandlerHoverOut(e) {
	caption = document.getElementById('caption');
	caption.style.background = '#ECD9DB';
}

function captionHandlerKeyPress(e) {
	
	var keycode = (e.keyCode ? e.keyCode : e.which);

	if (keycode == '13') {

		e.preventDefault();
		
		console.log("ENTER key pressed");
		
		$('#caption').blur();
	}
	
	e.stopPropagation();
}

function captionHandlerFocusOut(e) {
	var self = $(this);
	self.value = self.text();

	var privacy = $('input[name=privacy]').is(':checked');

	$.ajax('', {
		type : 'POST',
		data : {
			caption : self.value,
			privacy : privacy
		},
		success : function() {
			document.getElementById('pagename').innerText = '– ' + self.value;
			console.log('Success!');
		},
		error : function() {
			console.log('Error at server:');
		}
	});
	
	e.stopPropagation();
}

function checkboxHandler(e) {
	var privacy = $('input[name=privacy]').is(':checked');

	var caption = $('#caption').text();

	$.ajax('', {
		type : 'POST',
		data : {
			caption : caption,
			privacy : privacy
		},
		success : function() {
			console.log('Success!');
		},
		error : function() {
			console.log('Error at server:');
		}
	});

	e.stopPropagation();
}

$(document).ready(function() {
	$('#caption').hover(captionHandlerHoverIn, captionHandlerHoverOut);
	$('#caption').keypress(captionHandlerKeyPress);
	$('#caption').focusout(captionHandlerFocusOut);
	$('#privacy').click(checkboxHandler);
})