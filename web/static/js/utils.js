
function mobileWidthCheck() {
	//Checks whether the window is less then 900 pixels
	if (window.innerWidth < 900) {
		updateProperty('main','width', (window.innerWidth - 20) + 'px')
	} else {
		updateProperty('main','width','70%')
	}
}

function updateProperty(elementID, property, value) {
	if(document.getElementById(elementID)){
		document.getElementById(elementID).style.setProperty(property, value);
	}
}

function capitalize(string){
	return string.charAt(0).toUpperCase() + string.slice(1);
}
