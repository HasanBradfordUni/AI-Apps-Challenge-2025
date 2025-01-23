// This file contains JavaScript code for client-side functionality, such as handling form submissions and updating the UI dynamically.

document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const uploadForm = document.getElementById('upload-form');
    const resultsContainer = document.getElementById('results-container');

    // Handle search form submission
    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const query = document.getElementById('search-query').value;

        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
        })
        .then(response => response.json())
        .then(data => {
            displayResults(data.results);
        })
        .catch(error => console.error('Error:', error));
    });

    // Handle document upload form submission
    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const formData = new FormData(uploadForm);

        fetch('/upload', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            uploadForm.reset();
        })
        .catch(error => console.error('Error:', error));
    });

    // Function to display search results
    function displayResults(results) {
        resultsContainer.innerHTML = '';
        if (results.length === 0) {
            resultsContainer.innerHTML = '<p>No results found.</p>';
            return;
        }

        results.forEach(result => {
            const resultItem = document.createElement('div');
            resultItem.className = 'result-item';
            resultItem.innerHTML = `<h3>${result.title}</h3><p>${result.summary}</p>`;
            resultsContainer.appendChild(resultItem);
        });
    }
});