const navBar = document.querySelector('#main-nav-bar-tabs');
for(let ele of navBar.children){
	ele.addEventListener('click', navigate);
}

function navigate(e){
	e.preventDefault();
	console.log(e);
	console.log(e.target.text);
	e.target.style.textDecoration="underline"
	console.log(e.target.parentElement.nodeName)
}
