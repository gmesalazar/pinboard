console.log("loaded canvas.js")

var board = null;
var boardpinids = null;
var boardpins = null;
var allpins = null;
var imgs = null;
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
	
	imgs = new Array();

	for (var i = 0; i < boardpins.length; i++) {

		var img = new Image();
		img.src = boardpins[i].imgUrl;
		
		img.id = boardpins[i].id;
		img.xCoord = board.xCoords[boardpins[i].id];
		img.yCoord = board.yCoords[boardpins[i].id];
		
		imgs.push(img);
		
		img.onload = function(pin, img, i) {
			return function() {
				if (img.xCoord == undefined || img.yCoord == undefined) {
					
					var xCoord = (i % 4) * 200 + (i % 4 + 1) * 10.5;
					var yCoord = Math.floor(i / 4) * 200 + (Math.floor(i / 4) + 1) * 26.5;
					
					img.xCoord = xCoord;
					img.yCoord = yCoord;
					
					ctx.drawImage(img, xCoord, yCoord, 200, 200);
					
				} else {
					ctx.drawImage(img, img.xCoord, img.yCoord, 200, 200);
				}
			}
		}(boardpins[i], img, i);
	}
}

function updateImgs() {
	
	var bcanvas = document.getElementById('bcanvas');
	var ctx = bcanvas.getContext('2d');
	
	for (i = 0; i < imgs.length; i++) {
		if (imgs[i] != lastlyMovedPin) {
			ctx.drawImage(imgs[i], imgs[i].xCoord, imgs[i].yCoord, 200, 200);
		}
	}
}

function pointerIsInsideObject(mouseX, mouseY) {
	
	for (var i = 0; i < imgs.length; i++) {
		if ((mouseX >= imgs[i].xCoord && mouseX <= imgs[i].xCoord + 200)
				&& (mouseY >= imgs[i].yCoord && mouseY <= imgs[i].yCoord + 200)) {
			return imgs[i];
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
		
		$.ajax('/board/' + board.id, {
			type : 'POST',
			data : {
				pinId : lastlyMovedPin.id,
				xCoord : lastlyMovedPin.xCoord,
				yCoord : lastlyMovedPin.yCoord,
				action : 'update',
			}
		});
	});

	$('#bcanvas').mousedown(function(event) {
		
		var bcanvas = document.getElementById('bcanvas');
		var ctx = bcanvas.getContext('2d');
		
		var mouseX = event.pageX - this.offsetLeft;
		var mouseY = event.pageY - this.offsetTop;
		
		var img = pointerIsInsideObject(mouseX, mouseY);
		
		if (img != null) {
			 $('#bcanvas').mousemove(function(e) {
				 mouseX = e.pageX - this.offsetLeft;
				 mouseY = e.pageY - this.offsetTop;
				 
				 ctx.clearRect(img.xCoord, img.yCoord, 200, 200);
				 img.xCoord = mouseX;
				 img.yCoord = mouseY;
				 
				 updateImgs();
				 
				 ctx.drawImage(img, mouseX, mouseY, 200, 200);
				 
				 lastlyMovedPin = img;
			 });
		}
	});
	
});