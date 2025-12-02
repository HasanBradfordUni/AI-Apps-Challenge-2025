// scripts.js - Complete JavaScript for AI Programming Assistant

// Global variables
let currentCode = null;
let currentSuggestion = null;
let codingSessions = {};
let processingInProgress = false;

// Global variables for supported file types
let supportedFileTypes = [];

// Global variables for Monaco Editor
let monacoEditor = null;
let completionProvider = null;
let languageFeatureProvider = null;

// Document ready initialization
document.addEventListener('DOMContentLoaded', function() {
    setupFloatingHeader();
    setupSmoothScrolling();
    setupBackToTop();
    initializeMonacoEditor();
    loadSupportedFileTypes();
    loadSessions();
    updateCodeStats();
    updateSessionStats();
    setupFormValidation();
});

// Initialize Monaco Editor
function initializeMonacoEditor() {
    // Show loading overlay
    const container = document.getElementById('monaco-editor-container');
    const loadingOverlay = document.createElement('div');
    loadingOverlay.className = 'monaco-loading-overlay';
    loadingOverlay.innerHTML = '<div class="monaco-loading-spinner"></div>Loading Monaco Editor...';
    container.appendChild(loadingOverlay);

    require.config({ paths: { vs: 'https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs' } });
    require(['vs/editor/editor.main'], function () {
        // Remove loading overlay
        container.removeChild(loadingOverlay);
        
        // Create the editor
        monacoEditor = monaco.editor.create(container, {
            value: `# Welcome to the AI Programming Assistant
# Start typing your code here...
# Use Ctrl+Space for AI-powered suggestions!

def hello_world():
    print("Hello, World!")
    return "Welcome to Has AI!"

if __name__ == "__main__":
    message = hello_world()
    print(f"Message: {message}")`,
            language: 'python',
            theme: 'vs-dark',
            fontSize: 14,
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            readOnly: false,
            automaticLayout: true,
            minimap: { enabled: true },
            wordWrap: 'on',
            bracketMatching: 'always',
            autoIndent: 'advanced',
            formatOnPaste: true,
            formatOnType: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnCommitCharacter: true,
            acceptSuggestionOnEnter: 'on',
            tabCompletion: 'on',
            quickSuggestions: {
                other: true,
                comments: true,
                strings: true
            },
            parameterHints: {
                enabled: true
            },
            codeLens: true,
            folding: true,
            renderWhitespace: 'selection'
        });

        // Setup editor event listeners
        setupMonacoEventListeners();
        
        // Register AI completion provider
        registerAICompletionProvider();
        
        // Register language features
        registerLanguageFeatures();
        
        // Update hidden input on change
        monacoEditor.onDidChangeModelContent(() => {
            const code = monacoEditor.getValue();
            document.getElementById('code_input').value = code;
            updateCodeStats();
        });

        // Handle language changes
        const languageSelect = document.getElementById('programming_language');
        if (languageSelect) {
            languageSelect.addEventListener('change', function() {
                const language = this.value;
                monaco.editor.setModelLanguage(monacoEditor.getModel(), getMonacoLanguage(language));
            });
        }

        console.log('Monaco Editor initialized successfully!');
    });
}

// Setup Monaco Editor event listeners
function setupMonacoEventListeners() {
    // Handle Ctrl+Space for AI suggestions
    monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space, function() {
        triggerAISuggestions();
    });

    // Handle Ctrl+Shift+F for formatting
    monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF, function() {
        formatCode();
    });

    // Handle Ctrl+/ for commenting
    monacoEditor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, function() {
        monacoEditor.getAction('editor.action.commentLine').run();
    });

    // Context menu additions
    monacoEditor.addAction({
        id: 'ai-suggestion',
        label: 'Get AI Suggestion',
        keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Space],
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 1,
        run: function() {
            triggerAISuggestions();
        }
    });

    monacoEditor.addAction({
        id: 'explain-code',
        label: 'Explain Selected Code',
        contextMenuGroupId: 'navigation',
        contextMenuOrder: 2,
        run: function() {
            explainSelectedCode();
        }
    });
}

// Register AI completion provider
// Enhanced AI completion provider with better context understanding
function registerAICompletionProvider() {
    const languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust'];
    
    languages.forEach(language => {
        completionProvider = monaco.languages.registerCompletionItemProvider(language, {
            provideCompletionItems: function(model, position) {
                return getAICompletionItems(model, position);
            },
            triggerCharacters: ['.', '(', ' ', '\n', '#', '/', '*', '@', '"', "'"]
        });
    });
}

// Register language features (hover, diagnostics, etc.)
function registerLanguageFeatures() {
    const languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 'go', 'rust'];
    
    languages.forEach(language => {
        // Hover provider for AI explanations
        monaco.languages.registerHoverProvider(language, {
            provideHover: function(model, position) {
                return getAIHoverInfo(model, position);
            }
        });

        // Code action provider for AI fixes
        monaco.languages.registerCodeActionProvider(language, {
            provideCodeActions: function(model, range, context) {
                return getAICodeActions(model, range, context);
            }
        });
    });
}

