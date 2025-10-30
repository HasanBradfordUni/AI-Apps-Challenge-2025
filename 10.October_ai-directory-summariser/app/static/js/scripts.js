// Directory AI Summariser JavaScript Functions

// Enhanced logging for debugging
const DEBUG = true; // Set to false in production

function debugLog(message, data = null) {
    if (DEBUG) {
        console.log(`[DEBUG] ${new Date().toISOString()} - ${message}`);
        if (data) {
            console.log('[DEBUG] Data:', data);
        }
    }
}

function errorLog(message, error = null) {
    console.error(`[ERROR] ${new Date().toISOString()} - ${message}`);
    if (error) {
        console.error('[ERROR] Details:', error);
    }
}

function infoLog(message, data = null) {
    console.info(`[INFO] ${new Date().toISOString()} - ${message}`);
    if (data) {
        console.info('[INFO] Data:', data);
    }
}

// SINGLE DOMContentLoaded event listener
document.addEventListener('DOMContentLoaded', function() {
    debugLog('DOM Content Loaded - Starting Directory AI Summariser initialization');
    
    // Initialize the application
    initializeApp();
    
    // Form validation and submission handling (COMBINED)
    setupFormValidation();
    
    // File upload handling
    setupFileUpload();
    
    // Directory path validation
    setupDirectoryValidation();
    
    // Real-time feedback
    setupRealTimeFeedback();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Check for flash messages
    checkForFlashMessages();
    
    debugLog('Directory AI Summariser initialization complete');
});

// Initialize application
function initializeApp() {
    debugLog('Initializing application components');
    
    // Auto-dismiss flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    debugLog(`Found ${flashMessages.length} flash messages`);
    
    flashMessages.forEach((message, index) => {
        debugLog(`Setting up auto-dismiss for flash message ${index + 1}`);
        setTimeout(() => {
            message.style.transition = 'all 0.3s ease';
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                message.remove();
                debugLog(`Flash message ${index + 1} removed`);
            }, 300);
        }, 5000);
    });
    
    infoLog('Application initialization completed');
}

// Form validation setup - ENHANCED WITH DIRECTORY ANALYSIS HANDLING
function setupFormValidation() {
    debugLog('Setting up form validation');
    
    const forms = document.querySelectorAll('form');
    debugLog(`Found ${forms.length} forms to validate`);
    
    forms.forEach((form, index) => {
        debugLog(`Setting up validation for form ${index + 1}: ${form.action}`);
        
        // Check if already has event listener to prevent duplicates
        if (form.dataset.listenerAdded === 'true') {
            debugLog(`Form ${index + 1} already has event listener, skipping`);
            return;
        }
        
        // Mark as having listener
        form.dataset.listenerAdded = 'true';
        
        form.addEventListener('submit', function(e) {
            const formData = new FormData(this);
            const formDataObj = Object.fromEntries(formData.entries());
            
            debugLog(`Form ${index + 1} submission attempt`, formDataObj);
            
            const directoryInput = this.querySelector('input[name="directory_path"]');
            const templateFiles = this.querySelector('input[name="template_files"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            // Directory Analysis Form Handling
            if (this.action.includes('analyze_directory')) {
                debugLog('Directory analysis form submission detected');
                
                const path = directoryInput ? directoryInput.value.trim() : '';
                
                debugLog(`Directory path value: "${path}"`);
                debugLog(`Directory input element:`, directoryInput);
                
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
                
                // Show loading state for directory analysis
                if (submitBtn) {
                    submitBtn.dataset.originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Analyzing...';
                    submitBtn.disabled = true;
                }
                
                if (directoryInput) {
                    directoryInput.readOnly = true;  // ✅ Use readOnly instead of disabled
                    directoryInput.style.opacity = '0.6';
                    directoryInput.style.pointerEvents = 'none';  // Prevent clicking
                }
                
                // Show progress indicator
                showProgressIndicator('Starting directory analysis...');
                
                // Setup progress messages
                setupProgressMessages();
                
                debugLog('Directory analysis form submitted', { path: path });
                infoLog('Directory analysis started', { path: path, timestamp: new Date().toISOString() });
                
                // Let the form submit normally
                return true;
            }
            
            // Template Upload Form Handling
            else if (this.action.includes('upload_templates')) {
                if (templateFiles && templateFiles.files.length === 0) {
                    e.preventDefault();
                    showNotification('Please select at least one template file', 'error');
                    return false;
                }
                
                if (submitBtn) {
                    submitBtn.dataset.originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Uploading...';
                    submitBtn.disabled = true;
                }
                
                showProgressIndicator('Uploading and processing templates...');
                debugLog('Template upload form submitted');
            }
            
            // General Form Validation
            else {
                if (submitBtn) {
                    submitBtn.dataset.originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Processing...';
                    submitBtn.disabled = true;
                }
            }
            
            infoLog(`Form ${index + 1} validation passed, submitting`);
        });
    });
}

// Setup progress messages for directory analysis
function setupProgressMessages() {
    let progressStep = 0;
    const progressMessages = [
        'Scanning directory structure...',
        'Analyzing file contents...',
        'Generating AI insights...',
        'Saving results...'
    ];
    
    const progressInterval = setInterval(() => {
        if (progressStep < progressMessages.length) {
            updateProgressMessage(progressMessages[progressStep]);
            progressStep++;
        } else {
            clearInterval(progressInterval);
        }
    }, 2000);
    
    // Store interval ID for cleanup
    window.analysisProgressInterval = progressInterval;
}

// Update progress message
function updateProgressMessage(message) {
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) {
        const messageElement = progressIndicator.querySelector('.progress-message');
        if (messageElement) {
            messageElement.textContent = message;
            debugLog('Progress message updated:', message);
        }
    }
}

