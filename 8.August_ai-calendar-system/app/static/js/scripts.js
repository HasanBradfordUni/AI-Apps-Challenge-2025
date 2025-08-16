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
    // Create modal HTML
    const modalHTML = `
        <div id="quickEventModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="subHeading">🚀 Quick Create Event</h3>
                    <button onclick="closeQuickEventModal()" class="close-btn">&times;</button>
                </div>
                <form id="quickEventForm" class="quick-event-form">
                    <input type="text" name="title" placeholder="Event Title" class="form-input" required>
                    <textarea name="description" placeholder="Description (optional)" class="form-textarea" rows="2"></textarea>
                    
                    <div class="form-row">
                        <input type="date" name="date" class="form-input" value="${new Date().toISOString().split('T')[0]}">
                        <input type="time" name="start_time" class="form-input" value="09:00">
                    </div>
                    
                    <div class="form-row">
                        <input type="text" name="duration" placeholder="Duration (e.g., 1h 30m, 45, All Day)" class="form-input" value="1h">
                        <select name="platform" class="form-input">
                            <option value="">Select Platform</option>
                            <option value="In Person">In Person</option>
                            <option value="Microsoft Teams">Microsoft Teams</option>
                            <option value="Zoom">Zoom</option>
                            <option value="Google Meet">Google Meet</option>
                            <option value="Phone Call">Phone Call</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    
                    <input type="text" name="location" placeholder="Location/Meeting Link" class="form-input">
                    <input type="text" name="attendees" placeholder="Attendees (comma-separated emails)" class="form-input">
                    
                    <div class="form-actions">
                        <button type="button" onclick="closeQuickEventModal()" class="cancel-btn">Cancel</button>
                        <button type="submit" class="submit-btn">Create Event</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    // Add modal to page
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Handle form submission
    document.getElementById('quickEventForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitQuickEvent(this);
    });
}

function submitQuickEvent(form) {
    const formData = new FormData(form);
    const duration = parseDuration(formData.get('duration'));
    const startDateTime = `${formData.get('date')} ${formData.get('start_time')}`;
    
    // Calculate end time based on duration
    const endDateTime = calculateEndTime(startDateTime, duration);
    
    // Prepare final form data
    const finalFormData = new FormData();
    finalFormData.append('title', formData.get('title'));
    finalFormData.append('description', formData.get('description'));
    finalFormData.append('start_time', startDateTime);
    finalFormData.append('end_time', endDateTime);
    finalFormData.append('location', combineLocationAndPlatform(formData.get('location'), formData.get('platform')));
    finalFormData.append('attendees', formData.get('attendees'));
    finalFormData.append('is_all_day', duration.isAllDay ? 'true' : 'false');
    
    fetch('/create_event', {
        method: 'POST',
        body: finalFormData
    })
    .then(response => {
        if (response.ok) {
            showNotification('Event created successfully!', 'success');
            closeQuickEventModal();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Failed to create event.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error creating event.', 'error');
    });
}

function parseDuration(durationStr) {
    if (!durationStr || durationStr.toLowerCase() === 'all day') {
        return { minutes: 0, isAllDay: true };
    }
    
    durationStr = durationStr.toLowerCase().trim();
    let totalMinutes = 0;
    
    // Parse "1h 30m" format
    const hourMatch = durationStr.match(/(\d+)h/);
    const minuteMatch = durationStr.match(/(\d+)m/);
    
    if (hourMatch || minuteMatch) {
        if (hourMatch) totalMinutes += parseInt(hourMatch[1]) * 60;
        if (minuteMatch) totalMinutes += parseInt(minuteMatch[1]);
    } else {
        // Parse plain numbers
        const number = parseInt(durationStr);
        if (!isNaN(number)) {
            if (number < 10) {
                totalMinutes = number * 60; // Hours
            } else {
                totalMinutes = number; // Minutes
            }
        } else {
            totalMinutes = 60; // Default 1 hour
        }
    }
    
    return { minutes: totalMinutes, isAllDay: false };
}

function calculateEndTime(startDateTime, duration) {
    if (duration.isAllDay) {
        const date = startDateTime.split(' ')[0];
        return `${date} 23:59`;
    }
    
    const start = new Date(startDateTime);
    const end = new Date(start.getTime() + duration.minutes * 60000);
    
    return `${end.getFullYear()}-${String(end.getMonth() + 1).padStart(2, '0')}-${String(end.getDate()).padStart(2, '0')} ${String(end.getHours()).padStart(2, '0')}:${String(end.getMinutes()).padStart(2, '0')}`;
}

function combineLocationAndPlatform(location, platform) {
    if (platform && platform !== 'In Person' && platform !== '') {
        return platform + (location ? ` - ${location}` : '');
    }
    return location || '';
}

function closeQuickEventModal() {
    const modal = document.getElementById('quickEventModal');
    if (modal) {
        modal.remove();
    }
}

// Edit Event Functionality
function editEvent(eventId) {
    fetch(`/api/get_event/${eventId}`)
        .then(response => response.json())
        .then(event => {
            showEditEventModal(event);
        })
        .catch(error => {
            console.error('Error fetching event:', error);
            showNotification('Error loading event details.', 'error');
        });
}

function showEditEventModal(event) {
    const startDate = event.start_time ? event.start_time.split(' ')[0] : '';
    const startTime = event.start_time ? event.start_time.split(' ')[1] : '';
    
    const modalHTML = `
        <div id="editEventModal" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 class="subHeading">✏️ Edit Event</h3>
                    <button onclick="closeEditEventModal()" class="close-btn">&times;</button>
                </div>
                <form id="editEventForm" class="edit-event-form">
                    <input type="hidden" name="event_id" value="${event.id}">
                    <input type="text" name="title" placeholder="Event Title" class="form-input" value="${event.title || ''}" required>
                    <textarea name="description" placeholder="Description" class="form-textarea" rows="3">${event.description || ''}</textarea>
                    
                    <div class="form-row">
                        <input type="date" name="date" class="form-input" value="${startDate}">
                        <input type="time" name="start_time" class="form-input" value="${startTime}">
                    </div>
                    
                    <div class="form-row">
                        <input type="text" name="duration" placeholder="Duration" class="form-input" value="1h">
                        <select name="platform" class="form-input">
                            <option value="">Select Platform</option>
                            <option value="In Person">In Person</option>
                            <option value="Microsoft Teams">Microsoft Teams</option>
                            <option value="Zoom">Zoom</option>
                            <option value="Google Meet">Google Meet</option>
                            <option value="Phone Call">Phone Call</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    
                    <input type="text" name="location" placeholder="Location/Meeting Link" class="form-input" value="${event.location || ''}">
                    <input type="text" name="attendees" placeholder="Attendees" class="form-input" value="${event.attendees || ''}">
                    
                    <div class="form-actions">
                        <button type="button" onclick="deleteEvent(${event.id})" class="delete-btn">Delete</button>
                        <button type="button" onclick="closeEditEventModal()" class="cancel-btn">Cancel</button>
                        <button type="submit" class="submit-btn">Update Event</button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    document.getElementById('editEventForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitEditEvent(this);
    });
}

