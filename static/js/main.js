// Main JavaScript File

// Read the CSRF token from the meta tag (see templates/layouts/base.html).
// Every POST/PUT/DELETE fetch() call in this file (and other pages'
// inline scripts) should send this as an X-CSRFToken header, since
// Flask-WTF's CSRFProtect validates it on every state-changing request.
function getCsrfToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Auto-hide alerts after 5 seconds
setTimeout(function() {
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        var bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Confirm delete actions
function confirmDelete(message) {
    return confirm(message || 'Are you sure you want to delete this?');
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'PKR',
        style:'currency'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-PK');
}

// Show loading spinner
function showLoading(element) {
    element.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    element.disabled = true;
}

// Hide loading spinner
function hideLoading(element, text) {
    element.innerHTML = text;
    element.disabled = false;
}

// Print page
function printPage() {
    window.print();
}

// Export table to CSV
function exportTableToCSV(tableId, filename) {
    var csv = [];
    var rows = document.querySelectorAll('#' + tableId + ' tr');
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (var j = 0; j < cols.length; j++) {
            row.push('"' + cols[j].innerText + '"');
        }
        
        csv.push(row.join(','));
    }
    
    downloadCSV(csv.join('\n'), filename);
}

function downloadCSV(csv, filename) {
    var csvFile;
    var downloadLink;
    
    csvFile = new Blob([csv], {type: 'text/csv'});
    downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
}

// Search functionality
function searchTable(inputId, tableId) {
    var input, filter, table, tr, td, i, txtValue;
    input = document.getElementById(inputId);
    filter = input.value.toUpperCase();
    table = document.getElementById(tableId);
    tr = table.getElementsByTagName('tr');
    
    for (i = 1; i < tr.length; i++) {
        tr[i].style.display = 'none';
        td = tr[i].getElementsByTagName('td');
        
        for (var j = 0; j < td.length; j++) {
            if (td[j]) {
                txtValue = td[j].textContent || td[j].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    tr[i].style.display = '';
                    break;
                }
            }
        }
    }
}

// Form validation
function validateForm(formId) {
    var form = document.getElementById(formId);
    if (!form.checkValidity()) {
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// AJAX helper
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (successCallback) successCallback(data);
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) errorCallback(error);
    });
}

// Show notification
function showNotification(message, type) {
    var alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    var container = document.querySelector('main');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(function() {
        alertDiv.remove();
    }, 5000);
}

// Get current date in YYYY-MM-DD format
function getCurrentDate() {
    var today = new Date();
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0');
    var yyyy = today.getFullYear();
    return yyyy + '-' + mm + '-' + dd;
}

// Calculate days between dates
function daysBetween(date1, date2) {
    var oneDay = 24 * 60 * 60 * 1000;
    var firstDate = new Date(date1);
    var secondDate = new Date(date2);
    return Math.round(Math.abs((firstDate - secondDate) / oneDay));
}

// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('show');
        });
    }
});

// ============================================
// Dark / Light Theme Toggle
// Uses existing #themeToggle button and #themeIcon icon
// Persists preference in localStorage under key "theme"
// ============================================

// Apply the given theme ('dark' or 'light') to the page and update the icon
function applyTheme(theme) {
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
    }

    var themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        if (theme === 'dark') {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    }
}

// Toggle between dark and light theme, save preference, and update icon
function toggleTheme() {
    var isDark = document.body.classList.contains('dark-theme');
    var newTheme = isDark ? 'light' : 'dark';

    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

// Restore saved theme on page load (defaults to light if none saved)
function initializeTheme() {
    var savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    var themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
});

// ============================================
// Notification Bell
// Polls /notifications/recent every 30s, fills the
// navbar dropdown, and updates the unread badge.
// Does nothing if the bell isn't on the page (e.g. auth pages).
// ============================================

var NOTIFICATION_POLL_MS = 30000;

function timeAgo(dateStr) {
    // dateStr looks like "2026-07-28 14:30"
    var then = new Date(dateStr.replace(' ', 'T'));
    var diffMs = Date.now() - then.getTime();
    var minutes = Math.floor(diffMs / 60000);

    if (isNaN(minutes)) return dateStr;
    if (minutes < 1) return 'just now';
    if (minutes < 60) return minutes + 'm ago';
    var hours = Math.floor(minutes / 60);
    if (hours < 24) return hours + 'h ago';
    var days = Math.floor(hours / 24);
    return days + 'd ago';
}

function renderNotificationBadge(count) {
    var badge = document.getElementById('notificationBadge');
    if (!badge) return;

    if (count > 0) {
        badge.textContent = count > 9 ? '9+' : String(count);
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

function renderNotificationList(notifications) {
    var list = document.getElementById('notificationList');
    if (!list) return;

    if (!notifications || notifications.length === 0) {
        list.innerHTML = '<div class="text-center text-muted py-4 small">' +
            '<i class="fas fa-bell-slash"></i> No notifications yet</div>';
        return;
    }

    list.innerHTML = notifications.map(function (n) {
        var unreadClass = n.is_read ? '' : ' notification-unread';
        return '' +
            '<a href="#" class="notification-item' + unreadClass + '" data-id="' + n.id + '" data-link="' + (n.link || '') + '">' +
                '<span class="notification-icon notification-icon-' + n.category + '">' +
                    '<i class="fas fa-' + n.icon + '"></i>' +
                '</span>' +
                '<span class="notification-item-body">' +
                    '<span class="notification-item-title">' + n.title + '</span>' +
                    (n.message ? '<span class="notification-item-message">' + n.message + '</span>' : '') +
                    '<span class="notification-item-time">' + timeAgo(n.created_at) + '</span>' +
                '</span>' +
            '</a>';
    }).join('');

    list.querySelectorAll('.notification-item').forEach(function (item) {
        item.addEventListener('click', function (e) {
            e.preventDefault();
            var id = this.getAttribute('data-id');
            var link = this.getAttribute('data-link');

            fetch('/notifications/' + id + '/read', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
                .then(function () {
                    refreshNotifications();
                    if (link) window.location.href = link;
                });
        });
    });
}

function refreshNotifications() {
    var bell = document.getElementById('notificationBell');
    if (!bell) return;

    fetch('/notifications/recent')
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (!data.success) return;
            renderNotificationBadge(data.unread_count);
            renderNotificationList(data.notifications);
        })
        .catch(function () { /* fail silently, keep last known state */ });
}

function initializeNotifications() {
    var bell = document.getElementById('notificationBell');
    if (!bell) return;

    // Load once immediately, then whenever the dropdown is opened, then on an interval
    refreshNotifications();
    bell.addEventListener('click', refreshNotifications);
    setInterval(refreshNotifications, NOTIFICATION_POLL_MS);

    var markAllBtn = document.getElementById('markAllReadBtn');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function () {
            fetch('/notifications/mark-all-read', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
                .then(refreshNotifications);
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeNotifications();
});