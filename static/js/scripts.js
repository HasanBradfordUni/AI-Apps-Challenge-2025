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
    
    if (!message && uploadedFiles.length === 0) {
        showNotification('Please enter a message or upload files', 'warning');
        return;
    }
    
    // Create form data if files are present
    if (uploadedFiles.length > 0) {
        const formData = new FormData();
        formData.append('message', message);
        formData.append('mode', currentMode);
        
        uploadedFiles.forEach((file, index) => {
            formData.append(`file_${index}`, file);
        });
        
        formData.append('file_count', uploadedFiles.length);
        
        // Add message to chat
        addMessage('user', message + ` [${uploadedFiles.length} file(s) attached]`);
        
        // Clear input and files
        messageInput.value = '';
        uploadedFiles = [];
        document.getElementById('fileList').innerHTML = '';
        updateFilePreview();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Disable send button
        const sendButton = document.getElementById('sendButton');
        sendButton.disabled = true;
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (data.error) {
                addMessage('error', data.error);
                showNotification('Error: ' + data.error, 'error');
            } else {
                addMessage('bot', data.response);
                if (data.app_suggestion) {
                    showAppSuggestion(data.app_suggestion);
                }
                saveChatHistory();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('error', 'Failed to send message. Please try again.');
            showNotification('Connection error', 'error');
        } finally {
            sendButton.disabled = false;
            messageInput.focus();
        }
    } else {
        // Call original sendMessage if no files
        await originalSendMessage();
    }
};

// Voice Recording Variables
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let recognition = null;

// File Upload Variables
let uploadedFiles = [];
const MAX_FILES = 10;
const MAX_TOTAL_SIZE = 1024 * 1024 * 1024; // 1GB in bytes

// Initialize Speech Recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        
        recognition.onresult = function(event) {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            const transcriptDiv = document.getElementById('transcriptText');
            transcriptDiv.innerHTML = `
                <div style="color: #fff;">${finalTranscript}</div>
                <div style="color: #aaa; font-style: italic;">${interimTranscript}</div>
            `;
            
            // Update message input with final transcript
            if (finalTranscript) {
                const messageInput = document.getElementById('messageInput');
                messageInput.value = (messageInput.value + ' ' + finalTranscript).trim();
            }
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            showNotification('Speech recognition error: ' + event.error, 'error');
            stopVoiceRecording();
        };
    } else {
        console.warn('Speech recognition not supported');
    }
}

// Toggle voice recording
async function toggleVoiceRecording() {
    if (isRecording) {
        stopVoiceRecording();
    } else {
        startVoiceRecording();
    }
}

// Start voice recording
async function startVoiceRecording() {
    try {
        // Initialize speech recognition if not already done
        if (!recognition) {
            initSpeechRecognition();
        }
        
        if (!recognition) {
            showNotification('Speech recognition not supported in this browser', 'error');
            return;
        }
        
        // Start recording
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            // Could upload audio blob to server for processing if needed
        };
        
        mediaRecorder.start();
        recognition.start();
        isRecording = true;
        
        // Update UI
        const voiceBtn = document.getElementById('voiceBtn');
        voiceBtn.innerHTML = '🔴';
        voiceBtn.title = 'Recording... Click to stop';
        
        const transcriptDiv = document.getElementById('voiceTranscript');
        transcriptDiv.style.display = 'block';
        
        showNotification('Voice recording started', 'success');
        
    } catch (error) {
        console.error('Error starting voice recording:', error);
        showNotification('Could not access microphone', 'error');
    }
}

// Stop voice recording
function stopVoiceRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    if (recognition) {
        recognition.stop();
    }
    
    isRecording = false;
    
    // Update UI
    const voiceBtn = document.getElementById('voiceBtn');
    voiceBtn.innerHTML = '🎤';
    voiceBtn.title = 'Voice input';
    
    const transcriptDiv = document.getElementById('voiceTranscript');
    transcriptDiv.style.display = 'none';
    
    showNotification('Voice recording stopped', 'info');
}

// Open file upload dialog
function openFileUpload() {
    const fileInput = document.getElementById('fileInput');
    fileInput.click();
}

// Handle file selection
function handleFileSelection(event) {
    const files = Array.from(event.target.files);
    
    // Check file count
    if (uploadedFiles.length + files.length > MAX_FILES) {
        showNotification(`Maximum ${MAX_FILES} files allowed`, 'warning');
        return;
    }
    
    // Check total size
    let totalSize = uploadedFiles.reduce((sum, f) => sum + f.size, 0);
    const newFilesSize = files.reduce((sum, f) => sum + f.size, 0);
    
    if (totalSize + newFilesSize > MAX_TOTAL_SIZE) {
        showNotification('Total file size exceeds 1GB limit', 'warning');
        return;
    }
    
    // Add files
    files.forEach(file => {
        uploadedFiles.push(file);
        addFileToPreview(file);
    });
    
    updateFilePreview();
    
    // Clear input for next selection
    event.target.value = '';
}