// Get AI completion items
// Enhanced AI completion items with comment and context awareness
async function getAICompletionItems(model, position) {
    const lineContent = model.getLineContent(position.lineNumber);
    const textUntilPosition = lineContent.substring(0, position.column - 1);
    const textAfterPosition = lineContent.substring(position.column - 1);
    const allText = model.getValue();
    
    // Enhanced trigger conditions - include comments and partial statements
    if (textUntilPosition.trim().length < 1) {
        return { suggestions: [] };
    }

    // Check if we're in a comment and suggest code based on comment content
    const isInComment = checkIfInComment(lineContent, position.column, getSelectedLanguage());
    
    try {
        const suggestions = await getAICodeCompletions(allText, position, textUntilPosition, isInComment);
        
        return {
            suggestions: suggestions.map((suggestion, index) => ({
                label: suggestion.label,
                kind: getCompletionKind(suggestion.kind),
                documentation: {
                    value: suggestion.detail || 'AI-powered suggestion',
                    isTrusted: true
                },
                insertText: suggestion.insertText,
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                range: getInsertionRange(position, textUntilPosition),
                sortText: `${isInComment ? 'A' : 'B'}${index.toString().padStart(3, '0')}`, // Prioritize comment-based suggestions
                filterText: suggestion.filterText || suggestion.label,
                detail: `🤖 AI: ${suggestion.detail || 'Smart completion'}`,
                command: suggestion.command || {
                    id: 'ai-suggestion-applied',
                    title: 'AI Suggestion Applied'
                }
            }))
        };
    } catch (error) {
        console.error('Error getting AI completions:', error);
        return { suggestions: [] };
    }
}

// Check if cursor is in a comment
function checkIfInComment(lineContent, column, language) {
    const textBeforeCursor = lineContent.substring(0, column - 1);
    
    switch (language) {
        case 'python':
            return textBeforeCursor.includes('#');
        case 'javascript':
        case 'typescript':
        case 'java':
        case 'cpp':
        case 'csharp':
            return textBeforeCursor.includes('//') || textBeforeCursor.includes('/*');
        default:
            return false;
    }
}

// Get appropriate completion kind
function getCompletionKind(kindString) {
    const kindMap = {
        'function': monaco.languages.CompletionItemKind.Function,
        'method': monaco.languages.CompletionItemKind.Method,
        'variable': monaco.languages.CompletionItemKind.Variable,
        'class': monaco.languages.CompletionItemKind.Class,
        'interface': monaco.languages.CompletionItemKind.Interface,
        'module': monaco.languages.CompletionItemKind.Module,
        'property': monaco.languages.CompletionItemKind.Property,
        'keyword': monaco.languages.CompletionItemKind.Keyword,
        'snippet': monaco.languages.CompletionItemKind.Snippet,
        'text': monaco.languages.CompletionItemKind.Text,
        'file': monaco.languages.CompletionItemKind.File,
        'reference': monaco.languages.CompletionItemKind.Reference
    };
    
    return kindMap[kindString] || monaco.languages.CompletionItemKind.Text;
}

// Get appropriate insertion range
function getInsertionRange(position, textUntilPosition) {
    const words = textUntilPosition.split(/\s+/);
    const lastWord = words[words.length - 1];
    const wordStart = textUntilPosition.lastIndexOf(lastWord);
    
    return {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: wordStart >= 0 ? wordStart + 1 : position.column,
        endColumn: position.column
    };
}

// Enhanced AI code completions with comment awareness
async function getAICodeCompletions(code, position, context, isInComment = false) {
    const language = getSelectedLanguage();
    
    try {
        const response = await fetch('/api/ai-completions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: code,
                language: language,
                line: position.lineNumber,
                column: position.column,
                context: context,
                is_in_comment: isInComment,
                surrounding_lines: getSurroundingLines(code, position.lineNumber)
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            return data.completions || [];
        } else {
            console.warn('AI completions error:', data.error);
            return getEnhancedStaticCompletions(context, language, isInComment);
        }
    } catch (error) {
        console.warn('Failed to get AI completions, using enhanced fallback:', error);
        return getEnhancedStaticCompletions(context, language, isInComment);
    }
}

// Get surrounding lines for better context
function getSurroundingLines(code, lineNumber) {
    const lines = code.split('\n');
    const start = Math.max(0, lineNumber - 3);
    const end = Math.min(lines.length, lineNumber + 2);
    
    return lines.slice(start, end).join('\n');
}

