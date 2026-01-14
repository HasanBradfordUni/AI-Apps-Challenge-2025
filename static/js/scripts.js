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

// Global variables
let currentMode = 'general';
let suggestedAppId = null;
let chatHistory = [];

// Get data from window object (passed from HTML template)
const PROMPT_MODES = window.PROMPT_MODES || {};
const AVAILABLE_APPS = window.AVAILABLE_APPS || {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chatbot initialized');
    
    // Load chat history from localStorage
    loadChatHistory();
    
    // Setup Enter key to send message
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Update mode description
    updateModeDescription();
});

// Change prompt mode - FIXED
function changeMode() {
    const modeSelect = document.getElementById('promptMode');
    currentMode = modeSelect.value;
    updateModeDescription();
    
    // Add system message about mode change
    const mode = PROMPT_MODES[currentMode];
    if (mode) {
        addSystemMessage(`Switched to ${mode.name} mode`);
    }
}

// Update mode description - FIXED
function updateModeDescription() {
    const modeDesc = document.getElementById('modeDescription');
    const mode = PROMPT_MODES[currentMode];
    
    if (modeDesc && mode) {
        modeDesc.textContent = mode.description;
    }
}

// Send message to chatbot
async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message) {
        showNotification('Please enter a message', 'warning');
        return;
    }
    
    // Add user message to chat
    addMessage('user', message);
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Disable send button
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                mode: currentMode
            })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        if (data.error) {
            addMessage('error', data.error);
            showNotification('Error: ' + data.error, 'error');
        } else {
            // Add bot response
            addMessage('bot', data.response);
            
            // Check for app suggestion
            if (data.app_suggestion) {
                showAppSuggestion(data.app_suggestion);
            }
            
            // Save to history
            saveChatHistory();
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator();
        addMessage('error', 'Failed to send message. Please try again.');
        showNotification('Connection error', 'error');
    } finally {
        // Re-enable send button
        sendButton.disabled = false;
        messageInput.focus();
    }
}

// Quick message
function quickMessage(text) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = text;
    sendMessage();
}

// Add message to chat
function addMessage(type, content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    const now = new Date();
    const time = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    let icon = '🤖';
    let sender = 'AI Assistant';
    
    if (type === 'user') {
        icon = '👤';
        sender = 'You';
    } else if (type === 'error') {
        icon = '⚠️';
        sender = 'System';
    }
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${icon} ${sender}:</strong>
            <p>${formatMessage(content)}</p>
        </div>
        <div class="message-time">${time}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Add to history
    chatHistory.push({
        type: type,
        content: content,
        timestamp: now.toISOString()
    });
}

// Add system message
function addSystemMessage(content) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    messageDiv.style.textAlign = 'center';
    messageDiv.style.color = '#FFD700';
    messageDiv.style.fontStyle = 'italic';
    messageDiv.style.padding = '10px';
    
    messageDiv.innerHTML = `<p>ℹ️ ${content}</p>`;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Format message (handle markdown-like formatting)
