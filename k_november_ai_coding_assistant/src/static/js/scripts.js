// scripts.js - Complete JavaScript for AI Programming Assistant

// Global variables
let currentCode = null;
let currentSuggestion = null;
let codingSessions = {};
let processingInProgress = false;
let supportedFileTypes = [];
let monacoEditor = null;
let completionProvider = null;
let languageFeatureProvider = null;

// Document ready initialization
document.addEventListener('DOMContentLoaded', function() {
    setupBackToTop();
    initializeMonacoEditor();
    loadSupportedFileTypes();
    loadSessions();
    updateCodeStats();
    updateSessionStats();
    setupFormHandling();
});

// Setup form handling
function setupFormHandling() {
    const assistanceTypeSelect = document.getElementById('assistance_type');
    if (assistanceTypeSelect) {
        assistanceTypeSelect.addEventListener('change', function() {
            toggleAssistanceFields(this.value);
        });
        // Initial setup
        toggleAssistanceFields(assistanceTypeSelect.value);
    }
}

// Toggle assistance type fields
function toggleAssistanceFields(type) {
    const contextGroup = document.getElementById('context-group');
    const errorGroup = document.getElementById('error-group');
    const docTypeGroup = document.getElementById('doc-type-group');
    
    // Hide all optional fields first
    if (contextGroup) contextGroup.style.display = 'none';
    if (errorGroup) errorGroup.style.display = 'none';
    if (docTypeGroup) docTypeGroup.style.display = 'none';
    
    // Show relevant fields based on type
    if (type === 'suggestion' || type === 'completion') {
        if (contextGroup) contextGroup.style.display = 'block';
    } else if (type === 'error_explanation') {
        if (errorGroup) errorGroup.style.display = 'block';
    } else if (type === 'documentation') {
        if (docTypeGroup) docTypeGroup.style.display = 'block';
    }
}

// Initialize Monaco Editor
function initializeMonacoEditor() {
    const container = document.getElementById('monaco-editor-container');
    if (!container) {
        console.error('Monaco editor container not found');
        return;
    }
    
    const loadingOverlay = document.createElement('div');
    loadingOverlay.style.cssText = 'position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);color:white;display:flex;align-items:center;justify-content:center;z-index:1000;';
    loadingOverlay.innerHTML = '<div>Loading Monaco Editor...</div>';
    container.appendChild(loadingOverlay);

    require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
    
    require(['vs/editor/editor.main'], function () {
        try {
            if (loadingOverlay && loadingOverlay.parentNode) {
                loadingOverlay.parentNode.removeChild(loadingOverlay);
            }

            monacoEditor = monaco.editor.create(container, {
                value: '# Write your code here\n',
                language: 'python',
                theme: 'vs-dark',
                automaticLayout: true,
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: 'on',
                roundedSelection: false,
                scrollBeyondLastLine: false,
                readOnly: false,
                cursorStyle: 'line',
                wordWrap: 'on',
                suggestOnTriggerCharacters: true,
                quickSuggestions: {
                    other: true,
                    comments: false,
                    strings: false
                },
                parameterHints: { enabled: true },
                suggestSelection: 'first',
                tabCompletion: 'on',
                acceptSuggestionOnCommitCharacter: true,
                acceptSuggestionOnEnter: 'on'
            });

            monacoEditor.onDidChangeModelContent(() => {
                const codeInput = document.getElementById('code_input');
                if (codeInput) {
                    codeInput.value = monacoEditor.getValue();
                }
                updateCodeStats();
            });

            const languageSelect = document.getElementById('programming_language');
            if (languageSelect) {
                languageSelect.addEventListener('change', function() {
                    const language = this.value;
                    const monacoLang = getMonacoLanguage(language);
                    const model = monacoEditor.getModel();
                    if (model) {
                        monaco.editor.setModelLanguage(model, monacoLang);
                    }
                });
            }

            setupMonacoEventListeners();
            registerAICompletionProvider();
            registerLanguageFeatures();

            console.log('Monaco Editor initialized successfully');
            
        } catch (error) {
            console.error('Error initializing Monaco Editor:', error);
            if (loadingOverlay && loadingOverlay.parentNode) {
                loadingOverlay.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }
    }, function(err) {
        console.error('Error loading Monaco Editor:', err);
        if (loadingOverlay && loadingOverlay.parentNode) {
            loadingOverlay.innerHTML = `<p style="color: red;">Failed to load Monaco Editor. Please refresh.</p>`;
        }
    });
}

function setupMonacoEventListeners() {
    if (!monacoEditor) return;
    
    monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, function() {
        monacoEditor.trigger('keyboard', 'editor.action.triggerSuggest', {});
    });

    monacoEditor.addAction({
        id: 'ai-suggestion',
        label: 'Get AI Suggestion',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space],
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 1,
        run: function() {
            monacoEditor.trigger('keyboard', 'editor.action.triggerSuggest', {});
        }
    });

    monacoEditor.addAction({
        id: 'explain-code',
        label: 'Explain Selected Code',
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 2,
        run: function() {
            const selection = monacoEditor.getSelection();
            const selectedText = monacoEditor.getModel().getValueInRange(selection);
            if (selectedText) {
                explainCodeSnippet(selectedText);
            }
        }
    });
}

