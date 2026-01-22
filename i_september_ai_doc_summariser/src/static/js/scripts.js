// scripts.js - Complete JavaScript for Document Summarizer

// Global variables
let currentDocument = null;
let currentSummary = null;
let documentSessions = {};
let processingInProgress = false;

// Global variable to track current comparison session
let currentComparisonSession = null;

// Store current session ID globally
let currentSessionId = null;

// Document upload functionality
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const submitButton = uploadForm.querySelector('button[type="submit"]');
            
            // Disable submit button
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = 'Processing...';
            }
            
            try {
                const response = await fetch('/api/upload-document', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Store session ID globally
                    currentSessionId = data.session_id;
                    console.log('Session ID stored:', currentSessionId);
                    
                    // Display summary
                    const summaryDisplay = document.querySelector('.summary-display');
                    if (summaryDisplay) {
                        summaryDisplay.innerHTML = data.summary;
                        summaryDisplay.classList.add('ai-result-text');
                    }
                    
                    // Show regeneration panel
                    const regenerationPanel = document.getElementById('regeneration-panel');
                    if (regenerationPanel) {
                        regenerationPanel.style.display = 'block';
                    }
                    
                    // Update document preview if exists
                    const docPreview = document.getElementById('document-preview');
                    if (docPreview) {
                        docPreview.style.display = 'block';
                        const previewText = document.getElementById('document-text-preview');
                        if (previewText) {
                            previewText.textContent = data.document_text;
                        }
                        
                        const stats = document.getElementById('document-stats');
                        if (stats) {
                            stats.innerHTML = `
                                <p><strong>Filename:</strong> ${data.filename}</p>
                                <p><strong>Word Count:</strong> ${data.word_count.toLocaleString()}</p>
                                <p><strong>File Size:</strong> ${data.file_size_mb} MB</p>
                                <p><strong>Full Text Length:</strong> ${data.full_text_length.toLocaleString()} characters</p>
                            `;
                        }
                    }
                    
                    // Load sessions
                    loadSessions();
                    loadStats();
                    
                    alert('Document processed successfully!');
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error uploading document: ' + error.message);
            } finally {
                // Re-enable submit button
                if (submitButton) {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Generate Summary';
                }
            }
        });
    }
});

