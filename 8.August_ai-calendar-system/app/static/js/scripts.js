// AI Calendar System JavaScript Functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize clock if on dashboard
    if (document.getElementById('clock')) {
        updateClock();
        setInterval(updateClock, 1000);
    }
    
    // Auto-refresh dashboard every 5 minutes
    if (window.location.pathname === '/') {
        setInterval(function() {
            location.reload();
        }, 300000);
    }
    
    // Initialize calendar drag and drop if on calendar view
    if (document.querySelector('.calendar-grid')) {
        enableEventDragDrop();
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
});

// Clock Functions
function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();
    
    const clockElement = document.getElementById('clock');
    if (clockElement) {
        clockElement.innerHTML = `<div class="time">${timeString}</div><div class="date">${dateString}</div>`;
    }
}

// Voice Recording Functions
function startVoiceRecording() {
    const button = document.getElementById('recordButton');
    const status = document.getElementById('recordingStatus');
    
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Speech recognition not supported in this browser. Please use Chrome or Edge.');
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    button.innerHTML = '🔴 Recording...';
    button.disabled = true;
    status.innerHTML = '<div class="recording-indicator">Listening...</div>';
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        status.innerHTML = `<div class="recognized-text">Recognized: "${transcript}"</div>`;
        
        // Send transcript to server for processing
        const formData = new FormData();
        formData.append('voice_text', transcript);
        
        fetch('/voice_command', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                status.innerHTML += '<div class="success-message">Command processed successfully!</div>';
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                status.innerHTML += '<div class="error-message">Failed to process command.</div>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            status.innerHTML += '<div class="error-message">Network error occurred.</div>';
        });
    };
    
    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
        button.innerHTML = '🎤 Start Recording';
        button.disabled = false;
        status.innerHTML = `<div class="error-message">Voice recognition failed: ${event.error}</div>`;
    };
    
    recognition.onend = function() {
        button.innerHTML = '🎤 Start Recording';
        button.disabled = false;
    };
    
    recognition.start();
}

function startVoiceCommand() {
    window.location.href = '/voice_command';
}

// Meeting Time Suggestions
function suggestMeetingTimes(duration = 60) {
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Analyzing...';
    button.disabled = true;
    
    fetch('/api/suggest_times', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({duration: duration})
    })
    .then(response => response.json())
    .then(data => {
        button.textContent = originalText;
        button.disabled = false;
        
        if (data.suggestions && data.suggestions.length > 0) {
            let suggestions = data.suggestions.map(s => 
                `📅 ${s.date} ${s.start_time}-${s.end_time}\n💡 ${s.reasoning}`
            ).join('\n\n');
            alert('🤖 AI Suggested Meeting Times:\n\n' + suggestions);
        } else {
            alert('No available meeting times found for the requested duration.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.textContent = originalText;
        button.disabled = false;
        alert('Error getting meeting suggestions. Please try again.');
    });
}

// Quick Event Creation
function createQuickEvent() {
    const title = prompt('Enter event title:');
    if (!title) return;
    
    const date = prompt('Enter date (YYYY-MM-DD) or leave blank for today:');
    const time = prompt('Enter time (HH:MM) or leave blank for now:');
    
    const today = new Date();
    const eventDate = date || today.toISOString().split('T')[0];
    const eventTime = time || today.toTimeString().split(' ')[0].substring(0, 5);
    
    // Create form data
    const formData = new FormData();
    formData.append('title', title);
    formData.append('start_time', `${eventDate} ${eventTime}`);
    formData.append('end_time', `${eventDate} ${addHour(eventTime)}`);
    formData.append('description', 'Created via quick action');
    
    fetch('/create_event', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            alert('Event created successfully!');
            location.reload();
        } else {
            alert('Failed to create event.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error creating event.');
    });
}

