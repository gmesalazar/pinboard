console.log("loaded canvas.js")

var board = null;
var boardpinids = null;
var boardpins = null;
var allpins = null;

var lastlyMovedPin = null;

function setAllPins(data) {

	allpins = data;
}

function setBoard(data) {

	board = data;
	boardpinids = board.pins;

	boardpins = new Array();

	for ( var i = 0; i < boardpinids.length; i++) {
		for ( var j = 0; j < allpins.length; j++) {
			if (boardpinids[i] == allpins[j].id) {
				boardpins.push(allpins[j]);
			}
		}
	}

}

function addImages() {

	var bcanvas = document.getElementById('bcanvas');
	var ctx = bcanvas.getContext('2d');

	for (var i = 0; i < boardpins.length; i++) {

		var img = new Image();
		img.src = boardpins[i].imgUrl;

		img.onload = function(pin, img, i) {
			return function() {
				if (pin.xCoord == -1 && pin.yCoord == -1) {
					
					var xCoord = (i % 4) * 200 + (i % 4 + 1) * 11;
					var yCoord = Math.floor(i / 4) * 200 + (Math.floor(i / 4) + 1) * 25;
					
					ctx.drawImage(img, xCoord, yCoord, 200, 200);
					
					pin.xCoord = xCoord;
					pin.yCoord = yCoord;
					
				} else {
					ctx.drawImage(img, pin.xCoord, pin.yCoord, 200, 200);
				}
			}
		}(boardpins[i], img, i);
	}
}

function pointerIsInsideObject(mouseX, mouseY) {
	
	for (var i = 0; i < boardpins.length; i++) {
		if ((mouseX >= boardpins[i].xCoord && mouseX <= boardpins[i].xCoord + 200)
				&& (mouseY >= boardpins[i].yCoord && mouseY <= boardpins[i].yCoord + 200)) {
			return boardpins[i];
		}
	}
	
	return null;
}

$(document).ready(function() {

	var boardid = (location.pathname).split("/")[2];

	$.ajax('/pin', {
		type : 'GET',
		data : {
			fmt : 'json'
		},
		success : setAllPins

	}).done(function() {

		$.ajax('/board/' + boardid, {
			type : 'GET',
			data : {
				fmt : 'json'
			},
			success : setBoard

		}).done(addImages);
	});

	$('#bcanvas').mouseup(function(event) {
		$('#bcanvas').unbind('mousemove');
		
		$.ajax('/pin/' + lastlyMovedPin.id, {
			type : 'POST',
			data : {
				xCoord : lastlyMovedPin.xCoord,
				yCoord : lastlyMovedPin.yCoord,
				action : 'update',
			}
		});
	});

	$('#bcanvas').mousedown(function(event) {
		
		var bcanvas = document.getElementById('bcanvas');
		var ctx = bcanvas.getContext('2d');
		
		ctx.globalCompositeOperation = 'destination-over';
		
		var mouseX = event.pageX - this.offsetLeft;
		var mouseY = event.pageY - this.offsetTop;
		
		var pin = pointerIsInsideObject(mouseX, mouseY);
		console.log(pin);
		if (pin != null) {
			 $('#bcanvas').mousemove(function(e) {
				 mouseX = e.pageX - this.offsetLeft;
				 mouseY = e.pageY - this.offsetTop;
				 var img = new Image();
				 img.src = pin.imgUrl;
				 img.onload = function() {
					 ctx.clearRect(pin.xCoord, pin.yCoord, 200, 200);
					 pin.xCoord = mouseX;
					 pin.yCoord = mouseY;
					 ctx.drawImage(img, mouseX, mouseY, 200, 200);
					 addImages();
				 }
			 });
			 lastlyMovedPin = pin;
		}
	});
	
});