// Add file to preview
function addFileToPreview(file) {
    const fileList = document.getElementById('fileList');
    const fileId = `file-${Date.now()}-${Math.random()}`;
    
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.id = fileId;
    fileItem.innerHTML = `
        <div class="file-info">
            <span class="file-icon">${getFileIcon(file.type)}</span>
            <div class="file-details">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${formatFileSize(file.size)}</div>
            </div>
        </div>
        <button onclick="removeFile('${fileId}')" class="remove-file-btn">&times;</button>
    `;
    
    fileList.appendChild(fileItem);
}

// Get file icon based on type
function getFileIcon(type) {
    if (type.startsWith('image/')) return '🖼️';
    if (type.startsWith('video/')) return '🎥';
    if (type.startsWith('audio/')) return '🎵';
    if (type.includes('pdf')) return '📄';
    if (type.includes('word')) return '📝';
    if (type.includes('excel') || type.includes('spreadsheet')) return '📊';
    if (type.includes('powerpoint') || type.includes('presentation')) return '📽️';
    if (type.includes('zip') || type.includes('rar')) return '🗜️';
    if (type.includes('code') || type.includes('text')) return '💻';
    return '📎';
}

// Remove file
function removeFile(fileId) {
    const fileItem = document.getElementById(fileId);
    if (fileItem) {
        const index = Array.from(fileItem.parentNode.children).indexOf(fileItem);
        uploadedFiles.splice(index, 1);
        fileItem.remove();
        updateFilePreview();
    }
}

// Update file preview display
function updateFilePreview() {
    const preview = document.getElementById('fileUploadPreview');
    const uploadedCount = document.getElementById('uploadedCount');
    const totalSizeSpan = document.getElementById('totalSize');
    const fileCount = document.getElementById('fileCount');
    
    if (uploadedFiles.length > 0) {
        preview.style.display = 'block';
        uploadedCount.textContent = uploadedFiles.length;
        
        const totalSize = uploadedFiles.reduce((sum, f) => sum + f.size, 0);
        const totalMB = (totalSize / (1024 * 1024)).toFixed(2);
        totalSizeSpan.textContent = `${totalMB} MB / 1024 MB`;
        
        fileCount.textContent = uploadedFiles.length;
        fileCount.style.display = 'inline';
    } else {
        preview.style.display = 'none';
        fileCount.style.display = 'none';
    }
}

// Modify sendMessage to include uploaded files
const originalSendMessage = sendMessage;
sendMessage = async function() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message && uploadedFiles.length === 0) {
        showNotification('Please enter a message or upload files', 'warning');
        return;
    }
    
    // Create form data if files are present
    if (uploadedFiles.length > 0) {
        const formData = new FormData();
        formData.append('message', message);
        formData.append('mode', currentMode);
        
        uploadedFiles.forEach((file, index) => {
            formData.append(`file_${index}`, file);
        });
        
        formData.append('file_count', uploadedFiles.length);
        
        // Add message to chat
        addMessage('user', message + ` [${uploadedFiles.length} file(s) attached]`);
        
        // Clear input and files
        messageInput.value = '';
        uploadedFiles = [];
        document.getElementById('fileList').innerHTML = '';
        updateFilePreview();
        
        // Show typing indicator
        showTypingIndicator();
        
        // Disable send button
        const sendButton = document.getElementById('sendButton');
        sendButton.disabled = true;
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            removeTypingIndicator();
            
            if (data.error) {
                addMessage('error', data.error);
                showNotification('Error: ' + data.error, 'error');
            } else {
                addMessage('bot', data.response);
                if (data.app_suggestion) {
                    showAppSuggestion(data.app_suggestion);
                }
                saveChatHistory();
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            removeTypingIndicator();
            addMessage('error', 'Failed to send message. Please try again.');
            showNotification('Connection error', 'error');
        } finally {
            sendButton.disabled = false;
            messageInput.focus();
        }
    } else {
        // Call original sendMessage if no files
        await originalSendMessage();
    }
};

