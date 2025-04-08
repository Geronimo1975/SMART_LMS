// UNI_online main JavaScript file

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Toggle sidebar on mobile devices
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('mobile-visible');
        });
    }

    // Handle notification read status
    const notificationItems = document.querySelectorAll('.notification-item');
    
    notificationItems.forEach(item => {
        item.addEventListener('click', function() {
            const notificationId = this.dataset.notificationId;
            if (notificationId) {
                // Mark notification as read
                fetch(`/dashboard/notifications/${notificationId}/mark-as-read/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                    credentials: 'same-origin',
                })
                .then(response => {
                    if (response.ok) {
                        // Update UI
                        this.classList.remove('unread');
                        this.classList.add('read');
                        
                        // Update notification counter if it exists
                        const counter = document.querySelector('.notification-counter');
                        if (counter) {
                            const count = parseInt(counter.textContent) - 1;
                            counter.textContent = count > 0 ? count : '';
                            if (count <= 0) {
                                counter.style.display = 'none';
                            }
                        }
                    }
                });
            }
        });
    });

    // Helper function to get CSRF cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // File input preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const previewContainer = document.createElement('div');
        previewContainer.className = 'file-preview-container mt-2';
        input.parentNode.insertBefore(previewContainer, input.nextSibling);
        
        input.addEventListener('change', function(e) {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const fileExtension = file.name.split('.').pop().toLowerCase();
                
                // Check if file is an image
                if (['jpg', 'jpeg', 'png', 'gif', 'svg'].includes(fileExtension)) {
                    const img = document.createElement('img');
                    img.className = 'file-preview';
                    img.style.maxWidth = '200px';
                    img.style.maxHeight = '200px';
                    img.src = URL.createObjectURL(file);
                    previewContainer.appendChild(img);
                } else {
                    // Show file name for non-image files
                    const fileInfo = document.createElement('div');
                    fileInfo.className = 'file-info';
                    fileInfo.innerHTML = `<i class="fa fa-file"></i> ${file.name}`;
                    previewContainer.appendChild(fileInfo);
                }
            }
        });
    });
});
