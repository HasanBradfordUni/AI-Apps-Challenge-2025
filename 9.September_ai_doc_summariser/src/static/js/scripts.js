// scripts.js - Complete JavaScript for Document Summarizer

// Global variables
let currentDocument = null;
let currentSummary = null;
let documentSessions = {};
let processingInProgress = false;

// Global variable to track current comparison session
let currentComparisonSession = null;

// Document ready initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document Summarizer initialized');
    loadSessions();
    setupFormValidation();
    setupFileUpload();
    handleMainFormSubmission(); // Add this line
});

// Form handling functions
function clearForm() {
    const form = document.getElementById('upload-form');
    if (form) {
        form.reset();
        
        // Clear document preview
        const preview = document.getElementById('document-preview');
        if (preview) {
            preview.style.display = 'none';
        }
        
        // Clear summary results
        const summaryDisplay = document.querySelector('.summary-display');
        if (summaryDisplay) {
            summaryDisplay.innerHTML = 'No summary available. Upload a document above to generate an AI summary.';
        }
        
        // Hide regeneration panel
        const regenPanel = document.getElementById('regeneration-panel');
        if (regenPanel) {
            regenPanel.style.display = 'none';
        }
        
        console.log('Form cleared');
    }
}

function setupFormValidation() {
    const form = document.getElementById('upload-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('document_file');
            if (!fileInput.files.length) {
                e.preventDefault();
                alert('Please select a document to upload');
                return false;
            }
            
            // Show processing indicator
            showProcessingIndicator();
        });
    }
}

function setupFileUpload() {
    const fileInput = document.getElementById('document_file');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                validateFile(file);
                previewDocument(file);
            }
        });
    }
}

function validateFile(file) {
    const maxSize = 100 * 1024 * 1024; // 100MB
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    
    if (file.size > maxSize) {
        alert('File size exceeds 100MB limit');
        return false;
    }
    
    if (!allowedTypes.includes(file.type)) {
        alert('Invalid file type. Please upload PDF, DOCX, or TXT files only.');
        return false;
    }
    
    return true;
}

function previewDocument(file) {
    const preview = document.getElementById('document-preview');
    const textPreview = document.getElementById('document-text-preview');
    const statsPanel = document.getElementById('document-stats');
    
    if (preview && textPreview) {
        preview.style.display = 'block';
        textPreview.innerHTML = 'Loading document preview...';
        
        // Show basic file info
        if (statsPanel) {
            statsPanel.innerHTML = `
                <h4>📄 Document Information</h4>
                <p><strong>File Name:</strong> ${file.name}</p>
                <p><strong>File Size:</strong> ${(file.size / 1024 / 1024).toFixed(2)} MB</p>
                <p><strong>File Type:</strong> ${file.type}</p>
                <p><strong>Last Modified:</strong> ${new Date(file.lastModified).toLocaleString()}</p>
            `;
        }
        
        // For text files, show preview
        if (file.type === 'text/plain') {
            const reader = new FileReader();
            reader.onload = function(e) {
                const content = e.target.result;
                textPreview.innerHTML = content.substring(0, 500) + (content.length > 500 ? '...' : '');
            };
            reader.readAsText(file);
        } else {
            textPreview.innerHTML = 'Preview not available for this file type. Upload to process the document.';
        }
    }
}

// Summary regeneration functions
function regenerateSummary() {
    if (!currentDocument) {
        alert('No document loaded. Please upload a document first.');
        return;
    }
    
    const newType = document.getElementById('new-summary-type').value;
    const newLength = document.getElementById('new-summary-length').value;
    
    showProcessingIndicator();
    
    fetch('/api/regenerate-summary', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: currentDocument.session_id,
            summary_type: newType,
            summary_length: newLength
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            updateSummaryDisplay(data.summary);
            currentSummary = data.summary;
            showSuccessMessage('Summary regenerated successfully!');
        } else {
            showErrorMessage('Error regenerating summary: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred while regenerating summary');
    });
}

