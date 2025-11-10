const light_dark = document.querySelector('#color_changer');
light_dark.addEventListener('click', function() {
document.body.classList.toggle('dark');
console.log('clicked');
});