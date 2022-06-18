var winner
var loser

var results

const left_noun = document.querySelector('#left_noun');
const right_noun = document.querySelector('#right_noun');
const left_noun_title=document.querySelector('#noun1-title')
const right_noun_title =document.querySelector('#noun2-title')

const vertical_line = document.querySelector('#vertical-line')

left_noun.addEventListener("mouseover",darken);
right_noun.addEventListener("mouseover",darken);

left_noun_title.addEventListener("mouseover",darken);
right_noun_title.addEventListener("mouseover",darken);

left_noun.addEventListener("mouseout",lighten);
right_noun.addEventListener("mouseout",lighten);

left_noun_title.addEventListener("mouseout",lighten);
right_noun_title.addEventListener("mouseout",lighten);

var category_url

$.ajax({
 type: "GET",
 url: "/get_category_url/"+category_id,
 contentType: "application/json",
 dataType: 'json',
 success: function(result){
	 console.log("Category_url Received");
	 //make global variable results
	 category_url = result['category_url']
	 console.log(category_url)
	 matchup();
 }
});


left_noun.addEventListener("click",win);
right_noun.addEventListener("click",win);


function win(e){
	console.log('HELLO')
	if(e.target.id == "left_noun" || e.target.parentElement.parentElement.id == "left_noun"){
		winner=results.noun1_id
		loser=results.noun2_id
	}else if( e.target.id == "right_noun" || e.target.parentElement.parentElement.id == "right_noun"){
		winner=results.noun2_id
		loser=results.noun1_id
	}
	var server_data=[
		{"winner":winner},
		{"loser":loser},
		{"category_url":category_url}
	];

	//var xhttp = new XMLHttpRequest();
	//xhttp.open('POST','/game');
	//xhttp.setRequestHeader("Content-type", "application/json");
	//xhttp.send(JSON.stringify(server_data));
	//METHOD 2
	//console.log(e.target.id);

	$.ajax({
   type: "POST",
	 method: "POST",
   url: "/game_results",
   data: JSON.stringify(server_data),
	 contentType: "application/json",
   dataType: 'json'
 });
 $.ajax({
	type: "POST",
	method: "POST",
	url: "/matchup",
	data: JSON.stringify([{'category_url':category_url}]),
	contentType: "application/json",
	dataType: 'json',
	success: function(result){
		results = result;
    update_data(result);
  }
});
}
// When new matchup is received, images must be switched since the site can't reload a url it's already on
function update_data(result){
	//console.log(result);
	//console.log(result.noun1_image);
	left_noun.style.backgroundImage = "url("+result.noun1_image+")";
	right_noun.style.backgroundImage = "url("+result.noun2_image+")";
	left_noun_title.innerText = results.noun1_name
	right_noun_title.innerText = results.noun2_name
}

function darken(e){
	e.preventDefault;
	//e.target.style.background = "lightgray";
	color_change = "orange"
	e.target.style.borderColor = color_change;
	//e.target.style.backgroundImage = "url('js/images/man.png')";
	//vertical_line.style.backgroundColor = color_change;
}
function lighten(e){
	e.preventDefault;
	//e.target.style.background = "white";
	e.target.style.borderColor = "white";

	vertical_line.style.backgroundColor = "black";
}


window.addEventListener("resize", resize_background);

function resize_background(){
	left_noun.style.backgroundSize = String(right_noun.clientWidth)+"px " +String(right_noun.clientHeight)+"px"
	right_noun.style.backgroundSize = String(right_noun.clientWidth)+"px " +String(right_noun.clientHeight)+"px"
}
resize_background();
//console.log(String(right_noun.clientWidth)+" "+String(right_noun.clientHeight));
//console.log(left_noun.clientHidth)

//causes Update data function after post request receives ping back that data was received
function matchup(){
$.ajax({
 type: "POST",
 url: "/matchup",
 data: JSON.stringify([{'category_url':category_url}]),
 contentType: "application/json",
 dataType: 'json',
 success: function(result){
	 console.log("matchup data received");
	 //make global variable results
	 results=result
	 update_data(result);
 }
});
};