// Enhanced static completions with comment awareness
function getEnhancedStaticCompletions(context, language, isInComment) {
    const completions = [];
    
    // If in comment, suggest code based on comment content
    if (isInComment) {
        const commentText = context.replace(/[#/\*]/g, '').trim().toLowerCase();
        
        // Comment-driven code suggestions
        if (commentText.includes('function') || commentText.includes('def')) {
            completions.push({
                label: 'function_from_comment',
                insertText: generateFunctionFromComment(commentText, language),
                detail: 'Function based on comment',
                kind: 'function'
            });
        }
        
        if (commentText.includes('loop') || commentText.includes('iterate')) {
            completions.push({
                label: 'loop_from_comment',
                insertText: generateLoopFromComment(commentText, language),
                detail: 'Loop based on comment',
                kind: 'snippet'
            });
        }
        
        if (commentText.includes('class') || commentText.includes('object')) {
            completions.push({
                label: 'class_from_comment',
                insertText: generateClassFromComment(commentText, language),
                detail: 'Class based on comment',
                kind: 'class'
            });
        }
    }
    
    // Regular language-specific completions
    if (language === 'python') {
        addPythonCompletions(completions, context);
    } else if (language === 'javascript') {
        addJavaScriptCompletions(completions, context);
    }
    
    return completions;
}

// Generate function from comment
function generateFunctionFromComment(commentText, language) {
    const words = commentText.split(' ');
    const functionName = words.find(word => !['function', 'def', 'create', 'make'].includes(word)) || 'newFunction';
    
    switch (language) {
        case 'python':
            return `def ${functionName}(\${1:parameters}):\n    """${commentText}\n    \n    Args:\n        \${1:parameters}: Description\n    \n    Returns:\n        Description\n    """\n    \${0:pass}`;
        case 'javascript':
            return `function ${functionName}(\${1:parameters}) {\n    // ${commentText}\n    \${0:// TODO: Implement}\n}`;
        default:
            return `${functionName}()`;
    }
}

// Generate loop from comment
function generateLoopFromComment(commentText, language) {
    switch (language) {
        case 'python':
            return `for \${1:item} in \${2:iterable}:\n    # ${commentText}\n    \${0:pass}`;
        case 'javascript':
            return `for (let \${1:i} = 0; \${1:i} < \${2:length}; \${1:i}++) {\n    // ${commentText}\n    \${0:// TODO: Implement}\n}`;
        default:
            return `// ${commentText}`;
    }
}

// Generate class from comment
function generateClassFromComment(commentText, language) {
    const words = commentText.split(' ');
    const className = words.find(word => !['class', 'object', 'create', 'make'].includes(word)) || 'NewClass';
    
    switch (language) {
        case 'python':
            return `class ${className}:\n    """${commentText}\n    """\n    \n    def __init__(self, \${1:parameters}):\n        """Initialize ${className}\n        \n        Args:\n            \${1:parameters}: Description\n        """\n        \${0:pass}`;
        case 'javascript':
            return `class ${className} {\n    // ${commentText}\n    constructor(\${1:parameters}) {\n        \${0:// TODO: Initialize}\n    }\n}`;
        default:
            return `class ${className} {}`;
    }
}

// Add Python-specific completions
function addPythonCompletions(completions, context) {
    if (context.includes('import ')) {
        completions.push({
            label: 'common_imports',
            insertText: 'import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt',
            detail: 'Common data science imports',
            kind: 'snippet'
        });
    }
    
    if (context.includes('if __name__')) {
        completions.push({
            label: 'main_block',
            insertText: 'if __name__ == "__main__":\n    ${0:main()}',
            detail: 'Main execution block',
            kind: 'snippet'
        });
    }
}

// Add JavaScript-specific completions
function addJavaScriptCompletions(completions, context) {
    if (context.includes('console.')) {
        completions.push({
            label: 'console_log',
            insertText: 'console.log(${1:value});',
            detail: 'Console log statement',
            kind: 'snippet'
        });
    }
    
    if (context.includes('async ')) {
        completions.push({
            label: 'async_function',
            insertText: 'async function ${1:functionName}(${2:parameters}) {\n    try {\n        ${0:// TODO: Implement}\n    } catch (error) {\n        console.error(error);\n    }\n}',
            detail: 'Async function with error handling',
            kind: 'function'
        });
    }
}

// Enhanced session downloads with better loading states
function downloadSession(sessionId, showLoading = true) {
    try {
        if (!sessionId || !codingSessions[sessionId]) {
            showErrorMessage('Session not found');
            return;
        }
        
        if (showLoading) {
            showProcessingIndicator();
        }
        
        // Create download URL for txt format
        const downloadUrl = `/api/download-session-summary/${sessionId}`;
        
        console.log('Downloading session as TXT:', sessionId);
        
        // Create a temporary link and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `session_summary_${sessionId}.txt`;
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Handle download completion
        link.addEventListener('click', function() {
            setTimeout(() => {
                document.body.removeChild(link);
                if (showLoading) {
                    hideProcessingIndicator();
                }
                showSuccessMessage('Session summary downloaded as TXT!');
            }, 1000);
        });
        
        link.click();
        
    } catch (error) {
        if (showLoading) {
            hideProcessingIndicator();
        }
        console.error('Download error:', error);
        showErrorMessage('Failed to download session');
    }
}

function downloadSessionMarkdown(sessionId, showLoading = true) {
    try {
        if (!sessionId || !codingSessions[sessionId]) {
            showErrorMessage('Session not found');
            return;
        }
        
        if (showLoading) {
            showProcessingIndicator();
        }
        
        // Create download URL for markdown format
        const downloadUrl = `/api/download-session-markdown/${sessionId}`;
        
        console.log('Downloading session as Markdown:', sessionId);
        
        // Create a temporary link and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `session_summary_${sessionId}.md`;
        link.style.display = 'none';
        document.body.appendChild(link);
        
        // Handle download completion
        link.addEventListener('click', function() {
            setTimeout(() => {
                document.body.removeChild(link);
                if (showLoading) {
                    hideProcessingIndicator();
                }
                showSuccessMessage('Session summary downloaded as Markdown!');
            }, 1000);
        });
        
        link.click();
        
    } catch (error) {
        if (showLoading) {
            hideProcessingIndicator();
        }
        console.error('Download error:', error);
        showErrorMessage('Failed to download session');
    }
}

// Enhanced current session download functions
function downloadCurrentSessionTXT() {
    if (!currentCode || !currentCode.session_id) {
        showErrorMessage('No active session to download. Please generate AI assistance first.');
        return;
    }
    
    downloadSession(currentCode.session_id, true);
}

function downloadCurrentSessionMarkdown() {
    if (!currentCode || !currentCode.session_id) {
        showErrorMessage('No active session to download. Please generate AI assistance first.');
        return;
    }
    
    downloadSessionMarkdown(currentCode.session_id, true);
}

// Enhanced session loading after AI assistance
function showCurrentSessionDownload() {
    const currentSessionDiv = document.getElementById('current-session-download');
    if (currentSessionDiv && currentCode && currentCode.session_id) {
        currentSessionDiv.style.display = 'block';
        
        // Update the display with current session info
        const sessionInfo = codingSessions[currentCode.session_id];
        if (sessionInfo) {
            const infoDiv = currentSessionDiv.querySelector('.download-info');
            if (infoDiv) {
                infoDiv.innerHTML = `
                    <p><strong>Current Session:</strong> ${currentCode.session_id}</p>
                    <p><strong>Language:</strong> ${sessionInfo.language?.toUpperCase() || 'Unknown'}</p>
                    <p><strong>Type:</strong> ${sessionInfo.type?.replace('_', ' ').toUpperCase() || 'Unknown'}</p>
                    <ul class="export-info">
                        <li><strong>Session Summary:</strong> Complete record including original code, AI response, and settings</li>
                        <li><strong>TXT Format:</strong> Plain text format for easy reading and sharing</li>
                        <li><strong>Markdown Format:</strong> Formatted document with syntax highlighting</li>
                    </ul>
                `;
            }
        }
    }
}

// Floating Header Functionality
function setupFloatingHeader() {
    const header = document.querySelector('header');
    const body = document.body;
    let lastScrollTop = 0;
    let isAtTop = true;
    let hoverTimeout;
    
    // Create hover zone at top of screen
    const hoverZone = document.createElement('div');
    hoverZone.className = 'header-hover-zone';
    body.appendChild(hoverZone);
    
    // Scroll event handler
    function handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Check if we're at the top of the page
        if (scrollTop <= 100) {
            isAtTop = true;
            header.classList.remove('header-hidden');
            header.classList.remove('header-hover');
        } else {
            if (isAtTop) {
                // Just left the top area
                isAtTop = false;
                header.classList.add('header-hidden');
                header.classList.remove('header-hover');
            }
        }
        
        lastScrollTop = scrollTop;
    }
    
    // Mouse enter hover zone
    function showHeaderOnHover() {
        if (!isAtTop) {
            clearTimeout(hoverTimeout);
            header.classList.remove('header-hidden');
            header.classList.add('header-hover');
        }
    }
    
    // Mouse leave hover zone or header
    function hideHeaderOnLeave() {
        if (!isAtTop) {
            hoverTimeout = setTimeout(() => {
                header.classList.add('header-hidden');
                header.classList.remove('header-hover');
            }, 500); // 500ms delay before hiding
        }
    }
    
    // Event listeners
    window.addEventListener('scroll', handleScroll);
    
    // Hover zone events
    hoverZone.addEventListener('mouseenter', showHeaderOnHover);
    hoverZone.addEventListener('mouseleave', hideHeaderOnLeave);
    
    // Header events
    header.addEventListener('mouseenter', () => {
        clearTimeout(hoverTimeout);
        showHeaderOnHover();
    });
    
    header.addEventListener('mouseleave', hideHeaderOnLeave);
    
    // Touch events for mobile
    hoverZone.addEventListener('touchstart', showHeaderOnHover);
    
    // Click outside to hide on mobile
    document.addEventListener('touchstart', (e) => {
        if (!header.contains(e.target) && !hoverZone.contains(e.target) && !isAtTop) {
            hideHeaderOnLeave();
        }
    });
    
    // Initial state
    if (window.pageYOffset > 100) {
        isAtTop = false;
        header.classList.add('header-hidden');
    }
}

// Enhanced smooth scrolling for navigation links
function setupSmoothScrolling() {
    const navLinks = document.querySelectorAll('header .nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Code editor functions
function clearCodeEditor() {
    const codeInput = document.getElementById('code_input');
    const errorInput = document.getElementById('error_message');
    const contextInput = document.getElementById('context');
    
    if (codeInput) codeInput.value = '';
    if (errorInput) errorInput.value = '';
    if (contextInput) contextInput.value = '';
    
    // Clear results
    const suggestionDisplay = document.querySelector('.summary-display');
    if (suggestionDisplay) {
        suggestionDisplay.innerHTML = 'No AI assistance generated yet. Enter your code above and select an assistance type to get AI-powered help.';
    }
    
    // Hide stats
    const statsPanel = document.getElementById('code-stats');
    if (statsPanel) {
        statsPanel.style.display = 'none';
    }
    
    console.log('Code editor cleared');
}

function copyCode() {
    const codeInput = document.getElementById('code_input');
    if (codeInput && codeInput.value) {
        navigator.clipboard.writeText(codeInput.value).then(() => {
            showSuccessMessage('Code copied to clipboard!');
        }).catch(err => {
            showErrorMessage('Failed to copy code to clipboard');
        });
    } else {
        showErrorMessage('No code to copy');
    }
}

function setupFormValidation() {
    const form = document.getElementById('code-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const codeInput = document.getElementById('code_input');
            if (!codeInput.value.trim()) {
                e.preventDefault();
                alert('Please enter some code to get AI assistance');
                return false;
            }
            
            // Show processing indicator
            showProcessingIndicator();
        });
    }
}

function setupCodeEditor() {
    const codeInput = document.getElementById('code_input');
    if (codeInput) {
        // Add syntax highlighting class based on language selection
        const languageSelect = document.getElementById('programming_language');
        if (languageSelect) {
            languageSelect.addEventListener('change', function() {
                updateCodeStats();
                // Future: Update syntax highlighting
            });
        }
        
        // Update stats on code change
        codeInput.addEventListener('input', function() {
            updateCodeStats();
        });
    }
}

function updateCodeStats() {
    const codeInput = document.getElementById('code_input');
    const statsPanel = document.getElementById('code-stats');
    const statsContent = document.getElementById('code-stats-content');
    
    if (codeInput && statsPanel && statsContent) {
        const code = codeInput.value;
        if (code.trim()) {
            const lines = code.split('\n').length;
            const characters = code.length;
            const words = code.trim().split(/\s+/).length;
            const language = document.getElementById('programming_language').value;
            
            statsContent.innerHTML = `
                <div class="two-column">
                    <div>
                        <p><strong>Language:</strong> ${language.toUpperCase()}</p>
                        <p><strong>Lines:</strong> ${lines}</p>
                    </div>
                    <div>
                        <p><strong>Characters:</strong> ${characters}</p>
                        <p><strong>Words:</strong> ${words}</p>
                    </div>
                </div>
            `;
            
            statsPanel.style.display = 'block';
        } else {
            statsPanel.style.display = 'none';
        }
    }
}

function handleFormSubmission() {
    const form = document.getElementById('code-form');
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

function analyzeQuality() {
    showSuccessMessage('Code quality analysis feature coming soon!');
}

function generateTests() {
    showSuccessMessage('Test case generation feature coming soon!');
}

// File upload functions
function uploadCodeFile() {
    const fileInput = document.getElementById('code_file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to upload');
        return;
    }
    
    // Validate file type
    const allowedExtensions = ['py', 'js', 'java', 'cpp', 'c', 'h', 'cs', 'php', 'rb', 'go', 'rs', 'ts', 'html', 'css', 'sql', 'sh', 'txt'];
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        alert('Invalid file type. Please upload a code file.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        const codeContent = e.target.result;
        
        // Set the code in the editor
        const codeInput = document.getElementById('code_input');
        if (codeInput) {
            codeInput.value = codeContent;
        }
        
        // Auto-detect language based on file extension
        const languageMap = {
            'py': 'python',
            'js': 'javascript',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'cpp',
            'h': 'cpp',
            'cs': 'csharp',
            'php': 'php',
            'rb': 'ruby',
            'go': 'go',
            'rs': 'rust',
            'ts': 'typescript',
            'html': 'html',
            'css': 'css',
            'sql': 'sql',
            'sh': 'bash'
        };
        
        const languageSelect = document.getElementById('programming_language');
        if (languageSelect && languageMap[fileExtension]) {
            languageSelect.value = languageMap[fileExtension];
        }
        
        updateCodeStats();
        showSuccessMessage(`File ${file.name} loaded successfully!`);
    };
    
    reader.readAsText(file);
}

// Session management functions
function loadSessions() {
    fetch('/api/get-sessions')
    .then(response => response.json())
    .then(data => {
        if (data.sessions && data.sessions.length > 0) {
            codingSessions = {};
            
            // Convert array to object and find most recent
            let mostRecentSession = null;
            let mostRecentTime = 0;
            
            data.sessions.forEach(session => {
                codingSessions[session.id] = session;
                
                const sessionTime = new Date(session.timestamp).getTime();
                if (sessionTime > mostRecentTime) {
                    mostRecentTime = sessionTime;
                    mostRecentSession = session;
                }
            });
            
            // Set the most recent session as current if none is set
            if (!currentCode && mostRecentSession) {
                currentCode = { session_id: mostRecentSession.id };
            }
            
            updateSessionsList();
            updateSessionStats();
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
            updateExportDropdowns();
        }
    })
    .catch(error => {
        console.error('Error loading file types:', error);
    });
}

function updateExportDropdowns() {
    // Update any export dropdowns in the UI
    const exportSelects = document.querySelectorAll('.export-format-select');
    exportSelects.forEach(select => {
        select.innerHTML = '<option value="">Select file type...</option>';
        supportedFileTypes.forEach(type => {
            const option = document.createElement('option');
            option.value = type.value;
            option.textContent = type.label;
            select.appendChild(option);
        });
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
    const assistanceTypes = {};
    let totalCodeLines = 0;
    
    for (const session of Object.values(codingSessions)) {
        const language = session.language || 'unknown';
        const type = session.type || 'unknown';
        
        languages[language] = (languages[language] || 0) + 1;
        assistanceTypes[type] = (assistanceTypes[type] || 0) + 1;
        totalCodeLines += session.code_length || 0;
    }
    
    let html = `
        <div class="two-column">
            <div>
                <h5>📊 Session Statistics</h5>
                <ul>
                    <li>Total Sessions: ${totalSessions}</li>
                    <li>Total Code Lines: ${totalCodeLines}</li>
                    <li>Most Used Language: ${getMostUsedItem(languages)}</li>
                </ul>
            </div>
            <div>
                <h5>📈 Languages Used</h5>
                <ul>
    `;
    
    for (const [language, count] of Object.entries(languages)) {
        html += `<li>${language.toUpperCase()}: ${count}</li>`;
    }
    
    html += `
                </ul>
            </div>
        </div>
    `;
    
    statsContent.innerHTML = html;
}

function getMostUsedItem(items) {
    let maxCount = 0;
    let mostUsed = 'None';
    
    for (const [item, count] of Object.entries(items)) {
        if (count > maxCount) {
            maxCount = count;
            mostUsed = item;
        }
    }
    
    return mostUsed.toUpperCase();
}

function exportCurrentCode() {
    const codeInput = document.getElementById('code_input');
    const languageSelect = document.getElementById('programming_language');
    
    if (!codeInput || !codeInput.value.trim()) {
        showErrorMessage('No code to export. Please enter some code first.');
        return;
    }
    
    const language = languageSelect ? languageSelect.value : 'python';
    const code = codeInput.value;
    const sessionId = currentCode?.session_id || `export_${new Date().getTime()}`;
    
    showProcessingIndicator();
    
    fetch('/api/export-code-only', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language,
            session_id: sessionId
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(data => {
                throw new Error(data.error || 'Export failed');
            });
        }
    })
    .then(blob => {
        hideProcessingIndicator();
        
        // Get file extension from language
        const fileType = supportedFileTypes.find(type => type.value === language);
        const extension = fileType ? fileType.extension : '.txt';
        const filename = `${sessionId}_code${extension}`;
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showSuccessMessage(`Code exported as ${filename}!`);
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Export error:', error);
        showErrorMessage('Failed to export code: ' + error.message);
    });
}

function exportCurrentCodeAsLanguage(targetLanguage) {
    const codeInput = document.getElementById('code_input');
    
    if (!codeInput || !codeInput.value.trim()) {
        showErrorMessage('No code to export. Please enter some code first.');
        return;
    }
    
    const code = codeInput.value;
    const sessionId = currentCode?.session_id || `export_${new Date().getTime()}`;
    
    showProcessingIndicator();
    
    fetch('/api/export-code-only', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: targetLanguage,
            session_id: sessionId
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            return response.json().then(data => {
                throw new Error(data.error || 'Export failed');
            });
        }
    })
    .then(blob => {
        hideProcessingIndicator();
        
        // Get file extension from target language
        const fileType = supportedFileTypes.find(type => type.value === targetLanguage);
        const extension = fileType ? fileType.extension : '.txt';
        const filename = `${sessionId}_code${extension}`;
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showSuccessMessage(`Code exported as ${targetLanguage.toUpperCase()} file: ${filename}!`);
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Export error:', error);
        showErrorMessage('Failed to export code: ' + error.message);
    });
}

