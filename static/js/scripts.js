// Directory AI Summariser JavaScript Functions

// Enhanced logging for debugging
const DEBUG = true;

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

// Global variables for chatbot
let currentMode = 'general';
let suggestedAppId = null;
let chatHistory = [];
let uploadedFiles = [];
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];

// Get data from window object (passed from HTML template)
const PROMPT_MODES = window.PROMPT_MODES || {};
const AVAILABLE_APPS = window.AVAILABLE_APPS || {};

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    debugLog('DOM Content Loaded - Starting initialization');
    
    // Initialize the application
    initializeApp();
    
    // Form validation and submission handling
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
    
    // Initialize chatbot
    initializeChatbot();
    
    debugLog('Initialization complete');
});

// Initialize application
function initializeApp() {
    debugLog('Initializing application components');
    
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

// Initialize chatbot
function initializeChatbot() {
    console.log('Chatbot initialized');
    
    loadChatHistory();
    
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    updateModeDescription();
}

// =============================================================================
// FORM VALIDATION
// =============================================================================

function setupFormValidation() {
    debugLog('Setting up form validation');
    
    const forms = document.querySelectorAll('form');
    debugLog(`Found ${forms.length} forms to validate`);
    
    forms.forEach((form, index) => {
        if (form.dataset.listenerAdded === 'true') {
            return;
        }
        
        form.dataset.listenerAdded = 'true';
        
        form.addEventListener('submit', function(e) {
            const formData = new FormData(this);
            const formDataObj = Object.fromEntries(formData.entries());
            
            debugLog(`Form ${index + 1} submission attempt`, formDataObj);
            
            const directoryInput = this.querySelector('input[name="directory_path"]');
            const templateFiles = this.querySelector('input[name="template_files"]');
            const submitBtn = this.querySelector('button[type="submit"]');
            
            if (this.action.includes('analyze_directory')) {
                const path = directoryInput ? directoryInput.value.trim() : '';
                
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
                
                if (submitBtn) {
                    submitBtn.dataset.originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Analyzing...';
                    submitBtn.disabled = true;
                }
                
                if (directoryInput) {
                    directoryInput.readOnly = true;
                    directoryInput.style.opacity = '0.6';
                    directoryInput.style.pointerEvents = 'none';
                }
                
                showProgressIndicator('Starting directory analysis...');
                setupProgressMessages();
                
                return true;
            }
            
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
            }
            
            else {
                if (submitBtn) {
                    submitBtn.dataset.originalText = submitBtn.textContent;
                    submitBtn.textContent = 'Processing...';
                    submitBtn.disabled = true;
                }
            }
        });
    });
}

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
    
    window.analysisProgressInterval = progressInterval;
}

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

function isValidDirectoryPath(path) {
    if (path.length < 3) return false;
    if (path.match(/^[A-Za-z]:\\/)) return true;
    if (path.startsWith('/')) return true;
    if (path.startsWith('./') || path.startsWith('../')) return true;
    return false;
}

// =============================================================================
// FILE UPLOAD HANDLING
// =============================================================================

function setupFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            const maxSize = 16 * 1024 * 1024;
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
            
            if (totalSize > maxSize) {
                showNotification('Total file size exceeds 16MB limit', 'error');
                input.value = '';
                return;
            }
            
            if (validFiles !== files.length) {
                showNotification('Some files have unsupported formats', 'warning');
            }
            
            if (files.length > 0) {
                showNotification(`${files.length} file(s) selected (${formatFileSize(totalSize)})`, 'success');
            }
        });
    });
}

function openFileUpload() {
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.click();
    }
}

