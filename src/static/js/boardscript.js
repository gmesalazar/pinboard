console.log("boardscript.js loaded")

/* Mouse hover effect (caption) */

function divHandlerHoverIn(e) {
	caption = document.getElementById('title');
	caption.style.background = 'white';
	captionDiv = document.getElementById('title');
	captionDiv.setAttribute('contenteditable', true);
}

function divHandlerHoverOut(e) {
	caption = document.getElementById('title');
	caption.style.background = '#ECD9DB';
}

/* Key press and Focus out handlers (caption) */

function divHandlerKeyPress(e) {
	
	var keycode = (e.keyCode ? e.keyCode : e.which);
	
	if (keycode == '13') {
		
		e.preventDefault();
		
		console.log("ENTER key pressed");
		
		$('#title').blur();
		
	}
	
	e.stopPropagation();
}

function divHandlerFocusOut(e) {
	var self = $(this);
	self.value = self.text();

	var privacy = $('input[name=privacy]').is(':checked');

	$.ajax('', {
		type : 'POST',
		data : {
			title : self.value,
			privacy : privacy,
			action: 'update'
		},
		success : function() {
			document.getElementById('pagename').innerText = self.value;
			console.log('Success!');
		},
		error : function() {
			console.log('Error at server:');
		}
	});
	
	e.stopPropagation();
}

/* Privacy checkbox handler */

function checkboxHandler(e) {
	var privacy = $('input[name=privacy]').is(':checked');

	var title = $('#title').text();

	$.ajax('', {
		type : 'POST',
		data : {
			title : title,
			privacy : privacy,
			action: 'update'
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

/* Registering handlers */

$(document).ready(function() {
	$('#title').hover(divHandlerHoverIn, divHandlerHoverOut);
	$('#title').keypress(divHandlerKeyPress);
	$('#title').focusout(divHandlerFocusOut);
	$('#privacy').click(checkboxHandler);
});