function registerAICompletionProvider() {
    if (!monaco || !monacoEditor) return;
    
    const languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust'];
    
    languages.forEach(language => {
        try {
            monaco.languages.registerCompletionItemProvider(language, {
                triggerCharacters: ['.', ' ', '(', '[', '{'],
                provideCompletionItems: async function(model, position) {
                    return await getAICompletionItems(model, position);
                }
            });
        } catch (error) {
            console.error(`Error registering completion for ${language}:`, error);
        }
    });
}

function registerLanguageFeatures() {
    if (!monaco || !monacoEditor) return;
    
    const languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust'];
    
    languages.forEach(language => {
        try {
            monaco.languages.registerHoverProvider(language, {
                provideHover: async function(model, position) {
                    const word = model.getWordAtPosition(position);
                    if (!word) return null;
                    
                    try {
                        const response = await fetch('/api/ai-hover', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                code: model.getValue(),
                                word: word.word,
                                line: position.lineNumber,
                                language: getSelectedLanguage()
                            })
                        });
                        
                        const data = await response.json();
                        if (data.success && data.info) {
                            return { contents: [{ value: data.info }] };
                        }
                    } catch (error) {
                        console.error('Hover error:', error);
                    }
                    
                    return null;
                }
            });
        } catch (error) {
            console.error(`Error registering hover for ${language}:`, error);
        }
    });
}

async function getAICompletionItems(model, position) {
    const lineContent = model.getLineContent(position.lineNumber);
    const textUntilPosition = lineContent.substring(0, position.column - 1);
    const allText = model.getValue();
    const language = getSelectedLanguage();
    
    const allLines = allText.split('\n');
    const currentLineIndex = position.lineNumber - 1;
    const contextStart = Math.max(0, currentLineIndex - 5);
    const contextLines = allLines.slice(contextStart, currentLineIndex + 1);
    const codeContext = contextLines.join('\n');
    
    try {
        const response = await fetch('/api/ai-completions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: allText,
                language: language,
                line: position.lineNumber,
                column: position.column,
                current_line: lineContent,
                text_until_position: textUntilPosition,
                context_lines: codeContext
            })
        });

        if (!response.ok) {
            return { suggestions: [] };
        }

        const data = await response.json();
        
        if (data.success && data.completions && data.completions.length > 0) {
            return {
                suggestions: data.completions.map((suggestion, index) => ({
                    label: suggestion.label || suggestion.text || '',
                    kind: monaco.languages.CompletionItemKind[suggestion.kind] || monaco.languages.CompletionItemKind.Text,
                    documentation: {
                        value: suggestion.documentation || 'AI-powered suggestion',
                        isTrusted: true
                    },
                    insertText: suggestion.insertText || suggestion.text || suggestion.label,
                    range: {
                        startLineNumber: position.lineNumber,
                        endLineNumber: position.lineNumber,
                        startColumn: position.column - (suggestion.replaceLength || 0),
                        endColumn: position.column
                    },
                    sortText: `0${index.toString().padStart(3, '0')}`,
                    detail: `🤖 ${suggestion.detail || 'AI Suggestion'}`,
                    preselect: index === 0
                }))
            };
        }
        
        return { suggestions: [] };
        
    } catch (error) {
        console.error('Error getting AI completions:', error);
        return { suggestions: [] };
    }
}

function explainCodeSnippet(code) {
    const language = getSelectedLanguage();
    
    showProcessingIndicator();
    
    fetch('/api/explain-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code, language: language })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        
        if (data.success) {
            updateSuggestionDisplay(data.explanation);
            showSuccessMessage('Code explanation generated!');
        } else {
            showErrorMessage(data.error || 'Failed to explain code');
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        showErrorMessage('Error explaining code: ' + error.message);
    });
}