// Add message to chat
function addMessage(sender, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const currentTime = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>🤖 AI Assistant:</strong>
                <p>${content}</p>
            </div>
            <div class="message-time">${currentTime}</div>
        `;
    } else if (sender === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>You:</strong>
                <p>${content}</p>
            </div>
            <div class="message-time">${currentTime}</div>
        `;
    } else if (sender === 'error') {
        messageDiv.innerHTML = `
            <div class="message-content" style="background: rgba(220, 53, 69, 0.2); border: 1px solid #dc3545;">
                <strong>❌ Error:</strong>
                <p>${content}</p>
            </div>
            <div class="message-time">${currentTime}</div>
        `;
    }
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Add to chat history
    chatHistory.push({
        sender: sender,
        content: content,
        timestamp: currentTime
    });
}

// Add system message
function addSystemMessage(content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message system-message';
    messageDiv.style.textAlign = 'center';
    messageDiv.style.opacity = '0.7';
    
    messageDiv.innerHTML = `
        <div class="message-content" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);">
            <p style="margin: 0; font-style: italic;">ℹ️ ${content}</p>
        </div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Quick message function
function quickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    messageInput.focus();
}

// Suggest app function - FIXED
function suggestApp(appId) {
    debugLog(`Suggesting app: ${appId}`);
    
    const app = AVAILABLE_APPS[appId];
    if (!app) {
        errorLog(`App not found: ${appId}`);
        showNotification('App not found', 'error');
        return;
    }
    
    if (!app.available) {
        showNotification(`${app.name} is not currently available`, 'warning');
        return;
    }
    
    // Show app interface modal
    showAppInterface(appId, app);
}

// Show app interface - NEW FUNCTION
function showAppInterface(appId, appInfo) {
    debugLog(`Showing app interface for: ${appId}`);
    
    // Create modal
    const modalHTML = `
        <div id="appInterfaceModal" class="modal" style="display: flex;">
            <div class="modal-content" style="max-width: 800px; width: 90%;">
                <div class="modal-header">
                    <h3>${appInfo.icon} ${appInfo.name}</h3>
                    <button onclick="closeAppModal()" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p class="app-description">${appInfo.description}</p>
                    ${getAppInterface(appId)}
                </div>
            </div>
        </div>
    `;
    
    // Remove existing modal if present
    const existingModal = document.getElementById('appInterfaceModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    infoLog(`App interface shown: ${appInfo.name}`);
}

// Close app modal
function closeAppModal() {
    const modal = document.getElementById('appInterfaceModal');
    if (modal) {
        modal.style.opacity = '0';
        setTimeout(() => modal.remove(), 300);
    }
}

// Get app interface HTML - COMPLETE IMPLEMENTATION
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
        'testing_agent': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Project Name</label>
                    <input type="text" id="projectName" class="form-control" placeholder="Enter project name...">
                </div>
                <div class="form-group">
                    <label>Test Query</label>
                    <textarea id="testQuery" rows="3" class="form-control" placeholder="What are you testing?"></textarea>
                </div>
                <button onclick="runTestComparison()" class="primary-btn">Run Tests</button>
                <div id="testResults" class="results-area"></div>
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
        'document_extractor': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Upload Document</label>
                    <input type="file" id="documentFile" class="form-control" accept=".pdf,.docx,.txt">
                </div>
                <div class="form-group">
                    <label>Output Format</label>
                    <select id="outputFormat" class="form-control">
                        <option value="pdf">PDF</option>
                        <option value="docx">DOCX</option>
                        <option value="txt">TXT</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <button onclick="convertDocument()" class="primary-btn">Convert</button>
                <div id="conversionResult" class="results-area"></div>
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
                <button onclick="generateCoverLetter()" class="primary-btn">Generate Cover Letter</button>
                <div id="coverLetterResult" class="results-area"></div>
            </div>
        `,
        'job_ad_generator': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Job Title</label>
                    <input type="text" id="jobTitle" class="form-control" placeholder="e.g., Software Engineer">
                </div>
                <div class="form-group">
                    <label>Required Skills</label>
                    <textarea id="requiredSkills" rows="3" class="form-control" placeholder="List required skills..."></textarea>
                </div>
                <button onclick="generateJobAd()" class="primary-btn">Generate Job Ad</button>
                <div id="jobAdResult" class="results-area"></div>
            </div>
        `,
        'speech_to_text': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Upload Audio File</label>
                    <input type="file" id="audioFile" class="form-control" accept="audio/*">
                </div>
                <button onclick="transcribeAudio()" class="primary-btn">Transcribe Audio</button>
                <div id="transcriptionResult" class="results-area"></div>
            </div>
        `,
        'calendar_system': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Event Title</label>
                    <input type="text" id="eventTitle" class="form-control" placeholder="Meeting title...">
                </div>
                <div class="form-group">
                    <label>Date & Time</label>
                    <input type="datetime-local" id="eventDateTime" class="form-control">
                </div>
                <button onclick="createCalendarEvent()" class="primary-btn">Create Event</button>
                <div id="calendarResult" class="results-area"></div>
            </div>
        `,
        'doc_summariser': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Document Text</label>
                    <textarea id="summaryDocText" rows="8" class="form-control" placeholder="Paste document text here..."></textarea>
                </div>
                <button onclick="summarizeDocument()" class="primary-btn">Summarize</button>
                <div id="summaryResult" class="results-area"></div>
            </div>
        `,
        'directory_summariser': `
            <div class="app-interface">
                <div class="form-group">
                    <label>Directory Path</label>
                    <input type="text" id="directoryPath" class="form-control" placeholder="C:\\path\\to\\directory">
                </div>
                <button onclick="analyzeDirectory()" class="primary-btn">Analyze Directory</button>
                <div id="directoryResult" class="results-area"></div>
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
                    </select>
                </div>
                <button onclick="getCodeAssistance()" class="primary-btn">Get Assistance</button>
                <div id="codeAssistanceResult" class="results-area"></div>
            </div>
        `
    };
    
    return interfaces[appId] || '<p>App interface not yet implemented.</p>';
}

