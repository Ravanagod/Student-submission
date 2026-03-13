function countdown(deadline,id){

let end=new Date(deadline).getTime()

setInterval(function(){

let now=new Date().getTime()

let distance=end-now

let days=Math.floor(distance/(1000*60*60*24))

document.getElementById(id).innerHTML=days+" days left"

},1000)

}