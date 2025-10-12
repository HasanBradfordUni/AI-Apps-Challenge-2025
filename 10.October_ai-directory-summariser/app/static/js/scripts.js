// Directory AI Summariser JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
    
    // Form validation
    setupFormValidation();
    
    // File upload handling
    setupFileUpload();
    
    // Directory path validation
    setupDirectoryValidation();
    
    // Real-time feedback
    setupRealTimeFeedback();
});

// Initialize application
function initializeApp() {
    console.log('Directory AI Summariser initialized');
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.transition = 'all 0.3s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
    
    // Add loading states to buttons
    const buttons = document.querySelectorAll('.submit-btn, .action-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.type === 'submit') {
                this.dataset.originalText = this.textContent;
                this.textContent = 'Processing...';
                this.disabled = true;
            }
        });
    });
}

// Form validation setup
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const directoryInput = form.querySelector('input[name="directory_path"]');
            const templateFiles = form.querySelector('input[name="template_files"]');
            
            // Validate directory path
            if (directoryInput) {
                const path = directoryInput.value.trim();
                if (!path) {
                    e.preventDefault();
                    showNotification('Please enter a directory path', 'error');
                    return false;
                }
                
                if (!isValidDirectoryPath(path)) {
                    e.preventDefault();
                    showNotification('Please enter a valid directory path', 'error');
                    return false;
                }
            }
            
            // Validate template files
            if (templateFiles && templateFiles.files.length === 0) {
                e.preventDefault();
                showNotification('Please select at least one template file', 'error');
                return false;
            }
        });
    });
}

// Directory path validation
function isValidDirectoryPath(path) {
    // Basic path validation
    if (path.length < 3) return false;
    
    // Windows path validation
    if (path.match(/^[A-Za-z]:\\/)) return true;
    
    // Unix/Linux path validation
    if (path.startsWith('/')) return true;
    
    // Relative path validation
    if (path.startsWith('./') || path.startsWith('../')) return true;
    
    return false;
}

// File upload handling
function setupFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const maxSize = 16 * 1024 * 1024; // 16MB
            const allowedTypes = [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                'application/vnd.ms-powerpoint',
                'text/plain',
                'text/markdown'
            ];
            
            let totalSize = 0;
            let validFiles = 0;
            
            for (let file of files) {
                totalSize += file.size;
                
                if (allowedTypes.includes(file.type) || 
                    file.name.match(/\.(pdf|docx|doc|xlsx|xls|pptx|ppt|txt|md)$/i)) {
                    validFiles++;
                }
            }
            
            // Check total size
            if (totalSize > maxSize) {
                showNotification('Total file size exceeds 16MB limit', 'error');
                input.value = '';
                return;
            }
            
            // Check file types
            if (validFiles !== files.length) {
                showNotification('Some files have unsupported formats', 'warning');
            }
            
            // Show file count
            if (files.length > 0) {
                showNotification(`${files.length} file(s) selected (${formatFileSize(totalSize)})`, 'success');
            }
        });
    });
}

// Directory path validation with real-time feedback
function setupDirectoryValidation() {
    const directoryInputs = document.querySelectorAll('input[name="directory_path"]');
    
    directoryInputs.forEach(input => {
        let timeout;
        
        input.addEventListener('input', function(e) {
            clearTimeout(timeout);
            const path = e.target.value.trim();
            
            // Clear previous validation styles
            input.classList.remove('valid', 'invalid');
            
            if (path.length === 0) return;
            
            timeout = setTimeout(() => {
                if (isValidDirectoryPath(path)) {
                    input.classList.add('valid');
                    // Optionally check if directory exists (if you want to add server-side validation)
                    // checkDirectoryExists(path);
                } else {
                    input.classList.add('invalid');
                }
            }, 500);
        });
        
        // Add placeholder examples
        input.addEventListener('focus', function() {
            if (!this.value) {
                const examples = [
                    'C:\\Users\\Username\\Documents',
                    'C:\\Projects\\MyApp',
                    '/home/user/documents',
                    './my-project'
                ];
                const randomExample = examples[Math.floor(Math.random() * examples.length)];
                this.placeholder = `e.g., ${randomExample}`;
            }
        });
    });
}

// Real-time feedback setup
function setupRealTimeFeedback() {
    // Add progress indicators for long operations
    const analyzeButtons = document.querySelectorAll('button[type="submit"]');
    
    analyzeButtons.forEach(button => {
        const form = button.closest('form');
        if (form && form.action.includes('analyze_directory')) {
            form.addEventListener('submit', function() {
                showProgressIndicator('Analyzing directory structure...');
            });
        }
        
        if (form && form.action.includes('upload_templates')) {
            form.addEventListener('submit', function() {
                showProgressIndicator('Uploading and processing templates...');
            });
        }
    });
}