function handleFileSelection(event) {
    const files = Array.from(event.target.files);
    const maxFiles = 10;
    const maxTotalSize = 1024 * 1024 * 1024; // 1GB
    
    if (uploadedFiles.length + files.length > maxFiles) {
        showNotification(`Maximum ${maxFiles} files allowed`, 'error');
        return;
    }
    
    let totalSize = uploadedFiles.reduce((sum, f) => sum + f.size, 0);
    totalSize += files.reduce((sum, f) => sum + f.size, 0);
    
    if (totalSize > maxTotalSize) {
        showNotification('Total file size exceeds 1GB limit', 'error');
        return;
    }
    
    uploadedFiles = uploadedFiles.concat(files);
    updateFilePreview();
    showNotification(`${files.length} file(s) added`, 'success');
}

function updateFilePreview() {
    const fileList = document.getElementById('fileList');
    const fileUploadPreview = document.getElementById('fileUploadPreview');
    const uploadedCount = document.getElementById('uploadedCount');
    const totalSize = document.getElementById('totalSize');
    const fileCount = document.getElementById('fileCount');
    
    if (!fileList) return;
    
    if (uploadedFiles.length === 0) {
        fileUploadPreview.style.display = 'none';
        fileCount.style.display = 'none';
        return;
    }
    
    fileUploadPreview.style.display = 'block';
    fileCount.style.display = 'inline';
    fileCount.textContent = uploadedFiles.length;
    
    uploadedCount.textContent = uploadedFiles.length;
    
    const total = uploadedFiles.reduce((sum, f) => sum + f.size, 0);
    totalSize.textContent = `${(total / (1024 * 1024)).toFixed(2)} MB / 1024 MB`;
    
    fileList.innerHTML = uploadedFiles.map((file, index) => `
        <div class="file-item">
            <span class="file-icon">📄</span>
            <span class="file-name">${file.name}</span>
            <span class="file-size">${formatFileSize(file.size)}</span>
            <button onclick="removeFile(${index})" class="remove-file-btn">×</button>
        </div>
    `).join('');
}

