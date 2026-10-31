document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flash').forEach((message) => {
        window.setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-4px)';
            message.style.transition = 'opacity .3s ease, transform .3s ease';
            window.setTimeout(() => message.remove(), 300);
        }, 4500);
    });
});
