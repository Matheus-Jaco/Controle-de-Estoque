function toggleMovement(productId, productName) {
    const modal = document.getElementById('movementModal');
    const form = document.getElementById('movementForm');
    form.action = `/products/move/${productId}`;
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('movementModal');
    modal.style.display = 'none';
}

function setSidebarCollapsed(collapsed) {
    const layout = document.querySelector('.layout');
    if (!layout) return;
    layout.classList.toggle('collapsed', collapsed);
    document.documentElement.classList.toggle('sidebar-collapsed', collapsed);
    localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0');
}

window.onclick = function(event) {
    const modal = document.getElementById('movementModal');
    if (event.target === modal) {
        closeModal();
    }
};

window.addEventListener('DOMContentLoaded', function() {
    const toggleButtons = document.querySelectorAll('.sidebar-toggle');
    const collapsed = localStorage.getItem('sidebarCollapsed') === '1';
    setSidebarCollapsed(collapsed);
    toggleButtons.forEach(toggleButton => {
        toggleButton.addEventListener('click', function() {
            const current = document.documentElement.classList.contains('sidebar-collapsed');
            setSidebarCollapsed(!current);
        });
    });

    const flashCloseButtons = document.querySelectorAll('.flash-close');
    flashCloseButtons.forEach(button => {
        button.addEventListener('click', () => {
            const flash = button.closest('.flash');
            if (flash) flash.remove();
        });
    });

    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(flash => {
        setTimeout(() => flash.remove(), 6000);
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const clearZeroFields = form.querySelectorAll('input[data-clear-zero]');
        clearZeroFields.forEach(field => {
            field.addEventListener('focus', function() {
                if (this.value === '0' || this.value === '0.00') {
                    this.value = '';
                }
            });
            field.addEventListener('blur', function() {
                if (this.value.trim() === '') {
                    if (this.type === 'number') {
                        this.value = this.dataset.clearZeroDefault || '0';
                    }
                }
            });
        });

        form.addEventListener('submit', function(event) {
            const valid = Array.from(form.elements).every(input => {
                if (input.required && input.type !== 'submit' && input.type !== 'button') {
                    return input.value.trim() !== '';
                }
                return true;
            });
            if (!valid) {
                event.preventDefault();
                showFlashMessage('danger', 'Preencha todos os campos obrigatórios.');
            }
        });
    });

    const userDropdownBtn = document.getElementById('userDropdownBtn');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    const changeUserInfoItem = document.getElementById('changeUserInfoItem');
    const userInfoModal = document.getElementById('userInfoModal');
    const userInfoModalClose = document.getElementById('userInfoModalClose');
    const cancelUserInfoChange = document.getElementById('cancelUserInfoChange');

    if (userDropdownBtn && userDropdownMenu) {
        userDropdownBtn.addEventListener('click', function(event) {
            event.stopPropagation();
            const expanded = userDropdownBtn.getAttribute('aria-expanded') === 'true';
            userDropdownBtn.setAttribute('aria-expanded', !expanded);
            userDropdownMenu.classList.toggle('show');
        });

        document.addEventListener('click', function(event) {
            if (!userDropdownBtn.contains(event.target) && !userDropdownMenu.contains(event.target)) {
                userDropdownBtn.setAttribute('aria-expanded', 'false');
                userDropdownMenu.classList.remove('show');
            }
        });
    }

    if (changeUserInfoItem && userInfoModal) {
        changeUserInfoItem.addEventListener('click', function(event) {
            event.preventDefault();
            userDropdownBtn.setAttribute('aria-expanded', 'false');
            userDropdownMenu.classList.remove('show');
            userInfoModal.style.display = 'flex';
        });
    }

    if (userInfoModalClose && userInfoModal) {
        userInfoModalClose.addEventListener('click', function() {
            userInfoModal.style.display = 'none';
        });
    }

    if (cancelUserInfoChange && userInfoModal) {
        cancelUserInfoChange.addEventListener('click', function() {
            userInfoModal.style.display = 'none';
        });
    }

    const passwordToggles = document.querySelectorAll('.password-toggle');
    const eyeOpenIcon = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z" /><path d="M8 12a4 4 0 0 1 8 0" /></svg>';
    const eyeClosedIcon = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12Z" /><path d="M8 12a4 4 0 0 1 8 0" /><path d="M4 4l16 16" /></svg>';

    passwordToggles.forEach(toggle => {
        const targetId = toggle.dataset.target;
        const targetInput = document.getElementById(targetId);
        if (!targetInput) return;

        const setIcon = visible => {
            const icon = toggle.querySelector('.password-icon');
            if (!icon) return;
            icon.innerHTML = visible ? eyeOpenIcon : eyeClosedIcon;
            toggle.dataset.visible = visible ? 'true' : 'false';
            toggle.setAttribute('aria-label', visible ? 'Ocultar senha' : 'Mostrar senha');
        };

        setIcon(targetInput.type === 'text');

        toggle.addEventListener('click', function() {
            const visible = targetInput.type === 'password';
            targetInput.type = visible ? 'text' : 'password';
            setIcon(visible);
        });
    });

    if (typeof salesData !== 'undefined') {
        createChart('salesChart', 'Vendas', salesData);
    }
    if (typeof restockData !== 'undefined') {
        createChart('restockChart', 'Reposições', restockData);
    }
    if (typeof notesData !== 'undefined') {
        createPieChart('notesChart', notesData);
    }
});

function showFlashMessage(category, message) {
    let flashList = document.querySelector('.flash-list');
    const content = document.querySelector('.content');
    if (!flashList && content) {
        flashList = document.createElement('div');
        flashList.className = 'flash-list';
        content.prepend(flashList);
    }
    if (!flashList) return;

    const flash = document.createElement('div');
    flash.className = `flash ${category}`;
    flash.innerHTML = `<span>${message}</span><button type="button" class="flash-close" aria-label="Fechar">&times;</button>`;
    flashList.appendChild(flash);

    const closeButton = flash.querySelector('.flash-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => flash.remove());
    }

    setTimeout(() => flash.remove(), 6000);
}

function createChart(canvasId, label, dataPoints) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const labels = dataPoints.map(item => item.month);
    const values = dataPoints.map(item => item.total);
    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                borderColor: '#33d67a',
                backgroundColor: 'rgba(51,214,122,0.18)',
                tension: 0.35,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 250,
                easing: 'easeOutQuart'
            },
            hover: {
                mode: 'nearest',
                intersect: true,
                animationDuration: 0
            },
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#a2b1d0' } },
                y: { beginAtZero: true, ticks: { color: '#a2b1d0' } }
            }
        }
    });
}

function createPieChart(canvasId, dataPoints) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const labels = dataPoints.map(item => item.status);
    const values = dataPoints.map(item => item.total);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: ['#f4b740', '#4ecea2'],
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 250,
                easing: 'easeOutQuart'
            },
            hover: {
                mode: 'nearest',
                intersect: true,
                animationDuration: 0
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#a2b1d0' } }
            }
        }
    });
}
