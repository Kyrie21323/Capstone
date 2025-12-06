/**
 * Prophere Modal System
 * Handles confirmation modals and dynamic modal creation
 */

class ModalSystem {
    constructor() {
        this.activeModal = null;
    }

    /**
     * Show a confirmation modal
     * @param {string} title - Modal title
     * @param {string} message - Main message
     * @param {string} details - Additional details (optional)
     * @param {string} confirmText - Confirm button text
     * @param {string} cancelText - Cancel button text
     * @param {Function} onConfirm - Callback when confirmed
     * @returns {HTMLElement} The modal element
     */
    showConfirmation(title, message, details, confirmText, cancelText, onConfirm) {
        // Create modal overlay
        const overlay = document.createElement('div');
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        // Create modal
        const modal = document.createElement('div');
        modal.style.cssText = `
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            padding: 24px;
            max-width: 400px;
            width: 90%;
            transform: scale(0.9);
            transition: transform 0.3s ease;
        `;

        modal.innerHTML = `
            <div style="margin-bottom: 16px;">
                <h3 style="color: #2c3e50; font-size: 18px; font-weight: 600; margin-bottom: 8px;">${title}</h3>
                <p style="color: #6c757d; font-size: 14px; line-height: 1.4;">${message}</p>
                ${details ? `<p style="color: #6c757d; font-size: 13px; line-height: 1.4; margin-top: 8px;">${details}</p>` : ''}
            </div>
            <div style="display: flex; gap: 12px; justify-content: flex-end;">
                <button class="modal-cancel-btn" style="
                    background: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: background 0.2s ease;
                ">${cancelText}</button>
                <button class="modal-confirm-btn" style="
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: background 0.2s ease;
                ">${confirmText}</button>
            </div>
        `;

        overlay.appendChild(modal);
        document.body.appendChild(overlay);

        // Animate in
        setTimeout(() => {
            overlay.style.opacity = '1';
            modal.style.transform = 'scale(1)';
        }, 10);

        // Store reference
        this.activeModal = overlay;

        // Add event listeners
        const cancelBtn = modal.querySelector('.modal-cancel-btn');
        const confirmBtn = modal.querySelector('.modal-confirm-btn');

        const closeModal = () => {
            overlay.style.opacity = '0';
            modal.style.transform = 'scale(0.9)';
            setTimeout(() => {
                document.body.removeChild(overlay);
                this.activeModal = null;
            }, 300);
        };

        cancelBtn.addEventListener('click', closeModal);
        confirmBtn.addEventListener('click', () => {
            closeModal();
            if (onConfirm) onConfirm();
        });

        // Close on overlay click
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal();
            }
        });

        // Close on escape key
        const handleEscape = (e) => {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);

        return overlay;
    }

    /**
     * Close the currently active modal
     */
    close() {
        if (this.activeModal && this.activeModal.parentElement) {
            const modal = this.activeModal.querySelector('div');
            this.activeModal.style.opacity = '0';
            if (modal) modal.style.transform = 'scale(0.9)';

            setTimeout(() => {
                if (this.activeModal && this.activeModal.parentElement) {
                    document.body.removeChild(this.activeModal);
                }
                this.activeModal = null;
            }, 300);
        }
    }
}

// Initialize global modal system
const modalSystem = new ModalSystem();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalSystem;
}