function getSelectedLanguage() {
    const languageSelect = document.getElementById('programming_language');
    return languageSelect ? languageSelect.value : 'python';
}

function getMonacoLanguage(language) {
    const languageMap = {
        'python': 'python',
        'javascript': 'javascript',
        'typescript': 'typescript',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'csharp': 'csharp',
        'php': 'php',
        'ruby': 'ruby',
        'go': 'go',
        'rust': 'rust',
        'swift': 'swift',
        'kotlin': 'kotlin',
        'scala': 'scala',
        'html': 'html',
        'css': 'css',
        'sql': 'sql',
        'bash': 'shell'
    };
    return languageMap[language] || 'plaintext';
}

function updateCodeStats() {
    const codeInput = document.getElementById('code_input');
    const statsDiv = document.getElementById('code-stats');
    
    if (!codeInput || !statsDiv) return;
    
    const code = codeInput.value || '';
    if (code.trim().length === 0) {
        statsDiv.style.display = 'none';
        return;
    }
    
    statsDiv.style.display = 'block';
    
    const lines = code.split('\n').length;
    const chars = code.length;
    const words = code.trim().split(/\s+/).length;
    
    statsDiv.querySelector('.stat-item:nth-child(1)').textContent = `Lines: ${lines}`;
    statsDiv.querySelector('.stat-item:nth-child(2)').textContent = `Characters: ${chars}`;
    statsDiv.querySelector('.stat-item:nth-child(3)').textContent = `Words: ${words}`;
}

function loadSessions() {
    fetch('/api/get-sessions')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.sessions && data.sessions.length > 0) {
            codingSessions = {};
            
            data.sessions.forEach(session => {
                codingSessions[session.id] = session;
            });
            
            updateSessionsList();
            updateSessionStats();
        } else {
            updateSessionsList();
        }
    })
    .catch(error => {
        console.error('Error loading sessions:', error);
    });
}

function loadSupportedFileTypes() {
    fetch('/api/get-supported-file-types')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            supportedFileTypes = data.file_types;
        }
    })
    .catch(error => {
        console.error('Error loading file types:', error);
    });
}

function updateSessionStats() {
    const statsPanel = document.getElementById('session-stats');
    const statsContent = document.getElementById('stats-content');
    
    if (!statsPanel || !statsContent) return;
    
    if (Object.keys(codingSessions).length === 0) {
        statsPanel.style.display = 'none';
        return;
    }
    
    statsPanel.style.display = 'block';
    
    const totalSessions = Object.keys(codingSessions).length;
    const languages = {};
    let totalCodeLines = 0;
    
    for (const session of Object.values(codingSessions)) {
        const language = session.language || 'unknown';
        languages[language] = (languages[language] || 0) + 1;
        totalCodeLines += session.code_length || 0;
    }
    
    const mostUsed = Object.entries(languages).sort((a, b) => b[1] - a[1])[0];
    
    let html = `
        <div>
            <h5>📊 Session Statistics</h5>
            <ul>
                <li>Total Sessions: ${totalSessions}</li>
                <li>Total Characters: ${totalCodeLines}</li>
                <li>Most Used Language: ${mostUsed ? mostUsed[0].toUpperCase() : 'None'}</li>
            </ul>
        </div>
    `;
    
    statsContent.innerHTML = html;
}

function updateSessionsList() {
    const sessionsList = document.querySelector('.sessions-list');
    if (!sessionsList) return;
    
    if (Object.keys(codingSessions).length === 0) {
        sessionsList.innerHTML = '<div>No coding sessions yet. Start coding above to create your first session.</div>';
        return;
    }
    
    let sessionsHTML = '';
    Object.entries(codingSessions).forEach(([sessionId, session]) => {
        const date = new Date(session.timestamp).toLocaleString();
        const type = session.type.replace('_', ' ').toUpperCase();
        
        sessionsHTML += `
            <div class="session-item">
                <div class="session-info">
                    <div class="session-title">${sessionId}</div>
                    <div class="session-date">${date}</div>
                    <div class="session-details">
                        ${type} • ${session.language.toUpperCase()} • ${session.code_content.length} chars
                    </div>
                </div>
                <div class="session-actions">
                    <button onclick="loadSession('${sessionId}')" class="btn btn-secondary">Load</button>
                    <button onclick="downloadSession('${sessionId}')" class="btn btn-info">TXT</button>
                    <button onclick="downloadSessionMarkdown('${sessionId}')" class="btn btn-success">MD</button>
                    <button onclick="deleteSession('${sessionId}')" class="btn btn-danger">Delete</button>
                </div>
            </div>
        `;
    });
    
    sessionsList.innerHTML = sessionsHTML;
}