// Progress indicator
function showProgressIndicator(message) {
    const progressHTML = `
        <div id="progressIndicator" class="progress-overlay">
            <div class="progress-content">
                <div class="progress-spinner"></div>
                <p class="progress-message">${message}</p>
                <div class="progress-details">
                    <p>This may take a few moments depending on directory size...</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', progressHTML);
}

// Template matching functionality
function performTemplateMatching() {
    const button = event.target;
    const originalText = button.textContent;
    
    button.textContent = 'Finding Matches...';
    button.disabled = true;
    
    fetch('/template_matching', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        button.textContent = originalText;
        button.disabled = false;
        
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                window.location.href = '/view_analysis';
            }, 1000);
        } else {
            showNotification(data.error || 'Template matching failed', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.textContent = originalText;
        button.disabled = false;
        showNotification('Error performing template matching', 'error');
    });
}

// Export functionality
function exportAnalysis(format) {
    showNotification('Preparing export...', 'info');
    
    fetch(`/export_analysis/${format}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (response.ok) {
            const filename = response.headers.get('Content-Disposition')
                ?.split('filename=')[1]?.replace(/"/g, '') || 
                `directory_analysis.${format}`;
            
            return response.blob().then(blob => {
                downloadFile(blob, filename);
                showNotification('Export completed successfully', 'success');
            });
        } else {
            throw new Error('Export failed');
        }
    })
    .catch(error => {
        console.error('Export error:', error);
        showNotification('Export failed. Please try again.', 'error');
    });
}

// Download file helper
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Delete template confirmation
function confirmDeleteTemplate(templateId) {
    if (confirm('Are you sure you want to delete this template?')) {
        const form = document.querySelector(`form[action*="delete_template/${templateId}"]`);
        if (form) {
            const button = form.querySelector('button[type="submit"]');
            button.textContent = 'Deleting...';
            button.disabled = true;
            form.submit();
        }
    }
}

// Quick directory suggestions
function suggestDirectories() {
    const input = event.target;
    const suggestions = [
        'C:\\Users\\' + (window.navigator.userAgent.includes('Windows') ? 'Username' : 'user') + '\\Documents',
        'C:\\Users\\' + (window.navigator.userAgent.includes('Windows') ? 'Username' : 'user') + '\\Desktop',
        'C:\\Users\\' + (window.navigator.userAgent.includes('Windows') ? 'Username' : 'user') + '\\Downloads',
        '/home/user/documents',
        '/home/user/projects',
        './projects',
        '../data'
    ];
    
    const dropdown = createSuggestionsDropdown(suggestions);
    positionDropdown(dropdown, input);
}

// Create suggestions dropdown
function createSuggestionsDropdown(suggestions) {
    // Remove existing dropdown
    const existing = document.getElementById('directoryDropdown');
    if (existing) existing.remove();
    
    const dropdown = document.createElement('div');
    dropdown.id = 'directoryDropdown';
    dropdown.className = 'directory-suggestions';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = suggestion;
        item.addEventListener('click', function() {
            const input = document.querySelector('input[name="directory_path"]');
            input.value = suggestion;
            dropdown.remove();
        });
        dropdown.appendChild(item);
    });
    
    document.body.appendChild(dropdown);
    
    // Close dropdown when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeDropdown(e) {
            if (!dropdown.contains(e.target)) {
                dropdown.remove();
                document.removeEventListener('click', closeDropdown);
            }
        });
    }, 100);
    
    return dropdown;
}

// Position dropdown relative to input
function positionDropdown(dropdown, input) {
    const rect = input.getBoundingClientRect();
    dropdown.style.position = 'absolute';
    dropdown.style.top = (rect.bottom + window.scrollY) + 'px';
    dropdown.style.left = rect.left + 'px';
    dropdown.style.width = rect.width + 'px';
}

// Check directory existence (optional server-side validation)
function checkDirectoryExists(path) {
    fetch('/api/check_directory', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ path: path })
    })
    .then(response => response.json())
    .then(data => {
        const input = document.querySelector('input[name="directory_path"]');
        if (data.exists) {
            input.classList.add('exists');
            input.classList.remove('not-exists');
        } else {
            input.classList.add('not-exists');
            input.classList.remove('exists');
        }
    })
    .catch(error => {
        console.error('Directory check error:', error);
    });
}

// Show notification system
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications of the same type
    const existing = document.querySelectorAll(`.notification-${type}`);
    existing.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.transition = 'all 0.3s ease';
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

// Get notification icon based on type
function getNotificationIcon(type) {
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

// Format file size helper
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Copy analysis results to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(function(err) {
        console.error('Copy failed:', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Add copy buttons to analysis results
document.addEventListener('DOMContentLoaded', function() {
    const analysisContent = document.querySelectorAll('.summary-content, .ai-insights');
    analysisContent.forEach(content => {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '📋 Copy';
        copyBtn.onclick = () => copyToClipboard(content.textContent);
        content.parentNode.insertBefore(copyBtn, content.nextSibling);
    });
});

// Initialize tooltips for better UX
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = e.target.dataset.tooltip;
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) tooltip.remove();
}

// Initialize tooltips on page load
document.addEventListener('DOMContentLoaded', initializeTooltips);

// Handle page unload to clean up
window.addEventListener('beforeunload', function() {
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) progressIndicator.remove();
});