// Stub functions for app actions (these will call the backend APIs)
function executeDocumentSearch() {
    showNotification('Document search feature coming soon', 'info');
}

function runTestComparison() {
    showNotification('Test comparison feature coming soon', 'info');
}

function calculateWorkHours() {
    showNotification('Work hours calculator coming soon', 'info');
}

function convertDocument() {
    showNotification('Document conversion feature coming soon', 'info');
}

function generateCoverLetter() {
    showNotification('Cover letter generation coming soon', 'info');
}

function generateJobAd() {
    showNotification('Job ad generation feature coming soon', 'info');
}

function transcribeAudio() {
    showNotification('Audio transcription feature coming soon', 'info');
}

function createCalendarEvent() {
    showNotification('Calendar event creation coming soon', 'info');
}

async function summarizeDocument() {
    const text = document.getElementById('summaryDocText').value;
    const resultsDiv = document.getElementById('summaryResult');
    
    if (!text.trim()) {
        showNotification('Please enter document text', 'warning');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="spinner"></div> Generating summary...';
    
    try {
        const response = await fetch('/api/summarize-document', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ document_content: text })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultsDiv.innerHTML = `
                <h4>Summary:</h4>
                <div class="summary-content">${data.summary}</div>
            `;
            showNotification('Document summarized successfully', 'success');
        } else {
            resultsDiv.innerHTML = `<p class="error-text">Error: ${data.error}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p class="error-text">Error: ${error.message}</p>`;
        showNotification('Summarization failed', 'error');
    }
}

function analyzeDirectory() {
    showNotification('Directory analysis feature coming soon', 'info');
}

function getCodeAssistance() {
    showNotification('Code assistance feature coming soon', 'info');
}

// Chat utility functions
function showTypingIndicator() {
    const messagesDiv = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <span>AI is typing</span>
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    `;
    messagesDiv.appendChild(typingDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function clearChat() {
    if (confirm('Are you sure you want to clear the chat?')) {
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = `
            <div class="message bot-message">
                <div class="message-content">
                    <strong>🤖 AI Assistant:</strong>
                    <p>Chat cleared. How can I help you?</p>
                </div>
            </div>
        `;
        chatHistory = [];
        localStorage.removeItem('chatHistory');
        showNotification('Chat cleared', 'success');
    }
}

function exportChat() {
    const chatText = chatHistory.map(msg => 
        `[${msg.timestamp}] ${msg.sender.toUpperCase()}: ${msg.content}`
    ).join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat_export_${new Date().toISOString().slice(0,10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
    showNotification('Chat exported', 'success');
}

function showHelp() {
    addMessage('bot', `
        <strong>Help Guide:</strong><br><br>
        🎯 <strong>Prompt Modes:</strong> Select different AI personalities<br>
        🚀 <strong>Quick Apps:</strong> Click to launch specific tools<br>
        💬 <strong>Chat:</strong> Type messages or use voice input<br>
        📎 <strong>Files:</strong> Upload up to 10 files (1GB total)<br>
        🎤 <strong>Voice:</strong> Click microphone to speak<br><br>
        Type anything to get started!
    `);
}

function saveChatHistory() {
    try {
        localStorage.setItem('chatHistory', JSON.stringify(chatHistory.slice(-50)));
    } catch (e) {
        console.error('Failed to save chat history:', e);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('chatHistory');
        if (saved) {
            chatHistory = JSON.parse(saved);
            // Optionally restore messages to UI
        }
    } catch (e) {
        console.error('Failed to load chat history:', e);
    }
}

//# sourceMappingURL=app.js.map