function analyzeDocument() {
    if (!currentDocument) {
        alert('No document loaded. Please upload a document first.');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/analyze-document', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: currentDocument.session_id
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            showAnalysisResults(data.analysis);
            showSuccessMessage('Document analysis completed!');
        } else {
            showErrorMessage('Error analyzing document: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred during analysis');
    });
}

// Comparison functions
function showComparisonTool() {
    const tool = document.getElementById('comparison-tool');
    const btn = document.getElementById('show-comparison-btn');
    
    if (tool) {
        if (tool.style.display === 'none') {
            tool.style.display = 'block';
            btn.textContent = 'Hide Comparison Tool';
        } else {
            tool.style.display = 'none';
            btn.textContent = 'Show Comparison Tool';
        }
    }
}

function compareSummaries() {
    if (!currentDocument) {
        alert('No document loaded. Please upload a document first.');
        return;
    }
    
    const typeA = document.getElementById('compare-type-a').value;
    const typeB = document.getElementById('compare-type-b').value;
    
    showProcessingIndicator();
    
    fetch('/api/compare-summaries', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: currentDocument.session_id,
            summary_type_a: typeA,
            summary_type_b: typeB
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            document.getElementById('summary-a').innerHTML = data.summary_a;
            document.getElementById('summary-b').innerHTML = data.summary_b;
            showSuccessMessage('Summary comparison completed!');
        } else {
            showErrorMessage('Error comparing summaries: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred during comparison');
    });
}

// Session management functions
function loadSessions() {
    fetch('/api/get-sessions')
    .then(response => response.json())
    .then(data => {
        if (data.sessions && data.sessions.length > 0) {
            documentSessions = {};
            
            // Convert array to object and find most recent
            let mostRecentSession = null;
            let mostRecentTime = 0;
            
            data.sessions.forEach(session => {
                documentSessions[session.id] = session;
                
                const sessionTime = new Date(session.timestamp).getTime();
                if (sessionTime > mostRecentTime) {
                    mostRecentTime = sessionTime;
                    mostRecentSession = session;
                }
            });
            
            // Set the most recent session as current if none is set
            if (!currentDocument && mostRecentSession) {
                currentDocument = { session_id: mostRecentSession.id };
            }
            
            updateSessionsList();
            updateSessionStats();
        }
    })
    .catch(error => {
        console.error('Error loading sessions:', error);
    });
}

function updateSessionsList() {
    const sessionsList = document.getElementById('sessions-list');
    if (!sessionsList) return;
    
    if (Object.keys(documentSessions).length === 0) {
        sessionsList.innerHTML = '<div>No documents processed yet. Upload a document to create your first session.</div>';
        return;
    }
    
    let html = '';
    for (const [sessionId, session] of Object.entries(documentSessions)) {
        html += `
            <div class="session-item" data-session-id="${sessionId}">
                <div>
                    <div class="session-title">${session.filename || 'Unknown Document'}</div>
                    <div class="session-date">${new Date(session.timestamp).toLocaleString()}</div>
                    <small>Type: ${session.summary_type || 'General'} | Length: ${session.summary_length || 'Medium'}</small>
                </div>
                <div class="session-actions">
                    <button class="button btn-small" onclick="loadSession('${sessionId}')">Load</button>
                    <button class="button btn-small btn-secondary" onclick="downloadSession('${sessionId}')">Download</button>
                    <button class="button btn-small btn-danger" onclick="deleteSession('${sessionId}')">Delete</button>
                </div>
            </div>
        `;
    }
    
    sessionsList.innerHTML = html;
}

