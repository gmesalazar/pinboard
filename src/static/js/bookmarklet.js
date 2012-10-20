console.log('loaded bookmarklet.js')

imgsRef = document.getElementsByTagName('img');

imgsArr = new Array()

for (i = 0; i < imgsRef.length; i++) {
	imgElem = document.createElement('img');
	imgElem.src = imgsRef[i].src;
	
	imgsArr.push(imgElem);
}

document.body.innerHTML = '';

document.body.style.margin = '8px';
document.body.style.background = '#D0D4D2';

document.body.appendChild(document.createElement('br'));

h1 = document.createElement('h1');
h1.innerText = 'Pinboard';

document.body.appendChild(h1);

hostName = 'csce242-gmesalazar.appspot.com';
//hostName = 'localhost:8080';
locationHost = 'http://' + hostName + '/pin/';

for (i = 0; i < imgsArr.length; i++) {
	
	div = document.createElement('div');
	div.style.display = 'table';
	div.style.position = 'relative';
	div.style.margin = 'auto';
	div.style.height = 'auto';
	div.style.width = 'auto';
	div.style.borderRadius = '4px';
	div.style.boxShadow = '0px 0px 6px #73000A';
	div.style.padding = '8px';
	
	imgsArr[i].style.display = 'block';
	imgsArr[i].style.marginLeft = 'auto';
	imgsArr[i].style.marginRight = 'auto';
	
	form = document.createElement('form');
	form.setAttribute('method', 'post');
	form.setAttribute('action', locationHost);
	
	label = document.createElement('label');
	label.innerText = 'Caption: ';
	label.style.float = 'left';
	label.style.width = '100px';
	
	urlBox = document.createElement('input');
	urlBox.setAttribute('type', 'hidden');
	urlBox.setAttribute('name', 'url');
	urlBox.setAttribute('value', imgsArr[i].src);
	
	captionBox = document.createElement('input');
	captionBox.setAttribute('type', 'text');
	captionBox.setAttribute('name', 'caption');
	captionBox.style.display = 'inline';
	captionBox.style.float = 'right';
	
	button = document.createElement('input');
	button.setAttribute('type', 'submit');
	button.setAttribute('name', 'submitButton');
	button.setAttribute('value', 'This one');
	
	button.style.float = 'right';
	
	form.appendChild(label);
	form.appendChild(urlBox);
	form.appendChild(captionBox);
	form.appendChild(document.createElement('br'));
	form.appendChild(document.createElement('br'));
	form.appendChild(button);
	
	div.appendChild(imgsArr[i]);
	div.appendChild(document.createElement('br'));
	div.appendChild(form);
	
	document.body.appendChild(div);
	document.body.appendChild(document.createElement('br'));
}
