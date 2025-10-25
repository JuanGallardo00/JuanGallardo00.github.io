// Donation amount selection
let selectedAmountCents = 1000;

function selectAmount(amountCents) {
    selectedAmountCents = amountCents;
    document.querySelectorAll('.amount-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    document.getElementById('custom-amount-input').value = '';
    updateDonateButton();
}

function selectCustomAmount() {
    const customAmount = parseFloat(document.getElementById('custom-amount-input').value);
    if (customAmount && customAmount >= 0.50) {
        selectedAmountCents = Math.round(customAmount * 100);
        document.querySelectorAll('.amount-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        updateDonateButton();
    }
}

function updateDonateButton() {
    const amountDollars = (selectedAmountCents / 100).toFixed(2);
    document.getElementById('selected-amount').textContent = amountDollars;
}

async function handleDonate() {
    if (selectedAmountCents < 50) {
        showError('El monto minimo es $0.50');
        return;
    }
    if (selectedAmountCents > 99999999) {
        showError('El monto maximo es $999,999.99');
        return;
    }
    showLoading();
    hideError();
    disableButton();
    try {
        const response = await fetch('/stripe/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                amount: selectedAmountCents
            })
        });
        const data = await response.json();
        if (data.error) {
            showError(data.error);
            hideLoading();
            enableButton();
            return;
        }
        window.location.href = data.url;
    } catch (error) {
        showError('Error al procesar la donacion: ' + error.message);
        hideLoading();
        enableButton();
    }
}

function showLoading() {
    document.getElementById('loading-spinner').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading-spinner').classList.remove('show');
}

function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = '\u274C ' + message;
    errorEl.classList.add('show');
}

function hideError() {
    document.getElementById('error-message').classList.remove('show');
}

function disableButton() {
    document.getElementById('donate-button').disabled = true;
}

function enableButton() {
    document.getElementById('donate-button').disabled = false;
}
