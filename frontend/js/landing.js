/* ========================================
   LANDING PAGE - BetM8 Casino Online
   JavaScript para interactividad basica
   ======================================== */

// ===== MENU HAMBURGUESA EN MOVIL =====
// Abre y cierra el menu de navegacion en pantallas pequenas
const btnHamburguesa = document.getElementById('btn-hamburguesa');
const navbarEnlaces = document.getElementById('navbar-enlaces');

btnHamburguesa.addEventListener('click', function () {
    navbarEnlaces.classList.toggle('activo');
});

// Cerrar el menu cuando se hace clic en un enlace (movil)
const enlaces = navbarEnlaces.querySelectorAll('.navbar-link');

enlaces.forEach(function (enlace) {
    enlace.addEventListener('click', function () {
        navbarEnlaces.classList.remove('activo');
    });
});

// ===== NAVBAR CON FONDO AL HACER SCROLL =====
// Oscurece el fondo del navbar cuando el usuario baja la pagina
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', function () {
    if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(8, 8, 8, 0.98)';
    } else {
        navbar.style.backgroundColor = 'rgba(13, 13, 13, 0.95)';
    }
});