function removeFile(index) {
    uploadedFiles.splice(index, 1);
    updateFilePreview();
    showNotification('File removed', 'info');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// =============================================================================
// DIRECTORY VALIDATION
// =============================================================================

function setupDirectoryValidation() {
    const directoryInputs = document.querySelectorAll('input[name="directory_path"]');
    
    directoryInputs.forEach(input => {
        let timeout;
        
        input.addEventListener('input', function(e) {
            clearTimeout(timeout);
            const path = e.target.value.trim();
            
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

// =============================================================================
// REAL-TIME FEEDBACK
// =============================================================================

function setupRealTimeFeedback() {
    window.addEventListener('pageshow', function(e) {
        if (e.persisted) {
            resetFormState();
        }
    });
}

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
    
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) {
        progressIndicator.remove();
    }
    
    if (window.analysisProgressInterval) {
        clearInterval(window.analysisProgressInterval);
    }
}

// =============================================================================
// NOTIFICATIONS & PROGRESS
// =============================================================================

function showNotification(message, type = 'info', duration = 5000) {
    debugLog(`Showing notification: ${type} - ${message}`);
    
    const existing = document.querySelectorAll(`.notification-${type}`);
    existing.forEach(notif => notif.remove());
    
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
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    };
    return icons[type] || 'ℹ️';
}

function showProgressIndicator(message) {
    const existing = document.getElementById('progressIndicator');
    if (existing) existing.remove();
    
    const progressHTML = `
        <div id="progressIndicator" class="progress-overlay">
            <div class="progress-content">
                <div class="progress-spinner"></div>
                <p class="progress-message">${message}</p>
                <div class="progress-details">
                    <p>This may take a few moments...</p>
                    <p id="progressTimer">Elapsed time: 0s</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', progressHTML);
    
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
}

// =============================================================================
// CHATBOT FUNCTIONALITY
// =============================================================================

function changeMode() {
    const modeSelect = document.getElementById('promptMode');
    currentMode = modeSelect.value;
    updateModeDescription();
    
    const mode = PROMPT_MODES[currentMode];
    if (mode) {
        addSystemMessage(`Switched to ${mode.name} mode`);
    }
}

function updateModeDescription() {
    const modeDesc = document.getElementById('modeDescription');
    const mode = PROMPT_MODES[currentMode];
    
    if (modeDesc && mode) {
        modeDesc.textContent = mode.description;
    }
}

async function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();
    
    if (!message && uploadedFiles.length === 0) {
        showNotification('Please enter a message or upload files', 'warning');
        return;
    }
    
    if (message) {
        const fileInfo = uploadedFiles.length > 0 ? ` [${uploadedFiles.length} file(s) attached]` : '';
        addMessage('user', message + fileInfo);
    }
    
    messageInput.value = '';
    showTypingIndicator();
    
    const sendButton = document.getElementById('sendButton');
    sendButton.disabled = true;
    
    try {
        let response;
        
        if (uploadedFiles.length > 0) {
            const formData = new FormData();
            formData.append('message', message);
            formData.append('mode', currentMode);
            
            uploadedFiles.forEach((file, index) => {
                formData.append(`file_${index}`, file);
            });
            
            formData.append('file_count', uploadedFiles.length);
            
            response = await fetch('/chat', {
                method: 'POST',
                body: formData
            });
            
            uploadedFiles = [];
            document.getElementById('fileList').innerHTML = '';
            updateFilePreview();
        } else {
            response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    mode: currentMode
                })
            });
        }
        
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
}

function addMessage(sender, content) {
    const messagesDiv = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${sender === 'user' ? '👤 You' : sender === 'bot' ? '🤖 AI Assistant' : '⚠️ System'}:</strong>
            <p>${content}</p>
        </div>
        <div class="message-time">${timestamp}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    chatHistory.push({
        sender: sender,
        content: content,
        timestamp: timestamp
    });
}

function addSystemMessage(content) {
    addMessage('system', content);
}

function quickMessage(message) {
    const messageInput = document.getElementById('messageInput');
    messageInput.value = message;
    sendMessage();
}

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
        }
    } catch (e) {
        console.error('Failed to load chat history:', e);
    }
}

// =============================================================================
// APP SUGGESTIONS & MODALS
// =============================================================================

function suggestApp(appId) {
    const app = AVAILABLE_APPS[appId];
    if (!app) return;
    
    if (!app.available) {
        showNotification(`${app.name} is not currently available`, 'warning');
        return;
    }
    
    suggestedAppId = appId;
    
    const modal = document.getElementById('appSuggestionModal');
    const appDiv = document.getElementById('suggestedApp');
    
    appDiv.innerHTML = `
        <div class="app-card">
            <div class="app-icon">${app.icon}</div>
            <h4>${app.name}</h4>
            <p>${app.description}</p>
            <div class="app-interface-preview">
                ${getAppInterface(appId)}
            </div>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function showAppSuggestion(suggestion) {
    suggestedAppId = suggestion.app_id;
    
    const modal = document.getElementById('appSuggestionModal');
    const appDiv = document.getElementById('suggestedApp');
    
    appDiv.innerHTML = `
        <div class="app-card">
            <h4>${suggestion.app_name}</h4>
            <p>${suggestion.description}</p>
            <p class="confidence">Confidence: ${Math.round(suggestion.confidence * 100)}%</p>
        </div>
    `;
    
    modal.style.display = 'flex';
}

function closeModal() {
    const modal = document.getElementById('appSuggestionModal');
    modal.style.display = 'none';
    suggestedAppId = null;
}

function goToApp() {
    if (suggestedAppId) {
        const app = AVAILABLE_APPS[suggestedAppId];
        if (app) {
            addMessage('bot', `Opening ${app.name}...`);
            addMessage('system', getAppInterface(suggestedAppId));
        }
    }
    closeModal();
}

function continueChat() {
    closeModal();
    const messageInput = document.getElementById('messageInput');
    messageInput.focus();
}

// =============================================================================
// APP INTERFACES
// =============================================================================

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
                    <label>Project Description</label>
                    <textarea id="projectDescription" rows="3" class="form-control" placeholder="Describe your project..."></textarea>
                </div>
                <div class="form-group">
                    <label>Test Query</label>
                    <textarea id="testQuery" rows="3" class="form-control" placeholder="What are you testing?"></textarea>
                </div>
                <div class="form-group">
                    <label>Expected Results (PDF)</label>
                    <input type="file" id="expectedResults" class="form-control" accept=".pdf">
                </div>
                <div class="form-group">
                    <label>Actual Results (Screenshot)</label>
                    <input type="file" id="actualResults" class="form-control" accept="image/*">
                </div>
                <div class="form-group">
                    <label>Additional Context</label>
                    <textarea id="additionalContext" rows="3" class="form-control" placeholder="Any additional information..."></textarea>
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
                        <option value="day">Per Day</option>
                        <option value="week">Per Week</option>
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
                        <option value="same">Keep Same Format</option>
                        <option value="pdf">PDF</option>
                        <option value="docx">DOCX</option>
                        <option value="txt">TXT</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Table Handling</label>
                    <select id="tableHandling" class="form-control">
                        <option value="keep">Keep Original Table</option>
                        <option value="empty">Convert to Empty Table</option>
                        <option value="remove">Remove Tables</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Field Mapping (JSON format)</label>
                    <textarea id="fieldMapping" rows="3" class="form-control" placeholder='{"original_field": "new_field"}'></textarea>
                </div>
                <div class="form-group">
                    <label>Custom Placeholder Text</label>
                    <input type="text" id="placeholderText" class="form-control" placeholder="e.g., [To be filled]">
                </div>
                <div class="form-group">
                    <label>Page Range</label>
                    <input type="text" id="pageRange" class="form-control" placeholder="e.g., 1-3, all">
                </div>
                <div class="form-group">
                    <label>Output Formatting</label>
                    <select id="outputFormatting" class="form-control">
                        <option value="original">Keep Original Formatting</option>
                        <option value="default">Apply Default Formatting</option>
                        <option value="custom">Custom Formatting</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Additional Notes/Instructions</label>
                    <textarea id="additionalNotes" rows="3" class="form-control" placeholder="Any special instructions..."></textarea>
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
                <h4>Job Role Information</h4>
                <div class="form-group">
                    <label>Job Title</label>
                    <input type="text" id="jobTitle" class="form-control" placeholder="e.g., Software Engineer">
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 1; margin-right: 10px;">
                        <label>Employment Type</label>
                        <select id="employmentType" class="form-control">
                            <option value="full-time">Full-time</option>
                            <option value="part-time">Part-time</option>
                            <option value="contract">Contract</option>
                        </select>
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Work Mode</label>
                        <select id="workMode" class="form-control">
                            <option value="remote">Remote</option>
                            <option value="in-person">In-Person</option>
                            <option value="hybrid">Hybrid</option>
                        </select>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group" style="flex: 1; margin-right: 10px;">
                        <label>Department</label>
                        <input type="text" id="department" class="form-control" placeholder="e.g., Engineering">
                    </div>
                    <div class="form-group" style="flex: 1;">
                        <label>Location</label>
                        <input type="text" id="location" class="form-control" placeholder="e.g., New York, NY">
                    </div>
                </div>
                <div class="form-group">
                    <label>Salary Range</label>
                    <input type="text" id="salaryRange" class="form-control" placeholder="e.g., $80,000 - $120,000">
                </div>
                
                <h4>Requirements</h4>
                <div class="form-group">
                    <label>Minimum Education Required</label>
                    <input type="text" id="minEducation" class="form-control" placeholder="e.g., Bachelor's degree in Computer Science">
                </div>
                <div class="form-group">
                    <label>Experience Requirements</label>
                    <textarea id="experienceReqs" rows="3" class="form-control" placeholder="e.g., 3+ years in software development"></textarea>
                </div>
                <div class="form-group">
                    <label>Key Job Responsibilities</label>
                    <textarea id="jobResponsibilities" rows="4" class="form-control" placeholder="List main responsibilities..."></textarea>
                </div>
                <div class="form-group">
                    <label>Required Skills</label>
                    <textarea id="requiredSkills" rows="3" class="form-control" placeholder="List required skills..."></textarea>
                </div>
                <div class="form-group">
                    <label>Preferred Skills</label>
                    <textarea id="preferredSkills" rows="3" class="form-control" placeholder="List preferred skills..."></textarea>
                </div>
                <div class="form-group">
                    <label>Desired Personality Traits</label>
                    <textarea id="personalityTraits" rows="2" class="form-control" placeholder="e.g., Team player, self-motivated..."></textarea>
                </div>
                
                <h4>Company Information</h4>
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" id="companyName" class="form-control" placeholder="Your company name">
                </div>
                <div class="form-group">
                    <label>About Company</label>
                    <textarea id="aboutCompany" rows="3" class="form-control" placeholder="Brief company description..."></textarea>
                </div>
                <div class="form-group">
                    <label>Diversity & Inclusion Statement</label>
                    <textarea id="diversityStatement" rows="2" class="form-control" placeholder="Optional diversity statement..."></textarea>
                </div>
                <div class="form-group">
                    <label>Application Process Details</label>
                    <textarea id="applicationProcess" rows="2" class="form-control" placeholder="How to apply..."></textarea>
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
                    <label>Input Method</label>
                    <select id="inputMethod" class="form-control" onchange="toggleSummaryInput()">
                        <option value="text">Paste Text</option>
                        <option value="upload">Upload Document</option>
                    </select>
                </div>
                <div class="form-group" id="textInputGroup">
                    <label>Document Text</label>
                    <textarea id="summaryDocText" rows="8" class="form-control" placeholder="Paste document text here..."></textarea>
                </div>
                <div class="form-group" id="fileInputGroup" style="display: none;">
                    <label>Upload Document</label>
                    <input type="file" id="summaryDocFile" class="form-control" accept=".pdf,.docx,.txt,.md">
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
                        <option value="csharp">C#</option>
                        <option value="cpp">C++</option>
                    </select>
                </div>
                <button onclick="getCodeAssistance()" class="primary-btn">Get Assistance</button>
                <div id="codeAssistanceResult" class="results-area"></div>
            </div>
        `
    };
    
    return interfaces[appId] || '<p>App interface not yet implemented.</p>';
}

function toggleSummaryInput() {
    const method = document.getElementById('inputMethod').value;
    const textGroup = document.getElementById('textInputGroup');
    const fileGroup = document.getElementById('fileInputGroup');
    
    if (method === 'text') {
        textGroup.style.display = 'block';
        fileGroup.style.display = 'none';
    } else {
        textGroup.style.display = 'none';
        fileGroup.style.display = 'block';
    }
}

// =============================================================================
// APP EXECUTION FUNCTIONS
// =============================================================================

async function executeDocumentSearch() {
    const query = document.getElementById('searchQuery')?.value;
    const directory = document.getElementById('searchDirectory')?.value || 'default';
    
    if (!query) {
        showNotification('Please enter a search query', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/search-documents', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, directory })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultsDiv = document.getElementById('searchResults');
            resultsDiv.innerHTML = `
                <h4>Search Results</h4>
                <div class="ai-summary">${data.ai_summary}</div>
                <div class="results-list">
                    ${data.results.map(r => `<div class="result-item">${r}</div>`).join('')}
                </div>
            `;
            resultsDiv.style.display = 'block';
            showNotification('Search completed', 'success');
        } else {
            showNotification(data.error || 'Search failed', 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Search failed', 'error');
    }
}

async function runTestComparison() {
    const projectName = document.getElementById('projectName')?.value;
    const projectDescription = document.getElementById('projectDescription')?.value;
    const testQuery = document.getElementById('testQuery')?.value;
    const expectedResults = document.getElementById('expectedResults')?.files[0];
    const actualResults = document.getElementById('actualResults')?.files[0];
    const additionalContext = document.getElementById('additionalContext')?.value;
    
    if (!projectName || !testQuery) {
        showNotification('Please enter project name and test query', 'warning');
        return;
    }
    
    if (!expectedResults || !actualResults) {
        showNotification('Please upload both expected and actual results files', 'warning');
        return;
    }
    
    // Validate file types
    if (!expectedResults.name.toLowerCase().endsWith('.pdf')) {
        showNotification('Expected results must be a PDF file', 'warning');
        return;
    }
    
    const allowedImageTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp'];
    if (!allowedImageTypes.includes(actualResults.type) && 
        !actualResults.name.toLowerCase().match(/\.(png|jpg|jpeg|gif|bmp)$/)) {
        showNotification('Actual results must be an image file (PNG, JPG, GIF, BMP)', 'warning');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('project_name', projectName);
        formData.append('project_description', projectDescription || '');
        formData.append('test_query', testQuery);
        formData.append('expected_results', expectedResults);
        formData.append('actual_results', actualResults);
        formData.append('additional_context', additionalContext || '');
        
        showNotification('Running test comparison... This may take a moment.', 'info');
        
        // Log the request for debugging
        console.log('Sending test comparison request:', {
            project_name: projectName,
            test_query: testQuery,
            expected_file: expectedResults.name,
            actual_file: actualResults.name
        });
        
        const response = await fetch('/api/run-test-comparison', {
            method: 'POST',
            body: formData
            // Don't set Content-Type header - let browser set it for multipart/form-data
        });
        
        console.log('Response status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response:', errorText);
            throw new Error(`Server returned ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.success) {
            const resultsDiv = document.getElementById('testResults');
            resultsDiv.innerHTML = `
                <h4>Test Comparison Results</h4>
                <div class="comparison-section">
                    <h5>Comparison Analysis</h5>
                    <div class="comparison-content">${data.comparison}</div>
                </div>
                <div class="summary-section">
                    <h5>Summary</h5>
                    <div class="summary-content">${data.summary}</div>
                </div>
                <div class="result-actions" style="margin-top: 20px;">
                    <button onclick="copyToClipboard(document.querySelector('.comparison-content').innerText)" class="secondary-btn">
                        📋 Copy Comparison
                    </button>
                    <button onclick="copyToClipboard(document.querySelector('.summary-content').innerText)" class="secondary-btn">
                        📋 Copy Summary
                    </button>
                </div>
            `;
            resultsDiv.style.display = 'block';
            showNotification('Test comparison completed successfully!', 'success');
        } else {
            showNotification(data.error || 'Test comparison failed', 'error');
        }
    } catch (error) {
        console.error('Test comparison error:', error);
        showNotification(`Test comparison failed: ${error.message}`, 'error');
    }
}

async function convertDocument() {
    const documentFile = document.getElementById('documentFile')?.files[0];
    const outputFormat = document.getElementById('outputFormat')?.value;
    const tableHandling = document.getElementById('tableHandling')?.value;
    const fieldMapping = document.getElementById('fieldMapping')?.value;
    const placeholderText = document.getElementById('placeholderText')?.value;
    const pageRange = document.getElementById('pageRange')?.value;
    const outputFormatting = document.getElementById('outputFormatting')?.value;
    const additionalNotes = document.getElementById('additionalNotes')?.value;
    
    if (!documentFile) {
        showNotification('Please upload a document', 'warning');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('document_file', documentFile);
        formData.append('output_format', outputFormat);
        formData.append('table_handling', tableHandling);
        formData.append('field_mapping', fieldMapping || '{}');
        formData.append('placeholder_text', placeholderText || '');
        formData.append('page_range', pageRange || 'all');
        formData.append('output_formatting', outputFormatting);
        formData.append('additional_notes', additionalNotes || '');
        
        showNotification('Converting document...', 'info');
        
        const response = await fetch('/api/convert-document', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Download converted file
            const byteCharacters = atob(data.converted_file);
            const byteNumbers = new Array(byteCharacters.length);
            for (let i = 0; i < byteCharacters.length; i++) {
                byteNumbers[i] = byteCharacters.charCodeAt(i);
            }
            const byteArray = new Uint8Array(byteNumbers);
            const blob = new Blob([byteArray]);
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            URL.revokeObjectURL(url);
            
            const resultDiv = document.getElementById('conversionResult');
            resultDiv.innerHTML = `
                <h4>Conversion Complete</h4>
                <p>File: ${data.filename}</p>
                ${data.insights ? `<div class="insights">${data.insights}</div>` : ''}
            `;
            resultDiv.style.display = 'block';
            
            showNotification('Document converted successfully', 'success');
        } else {
            showNotification(data.error || 'Conversion failed', 'error');
        }
    } catch (error) {
        console.error('Conversion error:', error);
        showNotification('Conversion failed', 'error');
    }
}

async function generateJobAd() {
    // Collect all form data
    const jobData = {
        job_title: document.getElementById('jobTitle')?.value,
        employment_type: document.getElementById('employmentType')?.value,
        work_mode: document.getElementById('workMode')?.value,
        department: document.getElementById('department')?.value,
        location: document.getElementById('location')?.value,
        salary_range: document.getElementById('salaryRange')?.value,
        min_education: document.getElementById('minEducation')?.value,
        experience_reqs: document.getElementById('experienceReqs')?.value,
        job_responsibilities: document.getElementById('jobResponsibilities')?.value,
        required_skills: document.getElementById('requiredSkills')?.value,
        preferred_skills: document.getElementById('preferredSkills')?.value,
        personality_traits: document.getElementById('personalityTraits')?.value,
        company_name: document.getElementById('companyName')?.value,
        about_company: document.getElementById('aboutCompany')?.value,
        diversity_statement: document.getElementById('diversityStatement')?.value,
        application_process: document.getElementById('applicationProcess')?.value
    };
    
    if (!jobData.job_title) {
        showNotification('Please enter a job title', 'warning');
        return;
    }
    
    try {
        const formData = new FormData();
        Object.keys(jobData).forEach(key => {
            formData.append(key, jobData[key] || '');
        });
        
        showNotification('Generating job ad...', 'info');
        
        const response = await fetch('/api/generate-job-ad', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('jobAdResult');
            resultDiv.innerHTML = `
                <h4>Generated Job Advertisement</h4>
                <div class="job-ad-content">${data.job_ad}</div>
                <button onclick="copyToClipboard(\`${data.job_ad_raw.replace(/`/g, '\\`')}\`)" class="secondary-btn">Copy to Clipboard</button>
            `;
            resultDiv.style.display = 'block';
            showNotification('Job ad generated', 'success');
        } else {
            showNotification(data.error || 'Generation failed', 'error');
        }
    } catch (error) {
        console.error('Job ad generation error:', error);
        showNotification('Generation failed', 'error');
    }
}