function formatMessage(content) {
    // Convert **bold** to <strong>
    content = content.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    content = content.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Convert line breaks
    content = content.replace(/\n/g, '<br>');
    
    // Convert URLs to links
    content = content.replace(
        /(https?:\/\/[^\s]+)/g,
        '<a href="$1" target="_blank" style="color: #FFD700;">$1</a>'
    );
    
    return content;
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message bot-message';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <strong>🤖 AI Assistant is typing</strong>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Show app suggestion
function showAppSuggestion(suggestion) {
    const modal = document.getElementById('appSuggestionModal');
    const suggestedAppDiv = document.getElementById('suggestedApp');
    
    suggestedAppId = suggestion.app_id;
    
    suggestedAppDiv.innerHTML = `
        <h4>${suggestion.app_name}</h4>
        <p>${suggestion.description}</p>
        <p style="margin-top: 10px;">
            <strong>Confidence:</strong> ${Math.round(suggestion.confidence * 100)}%
        </p>
    `;
    
    modal.style.display = 'flex';
}

// Suggest app (from sidebar) - FIXED
function suggestApp(appId) {
    const app = AVAILABLE_APPS[appId];
    
    if (app) {
        showAppSuggestion({
            app_id: appId,
            app_name: app.name,
            description: app.description,
            confidence: 1.0
        });
    }
}

// Go to app
function goToApp() {
    if (suggestedAppId) {
        // Open app interface based on app_id
        openAppInterface(suggestedAppId);
        closeModal();
    }
}

// Continue chat
function continueChat() {
    closeModal();
    document.getElementById('messageInput').focus();
}

// Close modal
function closeModal() {
    document.getElementById('appSuggestionModal').style.display = 'none';
    suggestedAppId = null;
}

// Open app interface - FIXED
async function openAppInterface(appId) {
    const app = AVAILABLE_APPS[appId];
    
    if (!app) return;
    
    // Create modal for app interface
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.id = 'appInterfaceModal';
    modal.style.display = 'flex';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <div class="modal-header">
                <h3>${app.icon} ${app.name}</h3>
                <button onclick="closeAppInterface()" class="close-btn">&times;</button>
            </div>
            <div class="modal-body" id="appInterfaceBody">
                ${getAppInterface(appId)}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Get app interface HTML
function getAppInterface(appId) {
    const interfaces = {
        'document_search': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Search Query</label>
                    <input type="text" id="searchQuery" class="form-control" placeholder="Enter search query...">
                </div>
                <div class="form-group">
                    <label>Directory</label>
                    <input type="text" id="searchDirectory" class="form-control" value="default">
                </div>
                <button onclick="executeDocumentSearch()" class="primary-btn">Search</button>
                <div id="searchResults" class="results-area"></div>
            </div>
        `,
        'cover_letter_writer': `
            <div class="app-interface">
                <div class="form-group">
                    <label>CV/Resume Text</label>
                    <textarea id="cvText" rows="5" class="form-control" placeholder="Paste your CV text..."></textarea>
                </div>
                <div class="form-group">
                    <label>Job Description</label>
                    <textarea id="jobDescription" rows="5" class="form-control" placeholder="Paste job description..."></textarea>
                </div>
                <div class="form-group">
                    <label>Tone</label>
                    <select id="toneSelect" class="form-control">
                        <option value="professional">Professional</option>
                        <option value="friendly">Friendly</option>
                        <option value="formal">Formal</option>
                    </select>
                </div>
                <button onclick="generateCoverLetter()" class="primary-btn">Generate Cover Letter</button>
                <div id="coverLetterResult" class="results-area"></div>
            </div>
        `,
        'work_hours_calculator': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Contracted Hours</label>
                    <input type="number" id="contractedHours" class="form-control" placeholder="e.g., 40">
                </div>
                <div class="form-group">
                    <label>Time Frame</label>
                    <select id="timeFrame" class="form-control">
                        <option value="week">Per Week</option>
                        <option value="month">Per Month</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Work Description</label>
                    <textarea id="workDescription" rows="4" class="form-control" placeholder="Describe your work hours..."></textarea>
                </div>
                <button onclick="calculateWorkHours()" class="primary-btn">Calculate</button>
                <div id="workHoursResult" class="results-area"></div>
            </div>
        `,
        'coding_assistant': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Code</label>
                    <textarea id="codeInput" rows="10" class="form-control" placeholder="Paste your code here..." style="font-family: monospace;"></textarea>
                </div>
                <div class="form-group">
                    <label>Language</label>
                    <select id="languageSelect" class="form-control">
                        <option value="python">Python</option>
                        <option value="javascript">JavaScript</option>
                        <option value="java">Java</option>
                        <option value="csharp">C#</option>
                        <option value="cpp">C++</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Request Type</label>
                    <select id="requestType" class="form-control">
                        <option value="suggestion">Code Suggestions</option>
                        <option value="explain">Explain Code</option>
                        <option value="documentation">Generate Documentation</option>
                        <option value="quality_analysis">Quality Analysis</option>
                        <option value="test_cases">Generate Tests</option>
                    </select>
                </div>
                <button onclick="getCodeAssistance()" class="primary-btn">Get Assistance</button>
                <div id="codeAssistanceResult" class="results-area"></div>
            </div>
        `
    };
    
    return interfaces[appId] || '<p>App interface not yet implemented. Please use the main chat to interact with this feature.</p>';
}

// Close app interface
function closeAppInterface() {
    const modal = document.getElementById('appInterfaceModal');
    if (modal) {
        modal.remove();
    }
}

// API Functions

// Document Search
async function executeDocumentSearch() {
    const query = document.getElementById('searchQuery').value;
    const directory = document.getElementById('searchDirectory').value;
    const resultsDiv = document.getElementById('searchResults');
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="spinner"></div> Searching...';
    
    try {
        const response = await fetch('/api/search-documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, directory })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultsDiv.innerHTML = `
                <h4>Search Results:</h4>
                <div class="results-list">${formatSearchResults(data.results)}</div>
                <h4 style="margin-top: 20px;">AI Summary:</h4>
                <div class="ai-summary">${data.ai_summary}</div>
            `;
            showNotification('Search completed successfully', 'success');
        } else {
            resultsDiv.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
            showNotification(data.error, 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        showNotification('Search failed', 'error');
    }
}

// Format search results
function formatSearchResults(results) {
    if (!results || results.length === 0) {
        return '<p>No results found</p>';
    }
    
    return results.map(result => `
        <div class="result-item" style="padding: 10px; margin: 10px 0; background: rgba(255,255,255,0.1); border-radius: 5px;">
            <strong>${result.filename || result.title || 'Document'}</strong>
            <p>${result.content || result.excerpt || 'No preview available'}</p>
        </div>
    `).join('');
}

// Generate Cover Letter
async function generateCoverLetter() {
    const cvText = document.getElementById('cvText').value;
    const jobDescription = document.getElementById('jobDescription').value;
    const tone = document.getElementById('toneSelect').value;
    const resultsDiv = document.getElementById('coverLetterResult');
    
    if (!cvText || !jobDescription) {
        showNotification('Please fill in both CV text and job description', 'warning');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="spinner"></div> Generating cover letter...';
    
    try {
        const response = await fetch('/api/generate-cover-letter', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ cv_text: cvText, job_description: jobDescription, tone })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const escapedLetter = escapeHtml(data.cover_letter);
            resultsDiv.innerHTML = `
                <h4>Generated Cover Letter:</h4>
                <div class="cover-letter-content" style="white-space: pre-wrap; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                    ${data.cover_letter}
                </div>
                <button onclick="copyToClipboard(\`${escapedLetter}\`)" class="secondary-btn" style="margin-top: 10px;">
                    📋 Copy to Clipboard
                </button>
            `;
            showNotification('Cover letter generated successfully', 'success');
        } else {
            resultsDiv.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
            showNotification(data.error, 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        showNotification('Generation failed', 'error');
    }
}

// Calculate Work Hours
async function calculateWorkHours() {
    const contractedHours = document.getElementById('contractedHours').value;
    const timeFrame = document.getElementById('timeFrame').value;
    const workDescription = document.getElementById('workDescription').value;
    const resultsDiv = document.getElementById('workHoursResult');
    
    resultsDiv.innerHTML = '<div class="spinner"></div> Calculating...';
    
    try {
        const response = await fetch('/api/calculate-hours', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contracted_hours: contractedHours,
                time_frame: timeFrame,
                work_hours_description: workDescription
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultsDiv.innerHTML = `
                <h4>Analysis:</h4>
                <div class="summary-content" style="padding: 15px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                    ${data.summary}
                </div>
            `;
            showNotification('Calculation completed', 'success');
        } else {
            resultsDiv.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
            showNotification(data.error, 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        showNotification('Calculation failed', 'error');
    }
}

// Get Code Assistance
async function getCodeAssistance() {
    const code = document.getElementById('codeInput').value;
    const language = document.getElementById('languageSelect').value;
    const requestType = document.getElementById('requestType').value;
    const resultsDiv = document.getElementById('codeAssistanceResult');
    
    if (!code) {
        showNotification('Please enter some code', 'warning');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="spinner"></div> Analyzing code...';
    
    try {
        const response = await fetch('/api/code-assistance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: code,
                language: language,
                request_type: requestType
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultsDiv.innerHTML = `
                <h4>Assistance (${data.assistance_type}):</h4>
                <div class="code-assistance-content" style="white-space: pre-wrap; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 5px; font-family: monospace;">
                    ${escapeHtml(data.assistance)}
                </div>
            `;
            showNotification('Analysis completed', 'success');
        } else {
            resultsDiv.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
            showNotification(data.error, 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        showNotification('Analysis failed', 'error');
    }
}

// Chat actions
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatHistory = [];
        localStorage.removeItem('chatHistory');
        
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <strong>🤖 AI Assistant:</strong>
                    <p>Chat cleared. How can I help you today?</p>
                </div>
                <div class="message-time">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
            </div>
        `;
        
        showNotification('Chat history cleared', 'success');
    }
}

function exportChat() {
    if (chatHistory.length === 0) {
        showNotification('No chat history to export', 'warning');
        return;
    }
    
    const exportData = {
        exported_at: new Date().toISOString(),
        mode: currentMode,
        messages: chatHistory
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-export-${Date.now()}.json`;
    a.click();
    
    showNotification('Chat exported successfully', 'success');
}

function showHelp() {
    const helpMessage = `
        <h4>How to use the AI Chatbot Hub:</h4>
        <ul style="text-align: left;">
            <li>Select a prompt mode from the dropdown to change the AI's behavior</li>
            <li>Type your message and press Enter or click the send button</li>
            <li>Click on Quick Apps to access specific AI tools</li>
            <li>Use quick suggestions for common queries</li>
            <li>The AI will suggest relevant apps based on your questions</li>
        </ul>
    `;
    
    addMessage('bot', helpMessage);
}

// Helper functions
function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    } catch (e) {
        console.error('Failed to save chat history:', e);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            chatHistory = JSON.parse(saved);
        }
    } catch (e) {
        console.error('Failed to load chat history:', e);
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Add CSS for form controls and app interfaces
const appInterfaceStyle = document.createElement('style');
appInterfaceStyle.textContent = `
    .form-control {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.3);
        color: #fff;
        margin-bottom: 15px;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-group label {
        display: block;
        margin-bottom: 8px;
        color: #FFD700;
        font-weight: bold;
    }
    .results-area {
        margin-top: 20px;
        padding: 15px;
        background: rgba(0,0,0,0.3);
        border-radius: 8px;
        min-height: 100px;
    }
    .app-interface {
        color: #fff;
    }
    .spinner {
        border: 3px solid rgba(255,255,255,0.3);
        border-top: 3px solid #FFD700;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        animation: spin 1s linear infinite;
        display: inline-block;
        margin-right: 10px;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(appInterfaceStyle);