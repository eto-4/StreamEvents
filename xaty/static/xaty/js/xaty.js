document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatErrors = document.getElementById('chat-errors');
    const messageCount = document.getElementById('message-count');

    // ——— Utilitats ———————————————————————————————————————————————————

    function escapeHtml(text) {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function scrollToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function updateMessageCount(count) {
        if (messageCount) {
            messageCount.textContent = count + ' missatges';
        }
    }

    // ——— Crear element HTML d'un missatge ———————————————————————————————————————————————————
    function createMessageElement(message) {
        const div = document.createElement('div');
        div.classList.add('chat-message');
        if (message.is_highlighted) div.classList.add('highlighted');
        div.dataset.messageId = message.id;

        div.innerHTML = `
            <div class="message-header">
                <strong class="message-username">${escapeHtml(message.display_name)}</strong>
                <small class="text-muted">${escapeHtml(message.created_at)}</small>
            </div>
            <div class="message-content">
                <p class="mb-0">${escapeHtml(message.message)}</p>
            </div>
            ${message.can_delete ? `
            <div class="message-actions">
                <button class="btn btn-sm delete-message" data-message-id="${message.id}">
                    <i class="bi bi-trash"></i>
                </button>
            </div>` : ''}
        `;
        return div;
    }

    // ─── Carregar missatges ———————————————————————————————————————————————————
    
    function loadMessages() {
        fetch(`/xaty/${eventId}/messages/`)
        .then(res => res.json())
        .then(data => {
            const loadingText = document.getElementById('loading-text');
            if (loadingText) loadingText.remove();
        
            chatMessages.innerHTML = '';
        
            if (data.messages.length === 0) {
                if (eventStatus === 'live') {
                    chatMessages.innerHTML = '<p class="text-muted text-center small">Encara no hi ha missatges. Sigues el primer!</p>';
                }
                // Si no és live: no mostrem res, el loading ja ha desaparegut
            } else {
                data.messages.forEach(msg => {
                    chatMessages.appendChild(createMessageElement(msg));
                });
            }
        
            scrollToBottom();
            updateMessageCount(data.messages.length);
        })
        .catch(err => console.error('Error carregant missatges:', err));
    }

    // ——— Enviar missatge ———————————————————————————————————————————————————
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const textarea = chatForm.querySelector('textarea');
            const csrfToken = chatForm.querySelector('[name=csrfmiddlewaretoken]').value;

            if (chatErrors) chatErrors.textContent = '';

            fetch(`/xaty/${eventId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken,
                },
                body: new URLSearchParams({ message: textarea.value, csrfmiddlewaretoken: csrfToken })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        textarea.value = '';
                        loadMessages();
                    } else {
                        if (chatErrors && data.errors?.message) {
                            chatErrors.textContent = data.errors.message[0];
                        }
                    }
                })
                .catch(
                    err => console.error(
                        'Error enviant missatge:', 
                        err
                    )
                );
        });
    }

    // ─── Eliminar missatge (event delegation) ———————————————————————————————————————————————————

    if (chatMessages) {
        chatMessages.addEventListener('click', function (e) {
            const btn = e.target.closest('.delete-message');
            if (!btn) return;

            const messageId = btn.dataset.messageId;

            // Missatge de confirmació
            if (!confirm('Segur que vols eliminar aquest missatge?')) return;

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');

            fetch(`/xaty/message/${messageId}/delete/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrfToken ? csrfToken.value : '',
                },
                body: new URLSearchParams({
                    csrfmiddlewaretoken: csrfToken ? csrfToken.value : ''
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.success) loadMessages();
                })
                .catch( err => console.error(
                    'Error eliminant missatge: ', err
                ));
        });
    }

    // ─── Inicialització ———————————————————————————————————————————————————

    if (chatMessages) {
        loadMessages();
        setInterval(loadMessages, 3000);
    }
});