// Function to regenerate summary
async function regenerateSummary() {
    if (!currentSessionId) {
        alert('Please upload a document first');
        console.error('No session ID available');
        return;
    }
    
    console.log('Regenerating summary for session:', currentSessionId);
    
    const newType = document.getElementById('new-summary-type')?.value || 'general';
    const newLength = document.getElementById('new-summary-length')?.value || 'medium';
    const newTone = document.getElementById('new-summary-tone')?.value || 'neutral';
    
    try {
        const response = await fetch('/api/regenerate-summary', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                summary_type: newType,
                summary_length: newLength,
                summary_tone: newTone
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update summary display
            const summaryDisplay = document.querySelector('.summary-display');
            if (summaryDisplay) {
                summaryDisplay.innerHTML = data.summary;
                summaryDisplay.classList.add('ai-result-text');
            }
            alert('Summary regenerated successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error regenerating summary: ' + error.message);
    }
}

// Function to analyze document
async function analyzeDocument() {
    if (!currentSessionId) {
        alert('Please upload a document first');
        console.error('No session ID available');
        return;
    }
    
    console.log('Analyzing document for session:', currentSessionId);
    
    try {
        const response = await fetch('/api/analyze-document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSessionId
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Display analysis in a modal or alert
            const analysisText = data.analysis;
            
            // Create a modal or use alert
            alert('Document Analysis:\n\n' + analysisText);
            
            // Or you could create a nicer modal display
            // showAnalysisModal(analysisText);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error analyzing document: ' + error.message);
    }
}

// Function to export current summary
function exportCurrentSummary(format) {
    if (!currentSessionId) {
        alert('Please upload and generate a summary first');
        console.error('No session ID available for export');
        return;
    }
    
    console.log(`Exporting summary for session ${currentSessionId} as ${format}`);
    
    // Direct download via URL
    window.location.href = `/api/export-summary/${currentSessionId}/${format}`;
}

// Function to load sessions list
async function loadSessions() {
    try {
        const response = await fetch('/api/get-sessions');
        const data = await response.json();
        
        const sessionsList = document.getElementById('sessions-list');
        if (!sessionsList) return;
        
        if (data.sessions && data.sessions.length > 0) {
            sessionsList.innerHTML = '';
            
            data.sessions.forEach(session => {
                const sessionDiv = document.createElement('div');
                sessionDiv.className = 'session-item';
                sessionDiv.innerHTML = `
                    <h4>${session.filename}</h4>
                    <p><strong>Time:</strong> ${new Date(session.timestamp).toLocaleString()}</p>
                    <p><strong>Words:</strong> ${session.word_count.toLocaleString()}</p>
                    <p><strong>Summary Type:</strong> ${session.summary_settings?.type || 'N/A'}</p>
                    <button onclick="viewSession('${session.id}')">View</button>
                    <button onclick="downloadSession('${session.id}')">Download</button>
                    <button onclick="deleteSession('${session.id}')">Delete</button>
                `;
                sessionsList.appendChild(sessionDiv);
            });
        } else {
            sessionsList.innerHTML = '<div>No documents processed yet. Upload a document to create your first session.</div>';
        }
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

// Function to load statistics
async function loadStats() {
    try {
        const response = await fetch('/api/get-document-stats');
        const data = await response.json();
        
        const statsContent = document.getElementById('stats-content');
        const statsPanel = document.getElementById('session-stats');
        
        if (statsContent && data.total_documents > 0) {
            statsPanel.style.display = 'block';
            
            let typeDistribution = '';
            for (const [type, count] of Object.entries(data.summary_type_distribution)) {
                typeDistribution += `<li>${type}: ${count}</li>`;
            }
            
            statsContent.innerHTML = `
                <p><strong>Total Documents:</strong> ${data.total_documents}</p>
                <p><strong>Total Words Processed:</strong> ${data.total_words_processed.toLocaleString()}</p>
                <p><strong>Average Words per Document:</strong> ${Math.round(data.average_words_per_document).toLocaleString()}</p>
                <p><strong>Summary Types Used:</strong></p>
                <ul>${typeDistribution}</ul>
            `;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Function to view a specific session
async function viewSession(sessionId) {
    try {
        const response = await fetch(`/api/get-session/${sessionId}`);
        const data = await response.json();
        
        if (data.success) {
            // Set as current session
            currentSessionId = sessionId;
            
            // Update display
            const summaryDisplay = document.querySelector('.summary-display');
            if (summaryDisplay) {
                summaryDisplay.innerHTML = data.session.summary;
                summaryDisplay.classList.add('ai-result-text');
            }
            
            // Show regeneration panel
            const regenerationPanel = document.getElementById('regeneration-panel');
            if (regenerationPanel) {
                regenerationPanel.style.display = 'block';
            }
            
            // Scroll to results
            document.getElementById('results-section')?.scrollIntoView({ behavior: 'smooth' });
        }
    } catch (error) {
        console.error('Error viewing session:', error);
        alert('Error loading session');
    }
}

// Function to download session
function downloadSession(sessionId) {
    window.location.href = `/api/download-session/${sessionId}`;
}

// Function to delete session
async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this session?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/delete-session/${sessionId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Session deleted successfully');
            loadSessions();
            loadStats();
            
            // If this was the current session, clear it
            if (currentSessionId === sessionId) {
                currentSessionId = null;
                const summaryDisplay = document.querySelector('.summary-display');
                if (summaryDisplay) {
                    summaryDisplay.innerHTML = 'No summary available. Upload a document above to generate an AI summary.';
                }
            }
        } else {
            alert('Error deleting session: ' + data.error);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting session');
    }
}

// Load sessions on page load
document.addEventListener('DOMContentLoaded', function() {
    loadSessions();
    loadStats();
});