document.addEventListener('DOMContentLoaded', function() {
    var notification = document.querySelector('.notification');

    if (notification) {
        setTimeout(function() {
            notification.classList.add('active');
        }, 1000); 

        setTimeout(function() {
            notification.classList.remove('active');
        }, 6000); 
    }
});