function downloadSession(sessionId) {
    try {
        const link = document.createElement('a');
        link.href = `/api/download-session/${sessionId}/txt`;
        link.download = `${sessionId}_session_summary.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showSuccessMessage('Session downloaded as TXT!');
    } catch (error) {
        showErrorMessage('Failed to download session');
    }
}

function downloadSessionMarkdown(sessionId) {
    try {
        const link = document.createElement('a');
        link.href = `/api/download-session/${sessionId}/markdown`;
        link.download = `${sessionId}_session_summary.md`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showSuccessMessage('Session downloaded as Markdown!');
    } catch (error) {
        showErrorMessage('Failed to download session');
    }
}

function deleteSession(sessionId) {
    if (!confirm('Delete this session?')) return;
    
    fetch(`/api/delete-session/${sessionId}`, { method: 'DELETE' })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            delete codingSessions[sessionId];
            updateSessionsList();
            updateSessionStats();
            showSuccessMessage('Session deleted');
        } else {
            showErrorMessage('Error deleting session');
        }
    })
    .catch(error => {
        showErrorMessage('Network error');
    });
}

function loadSession(sessionId) {
    if (!codingSessions[sessionId]) {
        showErrorMessage('Session not found');
        return;
    }
    
    const session = codingSessions[sessionId];
    currentCode = { session_id: sessionId };
    
    if (monacoEditor && session.code_content) {
        monacoEditor.setValue(session.code_content);
    }
    
    const languageSelect = document.getElementById('programming_language');
    if (languageSelect && session.language) {
        languageSelect.value = session.language;
    }
    
    updateSuggestionDisplay(session.suggestion || 'No suggestion available');
    updateCodeStats();
    showSuccessMessage(`Session ${sessionId} loaded!`);
}

function getCodeSuggestion() {
    const code = monacoEditor ? monacoEditor.getValue() : document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const context = document.getElementById('context').value;
    
    if (!code.trim()) {
        showErrorMessage('Please enter some code first');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/code-suggestion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language, context })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            updateSuggestionDisplay(data.suggestion);
            loadSessions();
            showSuccessMessage('Code suggestion generated!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        showErrorMessage('Network error');
    });
}

function explainError() {
    const code = monacoEditor ? monacoEditor.getValue() : document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const errorMessage = document.getElementById('error_message').value;
    
    if (!errorMessage.trim()) {
        showErrorMessage('Please enter an error message');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/explain-error', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, error: errorMessage, language })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            updateSuggestionDisplay(data.explanation);
            loadSessions();
            showSuccessMessage('Error explanation generated!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        showErrorMessage('Network error');
    });
}

function updateSuggestionDisplay(content) {
    const display = document.querySelector('.summary-display');
    if (display) {
        display.innerHTML = content.replace(/\n/g, '<br>');
    }
}

function showSuccessMessage(msg) {
    showMessage(msg, 'success');
}

function showErrorMessage(msg) {
    showMessage(msg, 'error');
}

function showMessage(msg, type) {
    const existing = document.querySelectorAll('.alert');
    existing.forEach(a => a.remove());
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = msg;
    
    const mainBody = document.querySelector('.mainBody');
    if (mainBody) {
        mainBody.insertBefore(alert, mainBody.firstChild);
        setTimeout(() => alert.remove(), 5000);
    }
}

function showProcessingIndicator() {
    processingInProgress = true;
    document.querySelectorAll('button').forEach(b => b.disabled = true);
    showMessage('Processing...', 'info');
}

function hideProcessingIndicator() {
    processingInProgress = false;
    document.querySelectorAll('button').forEach(b => b.disabled = false);
    document.querySelectorAll('.alert-info').forEach(a => a.remove());
}

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function setupBackToTop() {
    const btn = document.getElementById('back-to-top');
    if (btn) {
        window.addEventListener('scroll', () => {
            btn.style.display = window.pageYOffset > 500 ? 'block' : 'none';
        });
    }
}