// Update the sessions list to include download options
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
                    <button onclick="loadSession('${sessionId}')" class="btn btn-secondary" title="Load this session">Load</button>
                    <button onclick="downloadSession('${sessionId}')" class="btn btn-info" title="Download as TXT">TXT</button>
                    <button onclick="downloadSessionMarkdown('${sessionId}')" class="btn btn-success" title="Download as Markdown">MD</button>
                    <button onclick="deleteSession('${sessionId}')" class="btn btn-danger" title="Delete this session">Delete</button>
                </div>
            </div>
        `;
    });
    
    sessionsList.innerHTML = sessionsHTML;
}

function downloadSession(sessionId) {
    try {
        if (!sessionId || !codingSessions[sessionId]) {
            showErrorMessage('Session not found');
            return;
        }
        
        // Create download URL for txt format
        const downloadUrl = `/api/download-session/${sessionId}/txt`;
        
        console.log('Downloading session as TXT:', sessionId);
        console.log('Download URL:', downloadUrl);
        
        // Create a temporary link and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${sessionId}_session_summary.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showSuccessMessage('Session summary downloaded as TXT!');
    } catch (error) {
        console.error('Download error:', error);
        showErrorMessage('Failed to download session');
    }
}

function downloadSessionMarkdown(sessionId) {
    try {
        if (!sessionId || !codingSessions[sessionId]) {
            showErrorMessage('Session not found');
            return;
        }
        
        // Create download URL for markdown format
        const downloadUrl = `/api/download-session/${sessionId}/markdown`;
        
        console.log('Downloading session as Markdown:', sessionId);
        console.log('Download URL:', downloadUrl);
        
        // Create a temporary link and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `${sessionId}_session_summary.md`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        showSuccessMessage('Session summary downloaded as Markdown!');
    } catch (error) {
        console.error('Download error:', error);
        showErrorMessage('Failed to download session');
    }
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
            delete codingSessions[sessionId];
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

function loadSession(sessionId) {
    if (!codingSessions[sessionId]) {
        showErrorMessage('Session not found');
        return;
    }
    
    fetch(`/api/get-session/${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const session = data.session;
            currentCode = { session_id: sessionId };
            currentSuggestion = session.suggestion;
            
            // Load code into editor
            const codeInput = document.getElementById('code_input');
            if (codeInput && session.code_content) {
                codeInput.value = session.code_content;
            }
            
            // Set language
            const languageSelect = document.getElementById('programming_language');
            if (languageSelect && session.language) {
                languageSelect.value = session.language;
            }
            
            // Load assistance settings
            const settings = session.assistance_settings || {};
            if (settings.context) {
                const contextInput = document.getElementById('context');
                if (contextInput) contextInput.value = settings.context;
            }
            
            if (settings.error_message) {
                const errorInput = document.getElementById('error_message');
                if (errorInput) errorInput.value = settings.error_message;
            }
            
            if (settings.doc_type) {
                const docTypeSelect = document.getElementById('doc_type');
                if (docTypeSelect) docTypeSelect.value = settings.doc_type;
            }
            
            if (settings.type) {
                const assistanceTypeSelect = document.getElementById('assistance_type');
                if (assistanceTypeSelect) assistanceTypeSelect.value = settings.type;
            }
            
            // Update suggestion display
            updateSuggestionDisplay(session.suggestion || 'No suggestion available for this session');
            
            updateCodeStats();
            showSuccessMessage(`Session ${sessionId} loaded successfully!`);
        } else {
            showErrorMessage('Error loading session: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showErrorMessage('Network error occurred while loading session');
    });
}

