console.log("loaded canvas.js")

var board = null;
var boardpinids = null;
var boardpins = null;
var allpins = null;
var imgs = null;
var lastlyMovedPin = null;
var lastlyClickedPin = null;
var anchors = null;


function Vector(x, y) {
	this.x = x;
	this.y = y;
	
	this.add = function(v2) {
		return new Vector(this.x + v2.x, this.y + v2.y);
	};
	
	this.subtract = function(v2) {
		return new Vector(this.x - v2.x, this.y - v2.y);
	};
} 

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

	for ( var i = 0; i < boardpins.length; i++) {

		var img = new Image();
		img.src = boardpins[i].imgUrl;
		
		img.id = boardpins[i].id;
		img.xCoord = board.xCoords[boardpins[i].id];
		img.yCoord = board.yCoords[boardpins[i].id];
		
		img.width = board.widths[boardpins[i].id];
		img.height = board.heights[boardpins[i].id];
		
		imgs.push(img);

		img.onload = function(pin, img, i) {
			return function() {
				if (img.xCoord == undefined || img.yCoord == undefined) {

					var xCoord = (i % 4) * 200 + (i % 4 + 1) * 10;
					var yCoord = Math.floor(i / 4) * 200
							+ (Math.floor(i / 4) + 1) * 26;

					img.xCoord = xCoord;
					img.yCoord = yCoord;

					ctx.drawImage(img, xCoord, yCoord, 200, 200);
					
					img.width = 200;
					img.height = 200;

				} else {
					ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
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
			ctx.drawImage(imgs[i], imgs[i].xCoord, imgs[i].yCoord, imgs[i].width, imgs[i].height);
		}
	}
}

function pointerIsInsidePin(mouseX, mouseY) {

	for ( var i = 0; i < imgs.length; i++) {
		
		if ((mouseX >= imgs[i].xCoord && mouseX <= imgs[i].xCoord + imgs[i].width)
				&& (mouseY >= imgs[i].yCoord && mouseY <= imgs[i].yCoord + imgs[i].height)) {

			return {
				img: imgs[i],
				op: 'move'
			};
		}
	}

	return null;
}

function pointerIsInsideAnchor(mouseX, mouseY) {
	
	for ( var i = 0; i < imgs.length; i++) {
		
		var dx = mouseX - anchors[0].x;
		var dy = mouseY - anchors[0].y;
			
		if (dx * dx + dy * dy < 64) {
			return  {
				op: 'resize',
				anchor: 0
			};
		}
		
		dx = mouseX - anchors[1].x;
		dy = mouseY - anchors[1].y;
		
		if (dx * dx + dy * dy < 64) {
			return  {
				op: 'resize',
				anchor: 1
			};
		}
		
		dx = mouseX - anchors[2].x;
		dy = mouseY - anchors[2].y;
		
		if (dx * dx + dy * dy < 64) {
			return  {
				op: 'resize',
				anchor: 2
			};
		}
		
		dx = mouseX - anchors[3].x;
		dy = mouseY - anchors[3].y;
		
		if (dx * dx + dy * dy < 64) {
			
				return  {
					op: 'resize',
					anchor: 3
				};
		}
	}
		
	return null;
}

function drawAnchor(x, y) {
	var bcanvas = document.getElementById('bcanvas');
	var ctx = bcanvas.getContext('2d');
	
	ctx.fillStyle = "rgb(105, 105, 105)";
	
	ctx.beginPath();
	ctx.arc(x, y, 8, 0, Math.PI * 2, true);
	ctx.fill();
	ctx.closePath();
}

function drawAnchors(img) {
	drawAnchor(img.xCoord, img.yCoord);
	drawAnchor(img.xCoord + img.width, img.yCoord);	
	drawAnchor(img.xCoord + img.width, img.yCoord + img.height);
	drawAnchor(img.xCoord, img.yCoord + img.height);
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

		if (lastlyMovedPin) {
	
			$.ajax('/board/' + board.id, {
				type : 'POST',
				data : {
					pinId : lastlyMovedPin.id,
					xCoord : lastlyMovedPin.xCoord,
					yCoord : lastlyMovedPin.yCoord,
					width : lastlyMovedPin.width,
					height : lastlyMovedPin.height,
					action : 'update',
				}
			});
		}

	});

	$('#bcanvas').mousedown(function(event) {
		
		var bcanvas = document.getElementById('bcanvas');
		var ctx = bcanvas.getContext('2d');

		var mouseX = event.pageX - this.offsetLeft;
		var mouseY = event.pageY - this.offsetTop;

		var result = pointerIsInsidePin(mouseX, mouseY);
		
		if (result) {
			
			img = result.img;
			
			if (lastlyClickedPin && lastlyClickedPin != img) {
				ctx.clearRect(lastlyClickedPin.xCoord - 8, lastlyClickedPin.yCoord - 8,
						lastlyClickedPin.width + 16, lastlyClickedPin.height + 16);
				ctx.drawImage(lastlyClickedPin, lastlyClickedPin.xCoord,
						lastlyClickedPin.yCoord, lastlyClickedPin.width, lastlyClickedPin.height);
				updateImgs();
			}
			
			drawAnchors(img);
			
			anchors = [
			           { x: img.xCoord, y: img.yCoord },
			           { x: img.xCoord + img.width, y: img.yCoord },
			           { x: img.xCoord + img.width, y: img.yCoord + img.height },
			           { x: img.xCoord, y: img.yCoord + img.height },
			];
			
			lastlyClickedPin = img;
			
		} else {
			ctx.clearRect(lastlyClickedPin.xCoord - 8, lastlyClickedPin.yCoord - 8,
					lastlyClickedPin.width + 16, lastlyClickedPin.height + 16);
			ctx.drawImage(lastlyClickedPin, lastlyClickedPin.xCoord,
					lastlyClickedPin.yCoord, lastlyClickedPin.width, lastlyClickedPin.height);
			updateImgs();
		}
		
		var result = pointerIsInsideAnchor(mouseX, mouseY);
		
		if (result) {
			
			$('#bcanvas').mousemove(function(e) {
				
				mouseX = e.pageX - this.offsetLeft;
				mouseY = e.pageY - this.offsetTop;
				
				anchors[result.anchor].x = mouseX;
				anchors[result.anchor].y = mouseY;
				
				console.log(result);
				
				switch (result.anchor) {
					case 0:
						
						img.width += img.xCoord - mouseX;
						img.height += img.yCoord - mouseY;
						
						img.xCoord = mouseX;
						img.yCoord = mouseY;
						
					    ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height );
					    ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
					    
					    drawAnchors(img);
						
					    lastlyClickedPin = img;
					    lastlyMovedPin = img;
					    
					    updateImgs();
					    
						break;
					case 1:
						
						img.width += mouseX - (img.width + img.xCoord);
						img.height += img.yCoord - mouseY;
						
						img.yCoord = mouseY;
						
					    ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height );
					    ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
					    
					    drawAnchors(img);
						
					    lastlyClickedPin = img;
					    lastlyMovedPin = img;
					    
					    updateImgs();
						
						break;
					case 2:
						
						img.width -= (img.width + img.xCoord) - mouseX;
						img.height += mouseY - (img.yCoord + img.height);
						
					    ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height );
					    ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
					    
					    drawAnchors(img);
						
					    lastlyClickedPin = img;
					    lastlyMovedPin = img;
					    
					    updateImgs();
						
						break;
					case 3:
						
						img.width += img.xCoord - mouseX;
						img.height += mouseY - (img.yCoord + img.height);
						
						img.xCoord = mouseX;
						
					    ctx.clearRect( 0, 0, ctx.canvas.width, ctx.canvas.height );
					    ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
					    
					    drawAnchors(img);
						
					    lastlyClickedPin = img;
					    lastlyMovedPin = img;
					    
					    updateImgs();
					    
						break;
				}
			});
			
		} else if (img) {

			var dx = mouseX - img.xCoord;
			var dy = mouseY - img.yCoord;

			$('#bcanvas').mousemove(function(e) {

				mouseX = e.pageX - this.offsetLeft;
				mouseY = e.pageY - this.offsetTop;

				ctx.clearRect(img.xCoord - 8, img.yCoord - 8, img.width + 16, img.height + 16);

				img.xCoord = mouseX - dx;
				img.yCoord = mouseY - dy;

				ctx.drawImage(img, img.xCoord, img.yCoord, img.width, img.height);
				
				lastlyMovedPin = img;
				
				updateImgs();

			});
		}
	});	
});