// Initialize skill progress bars
document.addEventListener('DOMContentLoaded', function() {
    const skillBars = document.querySelectorAll('.skill-progress');
    skillBars.forEach(bar => {
        const width = bar.getAttribute('data-width');
        if (width) {
            bar.style.width = width + '%';
        }
    });
});
