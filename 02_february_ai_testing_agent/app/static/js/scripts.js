document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const projectNameInput = document.getElementById('projectName');
    const contextInput = document.getElementById('context');

    uploadForm.addEventListener('submit', function(event) {
        if (!fileInput.value) {
            alert('Please upload a PDF file.');
            event.preventDefault();
        }
        if (!projectNameInput.value) {
            alert('Please enter a project name.');
            event.preventDefault();
        }
    });

    // Function to copy evaluation results
    document.getElementById('copyEvaluation').addEventListener('click', function() {
        const evaluationText = document.getElementById('evaluationResults').innerText;
        navigator.clipboard.writeText(evaluationText).then(() => {
            alert('Evaluation results copied to clipboard!');
        });
    });

    // Function to copy summary
    document.getElementById('copySummary').addEventListener('click', function() {
        const summaryText = document.getElementById('summaryResults').innerText;
        navigator.clipboard.writeText(summaryText).then(() => {
            alert('Summary copied to clipboard!');
        });
    });
});