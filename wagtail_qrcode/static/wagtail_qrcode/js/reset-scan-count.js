// Keep this action outside the page form's save / publish lifecycle.
document.addEventListener('click', async (event) => {
    const button = event.target.closest('[data-qr-reset-url]');
    if (!button || button.disabled) return;
    event.preventDefault();
    if (!window.confirm(button.dataset.confirm)) return;

    const panel = button.closest('[data-qr-scan-count]');
    const status = panel.querySelector('[data-qr-reset-status]');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    button.disabled = true;
    status.textContent = '';
    try {
        const response = await fetch(button.dataset.qrResetUrl, {
            method: 'POST',
            mode: 'same-origin',
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        if (!response.ok) throw new Error('Reset failed');
        const data = await response.json();
        if (data.usage_count !== 0 || typeof data.count_label !== 'string') {
            throw new Error('Invalid reset response');
        }
        panel.querySelector('[data-qr-count-label]').textContent = data.count_label;
        status.textContent = button.dataset.success;
    } catch {
        status.textContent = button.dataset.error;
        button.disabled = false;
    }
});
