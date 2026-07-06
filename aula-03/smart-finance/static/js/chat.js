document.addEventListener('DOMContentLoaded', function () {
    const inputElement = document.getElementById('chat-input');
    const sendButton = document.getElementById('chat-send-btn');
    if (!inputElement) return;

    const configElement = document.getElementById('chat-config');
    let config = {};
    if (configElement) {
        config = JSON.parse(configElement.textContent);
    }

    function sendMessage() {
        const msg = inputElement.value.trim();
        if (!msg) return;

        const chatBox = document.getElementById('chat-messages');
        chatBox.innerHTML += `
            <div class="message msg-user">
                <strong>Você</strong><br>${msg}
            </div>
        `;
        inputElement.value = '';
        chatBox.scrollTop = chatBox.scrollHeight;

        const formData = new FormData();
        formData.append('message', msg);
        if (config.csrfToken) {
            formData.append('csrfmiddlewaretoken', config.csrfToken);
        }

        fetch(config.apiUrl, {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                chatBox.innerHTML += `
                <div class="message msg-ai">
                    <strong>${config.aiName || 'Agente IA'}</strong><br>${data.reply}
                </div>
            `;
                chatBox.scrollTop = chatBox.scrollHeight;

                if (config.reloadOnTransaction) {
                    if (data.reply.includes('Lançamento feito') || data.reply.includes('Registrei')) {
                        setTimeout(() => { window.location.reload(); }, 2000);
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    inputElement.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
