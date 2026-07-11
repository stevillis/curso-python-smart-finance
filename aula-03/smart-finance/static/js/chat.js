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
                <div class="max-w-[80%] p-5 text-[1rem] leading-relaxed rounded-2xl bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-50 border border-slate-200 dark:border-slate-800 self-end rounded-br-sm shadow-sm animate-[fadeIn_0.3s_ease-out]">
                    ${msg}
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
                    <div class="max-w-full text-[1rem] leading-relaxed text-slate-900 dark:text-slate-50 self-start animate-[fadeIn_0.3s_ease-out]">
                        <strong class="flex items-center gap-2.5 text-[1rem] mb-3 font-semibold">${config.aiName || 'Agente IA'}</strong>
                        ${data.reply}
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
                                ? '<span class="py-1.5 px-2.5 rounded-md text-[0.75rem] font-semibold uppercase tracking-wider bg-green-500/10 text-green-600 dark:text-green-500">Receita</span>'
                                : '<span class="py-1.5 px-2.5 rounded-md text-[0.75rem] font-semibold uppercase tracking-wider bg-red-500/10 text-red-600 dark:text-red-500">Despesa</span>';

                            const amountClass = tx.type === 'receita' ? 'text-green-600 dark:text-green-500' : 'text-red-600 dark:text-red-500';
                            const amountFormatted = parseFloat(tx.amount).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

                            tr.innerHTML = `
                                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 text-[0.95rem] last:border-b-0">${tx.date}</td>
                                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 font-medium text-slate-900 dark:text-slate-50 last:border-b-0">${tx.description}</td>
                                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 text-[0.95rem] last:border-b-0">${tx.category}</td>
                                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 text-center last:border-b-0">${badge}</td>
                                <td class="py-4 px-7 border-b border-slate-200 dark:border-slate-800 font-semibold text-right last:border-b-0 ${amountClass}">R$ ${amountFormatted}</td>
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
