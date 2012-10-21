console.log("boardedscript.js loaded")

var thisboard = null;
var boardpins = null;
var allpins = null;
var remainpins = null;

function setThisBoard(data) {
	thisboard = data;
	boardpins = thisboard.pins;
}

function setAllPins(data) {
	allpins = data;
	remainpins = allpins.slice();
	
	for ( var i = 0; i < boardpins.length; i++) {
		for ( var j = 0; j < remainpins.length; j++) {
			if (remainpins[j].id == boardpins[i]) {
				remainpins.splice(j, 1);
			}
		}
	}
}

function pinsIdsToPins() {
	// TODO: improve this
	var pins = new Array();
	for ( var i = 0; i < boardpins.length; i++) {
		for ( var j = 0; j < allpins.length; j++) {
			if (allpins[j].id == boardpins[i]) {
				pins.push(allpins[j]);
			}
		}
	}

	return pins;
}

function addEvent(event) {

	event.preventDefault();

	var pinid = (this.id).split("_")[1];

	var pin = null;
	var index = null;

	for ( var i = 0; i < remainpins.length; i++) {
		if (remainpins[i].id == pinid) {
			index = i;
			pin = remainpins[i];
			remainpins.splice(i, 1);
			boardpins.push(pin.id);
			showAllPins();
			showBoardPins();
			break;
		}
	}

	$.ajax('', {
		type : 'POST',
		data : {
			addpin : pinid,
			action : 'update',
		},
		error : function() {
			remainpins.splice(index, 0, pin);
			boardpins.splice(boardpins.indexOf(pin.id), 1);
			showAllPins();
			showBoardPins();
			alert("The pin couldn't be added to the board, try again.");
		}
	});

	event.stopPropagation();
}

function remEvent(event) {

	event.preventDefault();

	var pinid = (this.id).split("_")[1];

	var pin = null;
	var index = null;

	var addedpins = pinsIdsToPins();

	for ( var i = 0; i < boardpins.length; i++) {
		if (boardpins[i] == pinid) {
			index = i;
			pin = addedpins[i];
			boardpins.splice(i, 1);
			remainpins.push(pin);
			updatePage();
			break;
		}
	}

	$.ajax('', {
		type : 'POST',
		data : {
			delpin : pinid,
			action : 'update',
		},
		error : function() {
			boardpins.splice(index, 0, pin.id);
			remainpins.splice(remainpins.indexOf(pin), 1);
			updatePage();
			alert("The pin couldn't be removed to the board, try again.");
		}
	});

	event.stopPropagation();
}

function showAllPins() {

	boxDIV = document.getElementById('allpins');
	boxDIV.innerHTML = "";

	for ( var i = 0; i < remainpins.length; i++) {

		p = document.createElement('p');

		a = document.createElement('a');
		a.setAttribute('class', 'thumbs');

		img = document.createElement('img');
		img.setAttribute('width', '200');
		img.setAttribute('align', 'top');
		img.setAttribute('src', remainpins[i].imgUrl);

		a.appendChild(img);
		p.appendChild(a);

		infoDIV = document.createElement('div');
		infoDIV.setAttribute('class', 'centralized');

		captionP = document.createElement('p');
		captionP.innerText = remainpins[i].caption;

		infoDIV.appendChild(captionP);

		p.appendChild(infoDIV);

		pinDIV = document.createElement('div');
		pinDIV.setAttribute('class', 'box');

		pinDIV.appendChild(p);

		buttom = document.createElement('input');
		buttom.setAttribute('type', 'submit');
		buttom.setAttribute('value', 'Add');

		form = document.createElement('form');
		form.setAttribute('id', 'addform_' + remainpins[i].id);

		form.appendChild(buttom);

		pinDIV.appendChild(form);

		boxDIV.appendChild(pinDIV);
		boxDIV.appendChild(document.createElement('br'));

		$('#addform_' + remainpins[i].id).submit(addEvent);
	}
}

function showBoardPins() {

	boxDIV = document.getElementById('boardpins');
	boxDIV.innerHTML = "";

	var pins = pinsIdsToPins();

	for ( var i = 0; i < pins.length; i++) {

		p = document.createElement('p');

		a = document.createElement('a');
		a.setAttribute('class', 'thumbs');
		a.setAttribute('href', '/pin/' + pins[i].id);

		img = document.createElement('img');
		img.setAttribute('width', '200');
		img.setAttribute('align', 'top');
		img.setAttribute('src', pins[i].imgUrl);

		a.appendChild(img);
		p.appendChild(a);

		infoDIV = document.createElement('div');
		infoDIV.setAttribute('class', 'centralized');

		captionP = document.createElement('p');
		captionP.innerText = pins[i].caption;

		infoDIV.appendChild(captionP);

		p.appendChild(infoDIV);

		pinDIV = document.createElement('div');
		pinDIV.setAttribute('class', 'box');

		pinDIV.appendChild(p);
		
		boxDIV.appendChild(pinDIV);
		boxDIV.appendChild(document.createElement('br'));

		if (document.getElementById('editable') != null) {
			buttom = document.createElement('input');
			buttom.setAttribute('type', 'submit');
			buttom.setAttribute('value', 'Remove');
	
			form = document.createElement('form');
			form.setAttribute('id', 'remform_' + pins[i].id);
	
			form.appendChild(buttom);
	
			pinDIV.appendChild(form);
			
			$('#remform_' + pins[i].id).submit(remEvent);
		}
		
	}
}

function updatePage() {
	if (document.getElementById('editable') != null) {
		showAllPins();
	}
	showBoardPins();
}

$(document).ready(function() {

	$.ajax('', {
		type : 'GET',
		data : {
			fmt : 'json'
		}, success : setThisBoard
		
	}).done(function() {
		
		$.ajax('/pin', {
			type : 'GET',
			data : {
				fmt : 'json'
			}, success : setAllPins
			
		}).done(updatePage);	
	});
});