function updateSessionStats() {
    const statsPanel = document.getElementById('session-stats');
    const statsContent = document.getElementById('stats-content');
    
    if (!statsPanel || !statsContent) return;
    
    if (Object.keys(documentSessions).length === 0) {
        statsPanel.style.display = 'none';
        return;
    }
    
    statsPanel.style.display = 'block';
    
    const totalSessions = Object.keys(documentSessions).length;
    const summaryTypes = {};
    let totalDocuments = 0;
    
    for (const session of Object.values(documentSessions)) {
        totalDocuments++;
        const type = session.summary_type || 'general';
        summaryTypes[type] = (summaryTypes[type] || 0) + 1;
    }
    
    let html = `
        <div class="two-column">
            <div>
                <h5>📊 Session Statistics</h5>
                <ul>
                    <li>Total Sessions: ${totalSessions}</li>
                    <li>Documents Processed: ${totalDocuments}</li>
                    <li>Most Used Type: ${getMostUsedType(summaryTypes)}</li>
                </ul>
            </div>
            <div>
                <h5>📈 Summary Types</h5>
                <ul>
    `;
    
    for (const [type, count] of Object.entries(summaryTypes)) {
        html += `<li>${type.charAt(0).toUpperCase() + type.slice(1)}: ${count}</li>`;
    }
    
    html += `
                </ul>
            </div>
        </div>
    `;
    
    statsContent.innerHTML = html;
}

function getMostUsedType(types) {
    let maxCount = 0;
    let mostUsed = 'None';
    
    for (const [type, count] of Object.entries(types)) {
        if (count > maxCount) {
            maxCount = count;
            mostUsed = type;
        }
    }
    
    return mostUsed.charAt(0).toUpperCase() + mostUsed.slice(1);
}

function loadSession(sessionId) {
    if (!documentSessions[sessionId]) {
        showErrorMessage('Session not found');
        return;
    }
    
    const session = documentSessions[sessionId];
    currentDocument = session;
    currentSummary = session.summary;
    
    // Update summary display
    updateSummaryDisplay(session.summary);
    
    // Show regeneration panel
    const regenPanel = document.getElementById('regeneration-panel');
    if (regenPanel) {
        regenPanel.style.display = 'block';
    }
    
    showSuccessMessage(`Loaded session: ${session.filename}`);
}

function downloadSession(sessionId) {
    const downloadUrl = `/api/download-session/${sessionId}`;
    
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `session_${sessionId}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) {
        return;
    }
    
    fetch(`/api/delete-session/${sessionId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            delete documentSessions[sessionId];
            updateSessionsList();
            updateSessionStats();
            showSuccessMessage('Session deleted successfully');
        } else {
            showErrorMessage('Error deleting session: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred while deleting session');
    });
}

// Upload document specifically for comparison
function uploadComparisonDocument() {
    const fileInput = document.getElementById('comparison_file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to upload');
        return;
    }
    
    if (!validateFile(file)) {
        return;
    }
    
    const formData = new FormData();
    formData.append('document_file', file);
    
    showProcessingIndicator();
    
    fetch('/api/upload-document', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            currentComparisonSession = data.session_id;
            
            // Show the comparison tool
            document.getElementById('comparison-tool').style.display = 'block';
            
            showSuccessMessage(`Document uploaded successfully: ${data.filename}`);
        } else {
            showErrorMessage('Upload failed: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred during upload');
    });
}

// Generate comparison summaries
function generateComparisonSummaries() {
    if (!currentComparisonSession) {
        alert('Please upload a document first');
        return;
    }
    
    const settings1 = {
        type: document.getElementById('compare-type-a').value,
        length: document.getElementById('compare-length-a').value,
        tone: document.getElementById('compare-tone-a').value
    };
    
    const settings2 = {
        type: document.getElementById('compare-type-b').value,
        length: document.getElementById('compare-length-b').value,
        tone: document.getElementById('compare-tone-b').value
    };
    
    showProcessingIndicator();
    
    fetch('/api/compare-summaries', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: currentComparisonSession,
            settings1: settings1,
            settings2: settings2
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            document.getElementById('summary-a').innerHTML = data.summary1;
            document.getElementById('summary-b').innerHTML = data.summary2;
            document.getElementById('comparison-results').style.display = 'block';
            
            showSuccessMessage('Comparison summaries generated successfully!');
        } else {
            showErrorMessage('Error generating summaries: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred during comparison');
    });
}

