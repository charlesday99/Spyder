
function mobileWidthCheck() {
	//Checks whether the window is less then 900 pixels
	if (window.innerWidth < 900) {
		updateProperty('main','width', (window.innerWidth - BAR_WIDTH) + 'px')
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

function submitText(text_type) {
	input_textbox = document.getElementById('input_text');
	if (text_type == "alert") {
		fetch("/ink/text?style=alert&text=" + input_textbox.value);
	} else if (text_type == "banner") {
		fetch("/ink/text?style=banner&text=" + input_textbox.value);
	} else {
		fetch("/ink/text?style=splash&text=" + input_textbox.value);
	}
	input_textbox.value = "";
}
