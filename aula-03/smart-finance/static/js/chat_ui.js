document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chat-input');
    const sendBtn = document.getElementById('chat-send-btn');
    const welcomeScreen = document.getElementById('welcome-screen');

    function hideWelcome() {
        if (welcomeScreen && input.value.trim() !== '') {
            welcomeScreen.style.display = 'none';
        }
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', hideWelcome);
    }
    
    if (input) {
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !e.altKey) {
                hideWelcome();
            }
        });
    }
    
    // Expose fillInput for suggestion pills
    window.fillInput = function(btn) {
        if (input) {
            input.value = btn.innerText.trim();
            input.focus();
            input.style.height = 'auto';
            input.style.height = (input.scrollHeight) + 'px';
        }
    };
});
