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
        const toast = document.getElementById('quick-add-toast');

        if (chatBox) {
            chatBox.innerHTML += `
                <div class="message msg-user">
                    <strong>Você</strong><br>${msg}
                </div>
            `;
            chatBox.scrollTop = chatBox.scrollHeight;
        } else if (toast) {
            toast.textContent = "Processando registros...";
            toast.className = "toast toast-loading show";
        }
        
        inputElement.value = '';

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
                if (chatBox) {
                    chatBox.innerHTML += `
                    <div class="message msg-ai">
                        <strong>${config.aiName || 'Agente IA'}</strong><br>${data.reply}
                    </div>
                    `;
                    chatBox.scrollTop = chatBox.scrollHeight;
                } else if (toast) {
                    toast.textContent = "Registrado com sucesso!";
                    toast.className = "toast toast-success show";
                    setTimeout(() => { toast.className = "toast"; }, 3000);
                }

                if (data.transactions && data.transactions.length > 0) {
                    const tbody = document.querySelector('table tbody');
                    if (tbody) {
                        const emptyRow = tbody.querySelector('td[colspan="5"]');
                        if (emptyRow) {
                            tbody.innerHTML = '';
                        }
                        
                        data.transactions.forEach(tx => {
                            const tr = document.createElement('tr');
                            tr.style.opacity = '0';
                            tr.style.transition = 'opacity 0.5s ease-in';
                            tr.style.backgroundColor = 'var(--bg-main)';
                            
                            const badge = tx.type === 'receita' 
                                ? '<span class="badge badge-income">Receita</span>' 
                                : '<span class="badge badge-expense">Despesa</span>';
                                
                            const amountClass = tx.type === 'receita' ? 'text-green' : 'text-red';
                            const amountFormatted = parseFloat(tx.amount).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                            
                            tr.innerHTML = `
                                <td style="color: var(--text-secondary); font-size: 0.9rem;">${tx.date}</td>
                                <td style="font-weight: 500;">${tx.description}</td>
                                <td>${tx.category}</td>
                                <td style="text-align: center;">${badge}</td>
                                <td class="${amountClass}" style="font-weight: 600; text-align: right">R$ ${amountFormatted}</td>
                            `;
                            
                            tbody.insertBefore(tr, tbody.firstChild);
                            
                            setTimeout(() => {
                                tr.style.opacity = '1';
                                setTimeout(() => {
                                    tr.style.backgroundColor = 'transparent';
                                }, 1000);
                            }, 50);
                        });
                    } else if (config.reloadOnTransaction) {
                        setTimeout(() => { window.location.reload(); }, 2000);
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                if (toast) {
                    toast.textContent = "Erro ao registrar.";
                    toast.className = "toast toast-error show";
                    setTimeout(() => { toast.className = "toast"; }, 3000);
                }
            });
    }

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    inputElement.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            if (e.altKey || e.shiftKey) {
                // Allow the default behavior (new line) for Alt+Enter or Shift+Enter
                return;
            } else {
                // Submit message on normal Enter
                e.preventDefault();
                sendMessage();
            }
        }
    });

    // Auto-resize textarea
    inputElement.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});
