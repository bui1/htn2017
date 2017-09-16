var switchbutton = document.querySelector("#need");
var titleswitch = document.querySelector("#switchtext")

switchbutton.addEventListener("click",function(){
	if (titleswitch.textContent == "Pick the language you want to chat in"){
		titleswitch.textContent = "Pick the language you want to to teach something to";
	} else{
		titleswitch.textContent == "Pick the language you want to chat in"
	}
});