// Functions for current session downloads
function downloadCurrentSessionTXT() {
    if (!currentCode || !currentCode.session_id) {
        showErrorMessage('No active session to download. Please generate AI assistance first.');
        return;
    }
    
    downloadSession(currentCode.session_id);
}

function downloadCurrentSessionMarkdown() {
    if (!currentCode || !currentCode.session_id) {
        showErrorMessage('No active session to download. Please generate AI assistance first.');
        return;
    }
    
    downloadSessionMarkdown(currentCode.session_id);
}

// Show current session download options when there's an active session
function showCurrentSessionDownload() {
    const currentSessionDiv = document.getElementById('current-session-download');
    if (currentSessionDiv && currentCode && currentCode.session_id) {
        currentSessionDiv.style.display = 'block';
    }
}

function hideCurrentSessionDownload() {
    const currentSessionDiv = document.getElementById('current-session-download');
    if (currentSessionDiv) {
        currentSessionDiv.style.display = 'none';
    }
}

// Update existing functions to show/hide current session download
function getCodeSuggestion() {
    const code = document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const context = document.getElementById('context').value;
    
    if (!code.trim()) {
        showErrorMessage('Please enter some code first');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/code-suggestion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            currentSuggestion = data.suggestion;
            
            // Process and display markdown content
            const processedContent = processMarkdownText(data.suggestion);
            updateSuggestionDisplay(processedContent);
            
            updateCodeStats();
            loadSessions();
            updateSessionStats();
            showCurrentSessionDownload(); // Show download options for current session
            showSuccessMessage('Code suggestion generated successfully!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

// Update other AI assistance functions to also show current session download
function explainError() {
    const code = document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const errorMessage = document.getElementById('error_message').value;
    
    if (!errorMessage.trim()) {
        showErrorMessage('Please enter an error message to explain');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/explain-error', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            error: errorMessage,
            language: language
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            currentSuggestion = data.explanation;
            
            const processedContent = processMarkdownText(data.explanation);
            updateSuggestionDisplay(processedContent);
            
            loadSessions();
            updateSessionStats();
            showCurrentSessionDownload(); // Show download options for current session
            showSuccessMessage('Error explanation generated successfully!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function generateDocs() {
    const code = document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const docType = document.getElementById('doc_type').value;
    
    if (!code.trim()) {
        showErrorMessage('Please enter some code first');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/generate-docs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language,
            doc_type: docType
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            currentSuggestion = data.documentation;
            
            const processedContent = processMarkdownText(data.documentation);
            updateSuggestionDisplay(processedContent);
            
            loadSessions();
            updateSessionStats();
            showCurrentSessionDownload(); // Show download options for current session
            showSuccessMessage('Documentation generated successfully!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function completeCode() {
    const code = document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const context = document.getElementById('context').value;
    
    if (!code.trim()) {
        showErrorMessage('Please enter some partial code first');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/complete-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            currentSuggestion = data.completion;
            
            const processedContent = processMarkdownText(data.completion);
            updateSuggestionDisplay(processedContent);
            
            loadSessions();
            updateSessionStats();
            showCurrentSessionDownload(); // Show download options for current session
            showSuccessMessage('Code completion generated successfully!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

function createExportDropdown() {
    const exportContainer = document.querySelector('.export-container');
    if (!exportContainer) return;
    
    const dropdownHTML = `
        <div class="export-dropdown">
            <label for="export-language-select">Export Code As:</label>
            <select id="export-language-select" class="export-format-select form-control">
                <option value="">Select file type...</option>
            </select>
            <button onclick="handleExportDropdownSelection()" class="btn btn-primary">Export Code</button>
        </div>
    `;
    
    exportContainer.innerHTML = dropdownHTML;
    updateExportDropdowns();
}

function handleExportDropdownSelection() {
    const select = document.getElementById('export-language-select');
    if (!select || !select.value) {
        showErrorMessage('Please select a file type first');
        return;
    }
    
    exportCurrentCodeAsLanguage(select.value);
}

// Utility functions for messages
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
    }
}

function showProcessingIndicator() {
    if (processingInProgress) return;
    
    processingInProgress = true;
    
    // Disable all buttons
    const buttons = document.querySelectorAll('button, input[type="submit"]');
    buttons.forEach(button => {
        button.disabled = true;
    });
    
    // Show loading message
    showMessage('Processing your request...', 'info');
}

function hideProcessingIndicator() {
    processingInProgress = false;
    
    // Re-enable all buttons
    const buttons = document.querySelectorAll('button, input[type="submit"]');
    buttons.forEach(button => {
        button.disabled = false;
    });
    
    // Remove info alerts
    const infoAlerts = document.querySelectorAll('.alert-info');
    infoAlerts.forEach(alert => alert.remove());
}

function updateSuggestionDisplay(content) {
    const suggestionDisplay = document.querySelector('.summary-display');
    if (suggestionDisplay) {
        // Add markdown-content class for styling
        suggestionDisplay.classList.add('markdown-content');
        
        // For AJAX responses, we need to handle markdown on the client side
        // or send already processed HTML from the server
        
        // Simple markdown-like formatting for dynamic content
        let formattedContent = content
            // Headers
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            // Code blocks
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        suggestionDisplay.innerHTML = formattedContent;
    }
}

// Function to process markdown in AJAX responses
function processMarkdownResponse(response) {
    // If the server sends already processed HTML, use it directly
    if (response.html) {
        return response.html;
    }
    
    // Otherwise, process the markdown text
    if (response.suggestion || response.explanation || response.documentation || response.completion) {
        const content = response.suggestion || response.explanation || response.documentation || response.completion;
        return processMarkdownText(content);
    }
    
    return response;
}

function processMarkdownText(text) {
    // Basic markdown processing for client-side rendering
    return text
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/^(.*)/, '<p>$1')
        .replace(/(.*$)/, '$1</p>');
}

// Update existing AJAX functions to handle markdown
function getCodeSuggestion() {
    const code = document.getElementById('code_input').value;
    const language = document.getElementById('programming_language').value;
    const context = document.getElementById('context').value;
    
    if (!code.trim()) {
        showErrorMessage('Please enter some code first');
        return;
    }
    
    showProcessingIndicator();
    
    fetch('/api/code-suggestion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            code: code,
            language: language,
            context: context
        })
    })
    .then(response => response.json())
    .then(data => {
        hideProcessingIndicator();
        if (data.success) {
            currentCode = { session_id: data.session_id };
            currentSuggestion = data.suggestion;
            
            // Process and display markdown content
            const processedContent = processMarkdownText(data.suggestion);
            updateSuggestionDisplay(processedContent);
            
            updateCodeStats();
            loadSessions();
            updateSessionStats();
            showSuccessMessage('Code suggestion generated successfully!');
        } else {
            showErrorMessage('Error: ' + data.error);
        }
    })
    .catch(error => {
        hideProcessingIndicator();
        console.error('Error:', error);
        showErrorMessage('Network error occurred');
    });
}

// Back to top functionality
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Show/hide back to top button
function setupBackToTop() {
    const backToTopBtn = document.getElementById('back-to-top');
    
    if (backToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 500) {
                backToTopBtn.classList.add('visible');
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.classList.remove('visible');
                setTimeout(() => {
                    if (!backToTopBtn.classList.contains('visible')) {
                        backToTopBtn.style.display = 'none';
                    }
                }, 300);
            }
        });
    }
}