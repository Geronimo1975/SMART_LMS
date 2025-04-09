// Main JavaScript file for SmartLMS - Lecturio-inspired Version

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartLMS JavaScript initialized');
    
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Initialize scroll animations
    initializeScrollAnimations();
    
    // Initialize counters in the trust badges
    initializeCounters();
    
    // Course list filtering
    initializeCourseSearch();
    
    // Add smooth scrolling to all links
    initializeSmoothScrolling();
    
    // Handle cookie consent interactions
    initializeCookieConsent();
    
    // Auto-dismiss alerts after 5 seconds
    initializeAlertAutoDismiss();
    
    // Dashboard active link handling
    highlightActiveLinks();
    
    // Handle form validation
    setupFormValidation();
    
    // Assignment due date countdown
    initializeAssignmentCountdowns();
    
    // Confirm deletion modals
    setupDeleteConfirmations();
});

// Initialize Bootstrap components
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Toasts
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl);
    });
    
    // Dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });
}

// Animated counters for trust badges
function initializeCounters() {
    const trustBadgeValues = document.querySelectorAll('.trust-badge-value');
    
    trustBadgeValues.forEach(badge => {
        const target = badge.textContent;
        const countDuration = 2000; // 2 seconds
        let startTime;
        
        // Extract the numeric part (strip the + or other non-numeric symbols)
        const numericTarget = parseInt(target.replace(/[^0-9]/g, ''));
        const suffix = target.replace(/[0-9]/g, '');
        
        badge.textContent = '0' + suffix;
        
        const updateCounter = (timestamp) => {
            if (!startTime) startTime = timestamp;
            const elapsed = timestamp - startTime;
            const progress = Math.min(elapsed / countDuration, 1);
            
            // Calculate current count using easeOutCubic easing function
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            const currentCount = Math.floor(numericTarget * easedProgress);
            
            badge.textContent = currentCount + suffix;
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        };
        
        // Start the animation when element is in view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    requestAnimationFrame(updateCounter);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        observer.observe(badge);
    });
}

// Course list filtering
function initializeCourseSearch() {
    const courseSearch = document.getElementById('course-search');
    if (courseSearch) {
        courseSearch.addEventListener('keyup', function() {
            const searchTerm = this.value.toLowerCase();
            const courseCards = document.querySelectorAll('.course-card');
            
            courseCards.forEach(function(card) {
                const title = card.querySelector('.course-card-title').textContent.toLowerCase();
                const description = card.querySelector('.course-card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || description.includes(searchTerm)) {
                    card.closest('.col-md-6').style.display = 'block';
                } else {
                    card.closest('.col-md-6').style.display = 'none';
                }
            });
        });
    }
}

// Initialize smooth scrolling for anchor links
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                e.preventDefault();
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Handle cookie consent banner
function initializeCookieConsent() {
    const cookieConsentBanner = document.querySelector('.cookie-consent-banner');
    if (cookieConsentBanner) {
        const acceptButton = cookieConsentBanner.querySelector('.accept-cookies');
        const rejectButton = cookieConsentBanner.querySelector('.reject-cookies');
        
        if (acceptButton) {
            acceptButton.addEventListener('click', function() {
                document.cookie = "cookie_consent=accepted; max-age=" + (365 * 24 * 60 * 60) + "; path=/";
                cookieConsentBanner.style.display = 'none';
            });
        }
        
        if (rejectButton) {
            rejectButton.addEventListener('click', function() {
                document.cookie = "cookie_consent=rejected; max-age=" + (365 * 24 * 60 * 60) + "; path=/";
                cookieConsentBanner.style.display = 'none';
            });
        }
    }
}

// Auto-dismiss alerts
function initializeAlertAutoDismiss() {
    const alerts = document.querySelectorAll('.alert:not(.alert-important)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

// Highlight active links in navigation
function highlightActiveLinks() {
    const currentLocation = window.location.pathname;
    
    // Sidebar navigation
    const navLinks = document.querySelectorAll('.list-group-item');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
    
    // Main navigation
    const mainNavLinks = document.querySelectorAll('.navbar-nav .nav-link');
    mainNavLinks.forEach(function(link) {
        const href = link.getAttribute('href');
        if (href === currentLocation || 
            (href !== '/' && currentLocation.startsWith(href))) {
            link.classList.add('active');
        }
    });
}

// Set up form validation
function setupFormValidation() {
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
}

// Initialize countdown timers for assignments
function initializeAssignmentCountdowns() {
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
}

// Set up delete confirmation dialogs
function setupDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                event.preventDefault();
            }
        });
    });
}

// Scroll animations for elements (revealing on scroll)
function initializeScrollAnimations() {
    // Add fade-in class to animate elements on scroll
    const animatedElements = document.querySelectorAll('.card, .hero-feature-item, .category-title, .course-card');
    
    if (!('IntersectionObserver' in window)) {
        // Fallback for browsers that don't support Intersection Observer
        animatedElements.forEach(el => el.style.opacity = '1');
        return;
    }
    
    const observerOptions = {
        root: null, // viewport
        threshold: 0.1, // trigger when 10% of the element is visible
        rootMargin: '0px 0px -50px 0px' // slight offset (triggers earlier)
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
                
                // Add animation styles
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Prepare elements for animation
    animatedElements.forEach(element => {
        observer.observe(element);
        // Set initial styles
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
    });
}