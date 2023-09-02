let navbar = document.querySelector('#navBar');
let navBarWrapper = document.querySelector('#navBarWrapper');
const menuIconWrapper = document.querySelector('#menuIconWrapper');

let aux = 0;

document.onclick = element => {
  if ( element.target.id !== 'menuIconWrapper' && element.target.id !== 'navBar') {
    navbar.classList.remove('showMe');
    menuIconWrapper.classList.remove('active');
  }
}

window.addEventListener('scroll', () => {

    if(window.scrollY>aux){
      navBarWrapper.classList.add('ocultar');
      navbar.classList.remove('showMe');
      menuIconWrapper.classList.remove('active');
    }
     else{
       navBarWrapper.classList.remove('ocultar');
    }
  
   aux = window.scrollY;
});

menuIconWrapper.onclick = () => toggleEfect()

document.querySelectorAll('.linkSelect').forEach( el => el.setAttribute('onclick','toggleEfect()'))

function toggleEfect(){
  navbar.classList.toggle('showMe');
  menuIconWrapper.classList.toggle('active');
}