async function transcribeAudio() {
    const audioFile = document.getElementById('audioFile')?.files[0];
    
    if (!audioFile) {
        showNotification('Please upload an audio file', 'warning');
        return;
    }
    
    try {
        const formData = new FormData();
        formData.append('audio_file', audioFile);
        
        showNotification('Transcribing audio...', 'info');
        
        const response = await fetch('/api/transcribe-audio', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('transcriptionResult');
            resultDiv.innerHTML = `
                <h4>Transcription</h4>
                <div class="transcription-text">${data.transcription}</div>
                ${data.summary ? `<h5>Summary</h5><div class="summary-text">${data.summary}</div>` : ''}
            `;
            resultDiv.style.display = 'block';
            showNotification('Transcription completed', 'success');
        } else {
            showNotification(data.error || 'Transcription failed', 'error');
        }
    } catch (error) {
        console.error('Transcription error:', error);
        showNotification('Transcription failed', 'error');
    }
}

async function createCalendarEvent() {
    const eventTitle = document.getElementById('eventTitle')?.value;
    const eventDateTime = document.getElementById('eventDateTime')?.value;
    
    if (!eventTitle || !eventDateTime) {
        showNotification('Please enter event title and date/time', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/create-calendar-event', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_title: eventTitle,
                event_datetime: eventDateTime
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('calendarResult');
            resultDiv.innerHTML = `
                <h4>Event Created</h4>
                <p>${data.message}</p>
            `;
            resultDiv.style.display = 'block';
            showNotification('Event created successfully', 'success');
        } else {
            showNotification(data.error || 'Event creation failed', 'error');
        }
    } catch (error) {
        console.error('Calendar event error:', error);
        showNotification('Event creation failed', 'error');
    }
}