function submitEditEvent(form) {
    const formData = new FormData(form);
    const eventId = formData.get('event_id');
    
    fetch(`/edit_event/${eventId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (response.ok) {
            showNotification('Event updated successfully!', 'success');
            closeEditEventModal();
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification('Failed to update event.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating event.', 'error');
    });
}

function deleteEvent(eventId) {
    if (confirm('Are you sure you want to delete this event?')) {
        fetch(`/delete_event/${eventId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                showNotification('Event deleted successfully!', 'success');
                closeEditEventModal();
                setTimeout(() => location.reload(), 1000);
            } else {
                showNotification('Failed to delete event.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error deleting event.', 'error');
        });
    }
}

function closeEditEventModal() {
    const modal = document.getElementById('editEventModal');
    if (modal) {
        modal.remove();
    }
}

// Calendar Import Functions
function importGoogleCalendar() {
    showNotification('Connecting to Google Calendar...', 'info');
    window.location.href = '/auth/google';
}

function importOutlookCalendar() {
    showNotification('Connecting to Outlook Calendar...', 'info');
    window.location.href = '/auth/outlook';
}

// Enhanced event click handling for calendar
document.addEventListener('DOMContentLoaded', function() {
    // ... existing code ...
    
    // Add event click handling for edit functionality
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('day-event')) {
            const eventId = e.target.dataset.eventId;
            if (eventId) {
                editEvent(eventId);
            }
        }
    });
});

// Format time for display (remove year, just show time)
function formatEventTime(dateTimeString) {
    if (!dateTimeString) return 'TBD';
    
    const date = new Date(dateTimeString);
    return date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
}

// ... rest of existing scripts.js code ...