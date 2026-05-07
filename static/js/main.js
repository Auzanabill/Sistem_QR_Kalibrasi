/* ==========================================
   CalibrationHub - Main JavaScript
   ========================================== */

// Toggle sidebar on mobile
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    sidebar.classList.toggle('active');
    
    if (overlay) {
        overlay.style.display = sidebar.classList.contains('active') ? 'block' : 'none';
    }
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add fade-in animation to elements
    const animateElements = document.querySelectorAll('[data-animate]');
    animateElements.forEach(function(el, index) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        setTimeout(function() {
            el.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 100 * (index + 1));
    });

    // Search functionality - auto-submit on Enter
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.closest('form').submit();
            }
        });
    });

    // Confirm delete dialogs
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Yakin ingin menghapus?')) {
                e.preventDefault();
            }
        });
    });

    // Animate stat numbers (count up)
    const statValues = document.querySelectorAll('.stat-value[data-count]');
    statValues.forEach(function(el) {
        const target = parseInt(el.dataset.count);
        let current = 0;
        const increment = Math.ceil(target / 30);
        const timer = setInterval(function() {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            el.textContent = current;
        }, 30);
    });
});

// Print QR Code
function printQR() {
    window.print();
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('✅ Disalin ke clipboard');
    });
}

// Simple toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'position-fixed bottom-0 end-0 p-3';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        <div class="toast show glass-card" role="alert">
            <div class="toast-body" style="color: var(--text-primary);">
                ${message}
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    setTimeout(function() { toast.remove(); }, 3000);
}
