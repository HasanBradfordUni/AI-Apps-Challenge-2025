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
    
    // Show loading state
    const submitBtn = form.querySelector('.submit-btn');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Creating...';
    submitBtn.disabled = true;
    
    // Prepare final form data as JSON
    const eventData = {
        'title': formData.get('title'),
        'description': formData.get('description'),
        'start_time': startDateTime,
        'end_time': endDateTime,
        'location': combineLocationAndPlatform(formData.get('location'), formData.get('platform')),
        'attendees': formData.get('attendees'),
        'is_all_day': duration.isAllDay ? 'true' : 'false'
    };
    
    fetch('/create_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify(eventData)
    })
    .then(response => response.json())
    .then(data => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
        
        if (data.success) {
            showNotification(data.message, 'success');
            closeQuickEventModal();
            
            // Update today's schedule in real-time
            updateTodaysSchedule();
            
            // If on calendar page, refresh the view
            if (window.location.pathname.includes('calendar_view')) {
                setTimeout(() => location.reload(), 1000);
            }
        } else {
            showNotification(data.error || 'Failed to create event.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
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

// Edit event modal functions
function editEvent(eventId) {
    console.log('Opening edit modal for event:', eventId);
    
    fetch(`/api/get_event/${eventId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch event');
            }
            return response.json();
        })
        .then(data => {
            console.log('Event data received:', data);
            
            // Populate the edit form
            document.getElementById('edit_event_id').value = data.id;
            document.getElementById('edit_title').value = data.title || '';
            document.getElementById('edit_description').value = data.description || '';
            document.getElementById('edit_date').value = data.date || '';
            document.getElementById('edit_start_time').value = data.start_time || '';
            document.getElementById('edit_duration').value = data.duration || '1h';
            document.getElementById('edit_platform').value = data.platform || 'In Person';
            document.getElementById('edit_location').value = data.location || '';
            document.getElementById('edit_attendees').value = data.attendees || '';
            
            // Show the modal
            document.getElementById('editEventModal').style.display = 'block';
        })
        .catch(error => {
            console.error('Error loading event:', error);
            alert('Error loading event details: ' + error.message);
        });
}

function closeEditModal() {
    document.getElementById('editEventModal').style.display = 'none';
}

// Handle edit form submission
document.addEventListener('DOMContentLoaded', function() {
    const editForm = document.getElementById('editEventForm');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const eventId = document.getElementById('edit_event_id').value;
            const formData = new FormData(editForm);
            
            // Convert FormData to JSON
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            
            console.log('Updating event:', eventId, data);
            
            fetch(`/edit_event/${eventId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert(result.message || 'Event updated successfully!');
                    closeEditModal();
                    // Reload the page to show updated event
                    window.location.reload();
                } else {
                    alert('Error: ' + (result.error || 'Failed to update event'));
                }
            })
            .catch(error => {
                console.error('Error updating event:', error);
                alert('Error updating event: ' + error.message);
            });
        });
    }
});

function deleteEventFromModal() {
    const eventId = document.getElementById('edit_event_id').value;
    
    if (!confirm('Are you sure you want to delete this event?')) {
        return;
    }
    
    fetch(`/delete_event/${eventId}`, {
        method: 'DELETE',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            alert(result.message || 'Event deleted successfully!');
            closeEditModal();
            window.location.reload();
        } else {
            alert('Error: ' + (result.error || 'Failed to delete event'));
        }
    })
    .catch(error => {
        console.error('Error deleting event:', error);
        alert('Error deleting event: ' + error.message);
    });
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('editEventModal');
    if (event.target === modal) {
        closeEditModal();
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

// Calendar navigation
function changeMonth(year, month) {
    window.location.href = `/calendar_view/${year}/${month}`;
}

// Enhanced email parser with AJAX
document.addEventListener('DOMContentLoaded', function() {
    const emailForm = document.getElementById('emailParserForm');
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('.submit-btn');
            const originalText = submitBtn.textContent;
            
            submitBtn.textContent = 'Parsing...';
            submitBtn.disabled = true;
            
            fetch('/email_sync', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                
                if (data.success) {
                    showNotification(data.message, 'success');
                    emailForm.reset();
                    // Update today's schedule if event was created
                    updateTodaysSchedule();
                } else {
                    showNotification(data.error || data.message, data.success ? 'success' : 'warning');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
                showNotification('Error processing email.', 'error');
            });
        });
    }
});

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

// New function to update today's schedule in real-time
function updateTodaysSchedule() {
    fetch('/api/today_events', {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.events) {
            const eventsContainer = document.querySelector('.events-list');
            if (eventsContainer) {
                if (data.events.length > 0) {
                    eventsContainer.innerHTML = data.events.map(event => `
                        <div class="event-item">
                            <div class="event-time-display">${event.time_display}</div>
                            <div class="event-details">
                                <h4>${event.title}</h4>
                                ${event.description ? `<p>${event.description}</p>` : ''}
                                ${event.location ? `<p class="event-location">📍 ${event.location}</p>` : ''}
                            </div>
                        </div>
                    `).join('');
                } else {
                    eventsContainer.innerHTML = '<p class="largeText">No events scheduled for today.</p>';
                }
            }
        }
    })
    .catch(error => {
        console.error('Error updating today\'s schedule:', error);
    });
}

// Function to remove event from calendar UI immediately
function removeEventFromUI(eventId) {
    const eventElements = document.querySelectorAll(`[data-event-id="${eventId}"]`);
    eventElements.forEach(element => {
        element.style.transition = 'all 0.3s ease';
        element.style.opacity = '0';
        element.style.transform = 'scale(0.8)';
        
        setTimeout(() => {
            element.remove();
        }, 300);
    });
}

// Function to update calendar display after changes
function updateCalendarDisplay() {
    // If we're on the calendar page, we can reload specific parts
    if (window.location.pathname.includes('calendar_view')) {
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
}

// Enhanced notification system with auto-dismiss
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()" style="background: none; border: none; color: white; margin-left: 10px; cursor: pointer;">&times;</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 5 seconds for success messages, 8 seconds for errors
    const dismissTime = type === 'error' ? 8000 : 5000;
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.transition = 'all 0.3s ease';
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }
    }, dismissTime);
}

// Add event listener for real-time event clicking
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('day-event')) {
        e.stopPropagation(); // Prevent day selection
        const eventId = e.target.dataset.eventId;
        if (eventId) {
            editEvent(eventId);
        }
    }
});

// Auto-refresh dashboard events every 30 seconds (optional)
if (window.location.pathname === '/') {
    setInterval(updateTodaysSchedule, 30000);
}

// Fix calendar day click to not interfere with event clicks
function selectDate(date) {
    // Only show create modal if we didn't click on an event
    showCreateEventModal(date);
}

// Update calendar day click handling to prevent event bubble
document.addEventListener('DOMContentLoaded', function() {
    // Update calendar day clicks to handle event vs day clicks
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('calendar-day')) {
            const date = e.target.dataset.date;
            if (date && !e.target.querySelector('.day-event:hover')) {
                selectDate(date);
            }
        }
    });
});