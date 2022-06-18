console.log("Running Divclick.js");
containers=document.querySelectorAll('.category-card');

for(i=0; i < containers.length; i++) {
	console.log("Hello")
	let container=containers[i];
	container.addEventListener("mouseover",darken);
	container.addEventListener("mouseout",lighten);
	container.addEventListener("click",clicked);
	for(j=0; j < container.children.length; j++){

		container.children[j].addEventListener("click",clicked);
		container.children[j].addEventListener("mouseover",darken);
		container.children[j].addEventListener("mouseout",lighten);
	};
};

//ON CLICK
function clicked(e){
	if(e.target.nodeName=='DIV'){
		name = (e.target.innerText);
	}
	else{
		name= (e.target.parentElement.firstElementChild.innerText);
	}
	console.log(name)
	var server_data=[
		{"name":name}
	];
	//var xhttp = new XMLHttpRequest();
	//xhttp.open('POST','/game');
	//xhttp.setRequestHeader("Content-type", "application/json");
	//xhttp.send(JSON.stringify(server_data));
	//METHOD 2
	//console.log(e.target.id);

//
/*
	$.ajax({
   type: "POST",
	 //function to post to, whatever is in url is essentially url_for
   url: "/category_js_redirect",
   data: JSON.stringify(server_data),
	 contentType: "application/json",
   dataType: 'json'

 });
*/
}


function darken(e){
	e.preventDefault;
	console.log(e)
	if(e.target.nodeName=='DIV'){
		e.target.style.borderColor = "black";
	}
	else{
		e.target.parentElement.style.borderColor="black";
	}

	//e.target.style.background = "lightgray";


	//e.target.style.backgroundImage = "url('js/images/man.png')";
};
function lighten(e){
	e.preventDefault;
	console.log(e);
	if(e.target.nodeName=='DIV'){
		e.target.style.borderColor = "white";
	}
	else{
		e.target.parentElement.style.borderColor="white";
	};

	//e.target.style.background = "white";

};


//left_person.style.backgroundSize = String(right_person.clientWidth)+"px "+String(right_person.clientHeight+"px")
//right_person.style.backgroundSize = String(right_person.clientWidth)+"px "+String(right_person.clientHeight+"px")
//console.log(String(right_person.clientWidth)+" "+String(right_person.clientHeight));
//console.log(left_person.clientHidth)
