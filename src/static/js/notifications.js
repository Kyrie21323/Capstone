/**
 * Web Notifications Manager
 * Handles browser notification permissions and displays
 */

class NotificationManager {
    constructor() {
        this.permissionGranted = false;
        this.checkPermission();
    }

    /**
     * Check current notification permission status
     */
    checkPermission() {
        if (!('Notification' in window)) {
            console.log('This browser does not support notifications');
            return false;
        }

        this.permissionGranted = Notification.permission === 'granted';
        return this.permissionGranted;
    }

    /**
     * Request notification permission from user
     */
    async requestPermission() {
        if (!('Notification' in window)) {
            return { success: false, message: 'Notifications not supported' };
        }

        if (Notification.permission === 'granted') {
            this.permissionGranted = true;
            return { success: true, message: 'Already granted' };
        }

        if (Notification.permission === 'denied') {
            return { success: false, message: 'Permission denied. Please enable in browser settings.' };
        }

        try {
            const permission = await Notification.requestPermission();
            this.permissionGranted = permission === 'granted';

            if (this.permissionGranted) {
                return { success: true, message: 'Permission granted!' };
            } else {
                return { success: false, message: 'Permission denied' };
            }
        } catch (error) {
            console.error('Error requesting notification permission:', error);
            return { success: false, message: 'Error requesting permission' };
        }
    }

    /**
     * Show a notification
     */
    showNotification(title, options = {}) {
        if (!this.permissionGranted) {
            console.log('Notification permission not granted');
            return false;
        }

        const defaultOptions = {
            icon: '/static/images/logo.png',
            badge: '/static/images/badge.png',
            vibrate: [200, 100, 200],
            requireInteraction: true,
            ...options
        };

        try {
            const notification = new Notification(title, defaultOptions);

            // Handle notification click
            notification.onclick = function (event) {
                event.preventDefault();
                window.focus();

                if (options.url) {
                    window.location.href = options.url;
                }

                notification.close();
            };

            return true;
        } catch (error) {
            console.error('Error showing notification:', error);
            return false;
        }
    }

    /**
     * Show match notification
     */
    showMatchNotification(matchData) {
        const { matchName, eventName, meetingTime, meetingLocation, eventId } = matchData;

        let body = `You matched with ${matchName} at ${eventName}!`;

        if (meetingTime && meetingLocation) {
            body += `\n\n📅 Meeting: ${meetingTime}\n📍 Location: ${meetingLocation}`;
        } else {
            body += '\n\nCoordinate your meeting time directly.';
        }

        this.showNotification('🎉 It\'s a Match!', {
            body: body,
            tag: `match-${Date.now()}`,
            url: `/user/dashboard`,
            data: { eventId, type: 'match' }
        });
    }

    /**
     * Show admin notification (meeting point unavailable)
     */
    showAdminNotification(message) {
        this.showNotification('⚠️ Admin Alert', {
            body: message,
            tag: `admin-${Date.now()}`,
            url: '/admin/dashboard'
        });
    }
}

// Create global instance
const notificationManager = new NotificationManager();

/**
 * Show permission request modal for attendees
 */
function showNotificationPermissionModal() {
    // Check if already granted
    if (notificationManager.checkPermission()) {
        return;
    }

    // Check if dismissed this session
    if (sessionStorage.getItem('notification-modal-dismissed') === 'true') {
        return;
    }

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'notification-permission-modal';
    modal.innerHTML = `
        <div class="notification-modal-overlay"></div>
        <div class="notification-modal-content">
            <h2>🔔 Enable Notifications</h2>
            <p>Get notified instantly when you match with someone!</p>
            <ul style="text-align: left; margin: 20px 0;">
                <li>✓ Real-time match alerts</li>
                <li>✓ Meeting details and reminders</li>
                <li>✓ Never miss a connection</li>
            </ul>
            <div class="modal-buttons">
                <button class="btn-primary" onclick="handleNotificationAllow()">Allow Notifications</button>
                <button class="btn-secondary" onclick="handleNotificationSkip()">Maybe Later</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

/**
 * Handle notification permission allow
 */
async function handleNotificationAllow() {
    const result = await notificationManager.requestPermission();

    if (result.success) {
        showToast('✓ Notifications enabled!', 'success');
        closeNotificationModal();
    } else {
        showToast(result.message, 'error');
    }
}

/**
 * Handle notification permission skip
 */
function handleNotificationSkip() {
    closeNotificationModal();
    // Store preference to not ask again this session
    sessionStorage.setItem('notification-modal-dismissed', 'true');
}

/**
 * Close notification modal
 */
function closeNotificationModal() {
    const modal = document.querySelector('.notification-permission-modal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#17a2b8'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    .notification-permission-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .notification-modal-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
    }
    
    .notification-modal-content {
        position: relative;
        background: white;
        padding: 40px;
        border-radius: 20px;
        max-width: 500px;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        animation: modalSlideIn 0.3s ease-out;
    }
    
    @keyframes modalSlideIn {
        from {
            transform: scale(0.8);
            opacity: 0;
        }
        to {
            transform: scale(1);
            opacity: 1;
        }
    }
    
    .notification-modal-content h2 {
        color: #2c3e50;
        margin-bottom: 15px;
    }
    
    .notification-modal-content ul {
        list-style: none;
        padding: 0;
    }
    
    .notification-modal-content li {
        padding: 8px 0;
        color: #555;
    }
    
    .modal-buttons {
        display: flex;
        gap: 15px;
        margin-top: 30px;
    }
    
    .modal-buttons button {
        flex: 1;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #57068c 0%, #ab82c5 100%);
        color: white;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(87, 6, 140, 0.3);
    }
    
    .btn-secondary {
        background: #e9ecef;
        color: #6c757d;
    }
    
    .btn-secondary:hover {
        background: #dee2e6;
    }
`;
document.head.appendChild(style);

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { notificationManager, showNotificationPermissionModal };
}