// Directory path validation
function isValidDirectoryPath(path) {
    debugLog(`Checking path validity: "${path}"`);
    
    // Basic path validation
    if (path.length < 3) {
        debugLog('Path too short');
        return false;
    }
    
    // Windows path validation
    if (path.match(/^[A-Za-z]:\\/)) {
        debugLog('Valid Windows path format detected');
        return true;
    }
    
    // Unix/Linux path validation
    if (path.startsWith('/')) {
        debugLog('Valid Unix/Linux path format detected');
        return true;
    }
    
    // Relative path validation
    if (path.startsWith('./') || path.startsWith('../')) {
        debugLog('Valid relative path format detected');
        return true;
    }
    
    debugLog('No valid path format detected');
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
    debugLog('Setting up real-time feedback systems');
    
    // Handle page navigation back
    window.addEventListener('pageshow', function(e) {
        if (e.persisted) {
            debugLog('Page restored from cache, resetting form state');
            resetFormState();
        }
    });
}

// Reset form state
function resetFormState() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const inputs = form.querySelectorAll('input');
        
        if (submitBtn && submitBtn.dataset.originalText) {
            submitBtn.textContent = submitBtn.dataset.originalText;
            submitBtn.disabled = false;
        }
        
        inputs.forEach(input => {
            input.disabled = false;
            input.style.opacity = '1';
        });
    });
    
    // Clear progress indicator
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) {
        progressIndicator.remove();
    }
    
    // Clear progress interval
    if (window.analysisProgressInterval) {
        clearInterval(window.analysisProgressInterval);
    }
    
    debugLog('Form state reset');
}

// Check for flash messages
function checkForFlashMessages() {
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message, [class*="flash"], .alert');
        debugLog('Found flash messages:', flashMessages.length);
        
        flashMessages.forEach((msg, index) => {
            debugLog(`Flash message ${index + 1}:`, msg.textContent);
        });
        
        if (flashMessages.length === 0) {
            debugLog('No flash messages found');
        }
    }, 100);
}

// Progress indicator
function showProgressIndicator(message) {
    debugLog(`Showing progress indicator: ${message}`);
    
    // Remove existing progress indicator
    const existing = document.getElementById('progressIndicator');
    if (existing) {
        debugLog('Removing existing progress indicator');
        existing.remove();
    }
    
    const progressHTML = `
        <div id="progressIndicator" class="progress-overlay">
            <div class="progress-content">
                <div class="progress-spinner"></div>
                <p class="progress-message">${message}</p>
                <div class="progress-details">
                    <p>This may take a few moments depending on directory size...</p>
                    <p id="progressTimer">Elapsed time: 0s</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', progressHTML);
    
    // Start timer
    const startTime = Date.now();
    const timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const timerElement = document.getElementById('progressTimer');
        if (timerElement) {
            timerElement.textContent = `Elapsed time: ${elapsed}s`;
        } else {
            clearInterval(timer);
        }
    }, 1000);
    
    infoLog('Progress indicator displayed', { message: message });
}

// Show notification system
function showNotification(message, type = 'info', duration = 5000) {
    debugLog(`Showing notification: ${type} - ${message}`);
    
    // Remove existing notifications of the same type
    const existing = document.querySelectorAll(`.notification-${type}`);
    existing.forEach(notif => {
        debugLog('Removing existing notification of same type');
        notif.remove();
    });
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 15px 20px;
        border-radius: 5px;
        color: white;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        max-width: 400px;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        ${type === 'success' ? 'background-color: #28a745;' : ''}
        ${type === 'error' ? 'background-color: #dc3545;' : ''}
        ${type === 'warning' ? 'background-color: #ffc107; color: #212529;' : ''}
        ${type === 'info' ? 'background-color: #17a2b8;' : ''}
    `;
    
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentElement) {
            debugLog(`Auto-removing notification after ${duration}ms`);
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
    
    infoLog('Notification displayed', { type: type, message: message });
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
    debugLog(`Starting export in format: ${format}`);
    showNotification('Preparing export...', 'info');
    
    fetch(`/export_analysis/${format}`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        debugLog(`Export response received: ${response.status} ${response.statusText}`);
        
        if (response.ok) {
            const filename = response.headers.get('Content-Disposition')
                ?.split('filename=')[1]?.replace(/"/g, '') || 
                `directory_analysis.${format}`;
            
            debugLog(`Export successful, downloading file: ${filename}`);
            
            return response.blob().then(blob => {
                downloadFile(blob, filename);
                showNotification('Export completed successfully', 'success');
                infoLog('Export completed', { format: format, filename: filename });
            });
        } else {
            throw new Error(`Export failed with status: ${response.status}`);
        }
    })
    .catch(error => {
        errorLog('Export failed', error);
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

// Handle page unload to clean up
window.addEventListener('beforeunload', function() {
    debugLog('Page unload detected, cleaning up');
    
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) {
        debugLog('Removing progress indicator on page unload');
        progressIndicator.remove();
    }
    
    // Clear any intervals
    if (window.analysisProgressInterval) {
        clearInterval(window.analysisProgressInterval);
    }
});

// Global error handler
window.addEventListener('error', function(e) {
    errorLog('JavaScript error caught', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error
    });
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
    console.error('[ERROR] Unhandled promise rejection:', e.reason);
});