console.log("script.js loaded")

function handlerIn(e) {
	caption = document.getElementById('caption');
	caption.style.background = 'white';
}

function handlerOut(e) {
	caption = document.getElementById('caption');
	caption.style.background = '#ECD9DB';
}

function handlerKeyPress(e) {
	var keycode = (e.keyCode ? e.keyCode : e.which);

	if (keycode == '13') {
		console.log("ENTER key pressed");

		var self = $(this);
		self.value = self.val();

		var privacy = $('input[name=privacy]').is(':checked');

		$('#captionDIV').replaceWith('<div id="caption">' + self.value + '</div>');

		$.ajax('', {
			type : 'POST',
			data : {
				caption : self.value,
				privacy : privacy
			},
			success : function() {
				console.log('Success!');
			},
			error : function() {
				console.log('Error at server:');
			}
		}).done(function() {
			location.reload();
		});

		e.stopPropagation();

	}
}

function handlerClick(e) {
	console.log('User clicked');

	var self = $(this);
	self.value = self.text();

	$('#caption').replaceWith(
			'<div id="captionDIV"><input id="captionTB" type="text" value="'
					+ self.value + '" name="caption"/><br/><br/></div>');

	$('#captionTB').keypress(handlerKeyPress);

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
	}).done(function() {
		location.reload();
	});

	e.stopPropagation();
}

$(document).ready(function() {
	$('#caption').hover(handlerIn, handlerOut);
	$('#caption').on("click", handlerClick);
	$('input[name=privacy]').on("click", checkboxHandler);
})