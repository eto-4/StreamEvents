document.addEventListener('DOMContentLoaded', function () {
    const toggleBtn = document.getElementById('assistant-toggle');
    const panel = document.getElementById('assistant-panel');
    const closeBtn = document.getElementById('assistant-close');
    const sendBtn = document.getElementById('assistant-send');
    const input = document.getElementById('assistant-input');
    const messages = document.getElementById('assistant-messages');

    // ─── Obrir / tancar panel ─────────────────────────────────
    toggleBtn.addEventListener('click', function () {
        const isOpen = panel.style.display === 'flex';
        panel.style.display = isOpen ? 'none' : 'flex';
        toggleBtn.style.display = isOpen ? 'flex' : 'none';
    });

    closeBtn.addEventListener('click', function () {
        panel.style.display = 'none';
        toggleBtn.style.display = 'flex';
    });

    // ─── Auto-créixer textarea ────────────────────────────────
    input.addEventListener('input', function () {
        this.style.height = 'auto';
        const maxHeight = parseInt(getComputedStyle(this).lineHeight) * 4;
        this.style.height = Math.min(this.scrollHeight, maxHeight) + 'px';
    });

    // ─── Enviar amb Enter ─────────────────────────────────────
    input.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener('click', sendMessage);

    // ─── Afegir missatge ──────────────────────────────────────
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.classList.add('assistant-msg', isUser ? 'user' : 'bot');
        div.innerText = text;
        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
        return div;
    }

    // ─── Afegir cards d'events ────────────────────────────────
    function addEventCards(events) {
        if (!events || events.length === 0) return;
        const wrapper = document.createElement('div');
        wrapper.classList.add('assistant-event-cards');
        events.forEach(evt => {
            const card = document.createElement('a');
            card.href = evt.url;
            card.classList.add('assistant-event-card');
            card.innerHTML = `
                <strong>${evt.title}</strong>
                <div class="event-meta">${evt.category} · ${evt.scheduled_date ? evt.scheduled_date.split('T')[0] : ''}</div>
            `;
            wrapper.appendChild(card);
        });
        messages.appendChild(wrapper);
        messages.scrollTop = messages.scrollHeight;
    }

    // ─── Enviar missatge ──────────────────────────────────────
    async function sendMessage() {
        const msg = input.value.trim();
        if (!msg) return;
        const onlyFuture = document.getElementById('only-future').checked;

        addMessage(msg, true);
        input.value = '';
        input.style.height = 'auto';

        const thinking = addMessage('Pensant...', false);

        try {
            const resp = await fetch('/assistant/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, only_future: onlyFuture })
            });
            const data = await resp.json();
            thinking.remove();
            addMessage(data.answer || '', false);
            addEventCards(data.events || []);
            if (data.follow_up) {
                addMessage(data.follow_up, false);
            }
        } catch (err) {
            thinking.innerText = 'Error de connexió. Torna-ho a provar.';
        }
    }
});