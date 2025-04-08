// Main JavaScript file for AI-powered LMS Platform

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
    
    // Initialize Neural Network Animation
    initNeuralNetwork();
    
    // Initialize typing effect
    initTypingEffect();
    
    // Initialize parallax effect
    initParallaxEffect();
    
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

// Neural Network Animation
function initNeuralNetwork() {
    const neuralNetwork = document.querySelector('.neural-network');
    if (!neuralNetwork) return;
    
    // Create nodes
    const nodeCount = 15;
    for (let i = 0; i < nodeCount; i++) {
        const node = document.createElement('div');
        node.className = 'neural-node';
        
        // Random position
        const top = Math.random() * 100;
        const left = Math.random() * 100;
        
        node.style.top = `${top}%`;
        node.style.left = `${left}%`;
        
        // Random animation delay
        node.style.animationDelay = `${Math.random() * 2}s`;
        
        neuralNetwork.appendChild(node);
    }
    
    // Create paths between random nodes
    const pathCount = 20;
    const nodes = neuralNetwork.querySelectorAll('.neural-node');
    
    for (let i = 0; i < pathCount; i++) {
        const path = document.createElement('div');
        path.className = 'neural-path';
        
        // Select two random nodes to connect
        const nodeIndex1 = Math.floor(Math.random() * nodes.length);
        let nodeIndex2 = Math.floor(Math.random() * nodes.length);
        
        // Ensure we don't connect to the same node
        while (nodeIndex2 === nodeIndex1) {
            nodeIndex2 = Math.floor(Math.random() * nodes.length);
        }
        
        const node1 = nodes[nodeIndex1];
        const node2 = nodes[nodeIndex2];
        
        // Get node positions
        const node1Rect = node1.getBoundingClientRect();
        const node2Rect = node2.getBoundingClientRect();
        const networkRect = neuralNetwork.getBoundingClientRect();
        
        // Calculate relative positions
        const x1 = (node1Rect.left + node1Rect.width/2) - networkRect.left;
        const y1 = (node1Rect.top + node1Rect.height/2) - networkRect.top;
        const x2 = (node2Rect.left + node2Rect.width/2) - networkRect.left;
        const y2 = (node2Rect.top + node2Rect.height/2) - networkRect.top;
        
        // Calculate path length and angle
        const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        
        // Set path properties
        path.style.width = `${length}px`;
        path.style.left = `${x1}px`;
        path.style.top = `${y1}px`;
        path.style.transform = `rotate(${angle}deg)`;
        path.style.animationDelay = `${Math.random() * 4}s`;
        
        neuralNetwork.appendChild(path);
    }
}

// Typing effect for AI headings
function initTypingEffect() {
    const typingElements = document.querySelectorAll('.ai-typing');
    
    typingElements.forEach(function(element) {
        const text = element.textContent;
        element.textContent = '';
        element.style.borderRight = '0.15em solid var(--accent-color)';
        element.style.display = 'inline-block';
        element.style.animation = 'blink-caret 0.75s step-end infinite';
        
        let i = 0;
        const typeSpeed = element.dataset.typeSpeed || 50;
        
        function typeWriter() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, typeSpeed);
            } else {
                // Remove cursor once typing is complete
                setTimeout(function() {
                    element.style.borderRight = 'none';
                    element.style.animation = 'none';
                }, 1500);
            }
        }
        
        // Add keyframe animation for cursor
        if (!document.querySelector('#typing-animation-style')) {
            const style = document.createElement('style');
            style.id = 'typing-animation-style';
            style.textContent = `
                @keyframes blink-caret {
                    from, to { border-color: transparent }
                    50% { border-color: var(--accent-color) }
                }
            `;
            document.head.appendChild(style);
        }
        
        // Start typing with a slight delay
        setTimeout(typeWriter, 500);
    });
}

// Parallax effect for AI hero section
function initParallaxEffect() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    if (parallaxElements.length > 0) {
        window.addEventListener('mousemove', function(e) {
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            
            parallaxElements.forEach(function(element) {
                const speed = element.dataset.speed || 0.05;
                const x = (window.innerWidth / 2 - mouseX) * speed;
                const y = (window.innerHeight / 2 - mouseY) * speed;
                
                element.style.transform = `translateX(${x}px) translateY(${y}px)`;
            });
        });
    }
}