async function analyzeDirectory() {
    const directoryPath = document.getElementById('directoryPath')?.value;
    
    if (!directoryPath) {
        showNotification('Please enter a directory path', 'warning');
        return;
    }
    
    try {
        showNotification('Analyzing directory...', 'info');
        
        const response = await fetch('/api/analyze-directory', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory_path: directoryPath })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const resultDiv = document.getElementById('directoryResult');
            resultDiv.innerHTML = `
                <h4>Directory Analysis</h4>
                <div class="analysis-content">${JSON.stringify(data.analysis, null, 2)}</div>
                ${data.summary ? `<h5>AI Summary</h5><div class="summary-content">${data.summary}</div>` : ''}
            `;
            resultDiv.style.display = 'block';
            showNotification('Directory analyzed', 'success');
        } else {
            showNotification(data.error || 'Analysis failed', 'error');
        }
    } catch (error) {
        console.error('Directory analysis error:', error);
        showNotification('Analysis failed', 'error');
    }
}

// =============================================================================
// VOICE RECORDING
// =============================================================================

async function toggleVoiceRecording() {
    if (!isRecording) {
        startVoiceRecording();
    } else {
        stopVoiceRecording();
    }
}

async function startVoiceRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            // Here you would send the audio to your speech-to-text API
            showNotification('Voice recording completed', 'success');
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        document.getElementById('voiceTranscript').style.display = 'block';
        document.getElementById('voiceBtn').style.backgroundColor = '#dc3545';
        
        showNotification('Recording started...', 'info');
    } catch (error) {
        console.error('Voice recording error:', error);
        showNotification('Could not start recording', 'error');
    }
}

function stopVoiceRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        document.getElementById('voiceTranscript').style.display = 'none';
        document.getElementById('voiceBtn').style.backgroundColor = '';
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function checkForFlashMessages() {
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('.flash-message, [class*="flash"], .alert');
        debugLog('Found flash messages:', flashMessages.length);
    }, 100);
}

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
        if (response.ok) {
            const filename = response.headers.get('Content-Disposition')
                ?.split('filename=')[1]?.replace(/"/g, '') || 
                `directory_analysis.${format}`;
            
            return response.blob().then(blob => {
                downloadFile(blob, filename);
                showNotification('Export completed successfully', 'success');
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

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(function(err) {
        console.error('Copy failed:', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// =============================================================================
// EVENT LISTENERS
// =============================================================================

window.addEventListener('beforeunload', function() {
    debugLog('Page unload detected, cleaning up');
    
    const progressIndicator = document.getElementById('progressIndicator');
    if (progressIndicator) {
        progressIndicator.remove();
    }
    
    if (window.analysisProgressInterval) {
        clearInterval(window.analysisProgressInterval);
    }
});

window.addEventListener('error', function(e) {
    errorLog('JavaScript error caught', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        error: e.error
    });
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('[ERROR] Unhandled promise rejection:', e.reason);
});