// Fixed export function - this should work after document processing
function exportCurrentSummary(format) {
    // First check if there's a current session from the main form
    let sessionToExport = null;
    
    // Check if we have a current document session from the main form
    if (currentDocument && currentDocument.session_id) {
        sessionToExport = currentDocument.session_id;
    }
    // Check if we have a comparison session
    else if (currentComparisonSession) {
        sessionToExport = currentComparisonSession;
    }
    // Check if there are any sessions available
    else if (Object.keys(documentSessions).length > 0) {
        // Use the most recent session
        const sessionIds = Object.keys(documentSessions);
        sessionToExport = sessionIds[sessionIds.length - 1];
    }
    
    if (!sessionToExport) {
        alert('No summary available to export. Please upload and process a document first.');
        return;
    }
    
    // Use direct URL approach for download
    const exportUrl = `/api/export-summary/${sessionToExport}/${format}`;
    
    // Create temporary link and trigger download
    const link = document.createElement('a');
    link.href = exportUrl;
    link.download = `summary_${sessionToExport}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showSuccessMessage(`Summary exported as ${format.toUpperCase()}`);
}

// Update the main form submission to set currentDocument properly
function handleMainFormSubmission() {
    const form = document.getElementById('upload-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            // Let the form submit normally, but track the result
            setTimeout(() => {
                // After form submission, check if there's a new session
                loadSessions();
            }, 2000);
        });
    }
}

// UI Helper functions
function updateSummaryDisplay(summary) {
    const summaryDisplay = document.querySelector('.summary-display');
    if (summaryDisplay && summary) {
        summaryDisplay.innerHTML = summary;
    }
}

function showAnalysisResults(analysis) {
    // Create or update analysis display
    let analysisDiv = document.getElementById('analysis-results');
    if (!analysisDiv) {
        analysisDiv = document.createElement('div');
        analysisDiv.id = 'analysis-results';
        analysisDiv.className = 'settings-panel';
        
        const comparisonSection = document.getElementById('comparison-section');
        if (comparisonSection) {
            comparisonSection.appendChild(analysisDiv);
        }
    }
    
    analysisDiv.innerHTML = `
        <h4>🔍 Document Analysis Results</h4>
        <div class="two-column">
            <div>
                <h5>Content Analysis</h5>
                <p>${analysis.content_analysis || 'No content analysis available'}</p>
            </div>
            <div>
                <h5>Key Insights</h5>
                <ul>
                    ${(analysis.key_insights || []).map(insight => `<li>${insight}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
}

function showProcessingIndicator() {
    processingInProgress = true;
    
    // Disable all buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = true);
    
    // Show loading spinner if available
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'block';
    }
    
    // Update button text for main submit
    const submitBtn = document.querySelector('input[type="submit"]');
    if (submitBtn) {
        submitBtn.value = 'Processing...';
    }
}

function hideProcessingIndicator() {
    processingInProgress = false;
    
    // Re-enable all buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => btn.disabled = false);
    
    // Hide loading spinner
    const spinner = document.querySelector('.loading-spinner');
    if (spinner) {
        spinner.style.display = 'none';
    }
    
    // Reset button text
    const submitBtn = document.querySelector('input[type="submit"]');
    if (submitBtn) {
        submitBtn.value = 'Upload & Summarize';
    }
}

function showSuccessMessage(message) {
    showMessage(message, 'success');
}

function showErrorMessage(message) {
    showMessage(message, 'error');
}

function showMessage(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at top of main body
    const mainBody = document.querySelector('.mainBody');
    if (mainBody) {
        mainBody.insertBefore(alert, mainBody.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}