// Calendar Navigation
function changeMonth(direction) {
    const currentUrl = new URL(window.location);
    const urlParams = new URLSearchParams(currentUrl.search);
    
    const currentMonth = parseInt(urlParams.get('month')) || new Date().getMonth() + 1;
    const currentYear = parseInt(urlParams.get('year')) || new Date().getFullYear();
    
    let newMonth = currentMonth + direction;
    let newYear = currentYear;
    
    if (newMonth > 12) {
        newMonth = 1;
        newYear++;
    } else if (newMonth < 1) {
        newMonth = 12;
        newYear--;
    }
    
    urlParams.set('month', newMonth);
    urlParams.set('year', newYear);
    currentUrl.search = urlParams.toString();
    window.location.href = currentUrl.toString();
}

// Event Modal Functions
function showCreateEventModal(date) {
    const startTimeInput = document.querySelector('input[name="start_time"]');
    const endTimeInput = document.querySelector('input[name="end_time"]');
    
    if (startTimeInput && endTimeInput) {
        const selectedDate = new Date(date);
        const defaultTime = '09:00';
        const defaultEndTime = '10:00';
        
        startTimeInput.value = `${date}T${defaultTime}`;
        endTimeInput.value = `${date}T${defaultEndTime}`;
        
        // Scroll to form
        document.querySelector('.create-event-section').scrollIntoView({ 
            behavior: 'smooth' 
        });
    }
}

// Drag and Drop Functionality
function enableEventDragDrop() {
    const events = document.querySelectorAll('.day-event');
    const days = document.querySelectorAll('.calendar-day');
    
    events.forEach(event => {
        event.draggable = true;
        event.addEventListener('dragstart', function(e) {
            e.dataTransfer.setData('text/plain', this.dataset.eventId);
            this.style.opacity = '0.5';
        });
        
        event.addEventListener('dragend', function(e) {
            this.style.opacity = '1';
        });
    });
    
    days.forEach(day => {
        day.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '#e3f2fd';
        });
        
        day.addEventListener('dragleave', function(e) {
            this.style.backgroundColor = '';
        });
        
        day.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.backgroundColor = '';
            
            const eventId = e.dataTransfer.getData('text/plain');
            const newDate = this.dataset.date;
            
            if (eventId && newDate) {
                moveEvent(eventId, newDate);
            }
        });
    });
}

function moveEvent(eventId, newDate) {
    fetch('/api/move_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            eventId: eventId,
            newDate: newDate
        })
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Failed to move event.');
        }
    })
    .catch(error => {
        console.error('Error moving event:', error);
        alert('Error moving event.');
    });
}

// Form Validation
function validateForm(event) {
    const form = event.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#e74c3c';
            isValid = false;
        } else {
            field.style.borderColor = '';
        }
    });
    
    // Validate datetime fields
    const startTime = form.querySelector('input[name="start_time"]');
    const endTime = form.querySelector('input[name="end_time"]');
    
    if (startTime && endTime && startTime.value && endTime.value) {
        if (new Date(startTime.value) >= new Date(endTime.value)) {
            alert('End time must be after start time.');
            isValid = false;
        }
    }
    
    if (!isValid) {
        event.preventDefault();
        alert('Please fill in all required fields correctly.');
    }
}

// Utility Functions
function addHour(timeString) {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours) + 1, parseInt(minutes));
    return date.toTimeString().split(' ')[0].substring(0, 5);
}

function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Copy to clipboard functions
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Auto-save draft functionality for forms
function enableAutoSave() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                const key = `autosave_${form.className}_${input.name}`;
                localStorage.setItem(key, input.value);
            });
            
            // Restore saved values
            const key = `autosave_${form.className}_${input.name}`;
            const savedValue = localStorage.getItem(key);
            if (savedValue && !input.value) {
                input.value = savedValue;
            }
        });
        
        // Clear autosave on successful submit
        form.addEventListener('submit', function() {
            const inputs = this.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                const key = `autosave_${this.className}_${input.name}`;
                localStorage.removeItem(key);
            });
        });
    });
}

// Initialize autosave
enableAutoSave();