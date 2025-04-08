// Main JavaScript file for LMS Platform

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Handle cookie consent interactions
    const cookieConsentBanner = document.querySelector('.cookie-consent-banner');
    if (cookieConsentBanner) {
        const acceptButton = cookieConsentBanner.querySelector('.accept-cookies');
        const rejectButton = cookieConsentBanner.querySelector('.reject-cookies');
        
        if (acceptButton) {
            acceptButton.addEventListener('click', function() {
                // Set cookie to remember user's choice
                document.cookie = "cookie_consent=accepted; max-age=" + (365 * 24 * 60 * 60) + "; path=/";
                cookieConsentBanner.style.display = 'none';
            });
        }
        
        if (rejectButton) {
            rejectButton.addEventListener('click', function() {
                // Set cookie to remember user's choice
                document.cookie = "cookie_consent=rejected; max-age=" + (365 * 24 * 60 * 60) + "; path=/";
                cookieConsentBanner.style.display = 'none';
            });
        }
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Dashboard active link handling
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.list-group-item');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Mobile menu handling
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    }
    
    // Course list filtering
    const courseSearch = document.getElementById('course-search');
    if (courseSearch) {
        courseSearch.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const courseCards = document.querySelectorAll('.course-card');
            
            courseCards.forEach(function(card) {
                const title = card.querySelector('.card-title').textContent.toLowerCase();
                const description = card.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Assignment due date countdown
    const dueDateElements = document.querySelectorAll('.due-date-countdown');
    if (dueDateElements.length > 0) {
        function updateCountdowns() {
            dueDateElements.forEach(function(element) {
                const dueDate = new Date(element.dataset.dueDate);
                const now = new Date();
                const diff = dueDate - now;
                
                if (diff <= 0) {
                    element.textContent = 'Overdue';
                    element.classList.add('text-danger');
                } else {
                    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    
                    if (days > 0) {
                        element.textContent = `${days} days, ${hours} hours remaining`;
                    } else {
                        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                        element.textContent = `${hours} hours, ${minutes} minutes remaining`;
                        
                        if (hours < 24) {
                            element.classList.add('text-warning');
                        }
                    }
                }
            });
        }
        
        // Initial update
        updateCountdowns();
        
        // Update every minute
        setInterval(updateCountdowns, 60000);
    }
    
    // Confirm deletion modals
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
});