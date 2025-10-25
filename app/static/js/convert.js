// Tab switching functionality
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');
}

// File list display
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('images-input').addEventListener('change', function(e) {
        displayFileList(e.target.files, 'images-file-list');
    });

    document.getElementById('merge-input').addEventListener('change', function(e) {
        displayFileList(e.target.files, 'merge-file-list');
    });

    document.getElementById('split-input').addEventListener('change', function(e) {
        displayFileList(e.target.files, 'split-file-list');
    });
});

function displayFileList(files, listId) {
    const listEl = document.getElementById(listId);
    listEl.innerHTML = '';
    if (files.length > 0) {
        Array.from(files).forEach(file => {
            const item = document.createElement('div');
            item.className = 'file-item';
            const sizeSpan = document.createElement('span');
            sizeSpan.className = 'file-item-size';
            sizeSpan.textContent = (file.size / 1024).toFixed(2) + ' KB';
            item.innerHTML = '<span>' + file.name + '</span>';
            item.appendChild(sizeSpan);
            listEl.appendChild(item);
        });
    }
}

// Convert images to PDF
async function convertImagesToPDF() {
    const files = document.getElementById('images-input').files;
    if (files.length === 0) {
        showError('images-error', 'Por favor selecciona al menos una imagen');
        return;
    }
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files[]', file));
    showLoading('images-loading');
    hideResult('images-result');
    hideError('images-error');
    try {
        const response = await fetch('/convert/upload/images-to-pdf', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        hideLoading('images-loading');
        if (data.success) {
            showResult('images-result', '&#10004; ' + data.message + '<br><a href="' + data.download_url + '" class="btn btn-primary download-link">Descargar PDF</a>');
        } else {
            showError('images-error', data.error || 'Error desconocido');
        }
    } catch (error) {
        hideLoading('images-loading');
        showError('images-error', 'Error de conexion: ' + error.message);
    }
}

// Merge PDFs
async function mergePDFs() {
    const files = document.getElementById('merge-input').files;
    if (files.length < 2) {
        showError('merge-error', 'Por favor selecciona al menos 2 PDFs');
        return;
    }
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('files[]', file));
    showLoading('merge-loading');
    hideResult('merge-result');
    hideError('merge-error');
    try {
        const response = await fetch('/convert/upload/merge-pdfs', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        hideLoading('merge-loading');
        if (data.success) {
            showResult('merge-result', '&#10004; ' + data.message + '<br><a href="' + data.download_url + '" class="btn btn-primary download-link">Descargar PDF Unido</a>');
        } else {
            showError('merge-error', data.error || 'Error desconocido');
        }
    } catch (error) {
        hideLoading('merge-loading');
        showError('merge-error', 'Error de conexion: ' + error.message);
    }
}

// Split PDF
async function splitPDF() {
    const file = document.getElementById('split-input').files[0];
    if (!file) {
        showError('split-error', 'Por favor selecciona un PDF');
        return;
    }
    const startPage = document.getElementById('start-page').value;
    const endPage = document.getElementById('end-page').value;
    const formData = new FormData();
    formData.append('file', file);
    formData.append('start_page', startPage);
    formData.append('end_page', endPage);
    showLoading('split-loading');
    hideResult('split-result');
    hideError('split-error');
    try {
        const response = await fetch('/convert/upload/split-pdf', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        hideLoading('split-loading');
        if (data.success) {
            showResult('split-result', '&#10004; ' + data.message + '<br><a href="' + data.download_url + '" class="btn btn-primary download-link">Descargar PDF Dividido</a>');
        } else {
            showError('split-error', data.error || 'Error desconocido');
        }
    } catch (error) {
        hideLoading('split-loading');
        showError('split-error', 'Error de conexion: ' + error.message);
    }
}

// Helper functions
function showLoading(id) {
    document.getElementById(id).classList.add('show');
}

function hideLoading(id) {
    document.getElementById(id).classList.remove('show');
}

function showResult(id, message) {
    const el = document.getElementById(id);
    el.innerHTML = message;
    el.classList.add('show');
}

function hideResult(id) {
    document.getElementById(id).classList.remove('show');
}

function showError(id, message) {
    const el = document.getElementById(id);
    el.innerHTML = '&#10060; ' + message;
    el.classList.add('show');
}

function hideError(id) {
    document.getElementById(id).classList.remove('show');
}
