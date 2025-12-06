/**
 * Prophere Keyword Tagging System
 * Handles tag-based keyword input functionality
 */

class KeywordInput {
    constructor(inputElement, tagsContainer) {
        this.input = inputElement;
        this.tagsContainer = tagsContainer;
        this.tags = [];
        this.init();
    }

    init() {
        // Handle Enter key
        this.input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                const value = this.input.value.trim();
                if (value && !this.isDuplicate(value)) {
                    this.addTag(value);
                    this.input.value = '';
                }
            }
        });

        // Handle blur (optional - add tag when focus lost)
        this.input.addEventListener('blur', () => {
            const value = this.input.value.trim();
            if (value && !this.isDuplicate(value)) {
                this.addTag(value);
                this.input.value = '';
            }
        });
    }

    addTag(text) {
        const tag = document.createElement('div');
        tag.className = 'input-tag';
        tag.innerHTML = `${text}<span class="remove-tag">×</span>`;

        // Add remove functionality
        const removeBtn = tag.querySelector('.remove-tag');
        removeBtn.addEventListener('click', () => this.removeTag(tag));

        this.tagsContainer.appendChild(tag);
        this.tags.push(tag);
    }

    removeTag(tag) {
        tag.remove();
        const index = this.tags.indexOf(tag);
        if (index > -1) {
            this.tags.splice(index, 1);
        }
    }

    isDuplicate(text) {
        return Array.from(this.tags).some(tag => {
            let existingText = tag.textContent || tag.innerText || '';
            existingText = existingText.replace(/×/g, '').trim();
            return existingText.toLowerCase() === text.toLowerCase();
        });
    }

    getTags() {
        return Array.from(this.tags).map(tag => {
            let text = tag.textContent || tag.innerText || '';
            text = text.replace(/×/g, '').trim();
            return text;
        }).filter(text => text.length > 0);
    }

    getTagsAsString() {
        return this.getTags().join(',');
    }

    clear() {
        this.tags.forEach(tag => tag.remove());
        this.tags = [];
    }

    loadTags(tagArray) {
        this.clear();
        tagArray.forEach(tag => {
            if (tag.trim()) {
                this.addTag(tag.trim());
            }
        });
    }
}

// Auto-initialize keyword inputs on page load
document.addEventListener('DOMContentLoaded', function () {
    // Find all keyword input containers
    document.querySelectorAll('.keywords-input-container').forEach(container => {
        const input = container.querySelector('input');
        const tagsContainer = container.querySelector('.keywords-tags') ||
            document.createElement('div');

        if (!container.querySelector('.keywords-tags')) {
            tagsContainer.className = 'keywords-tags';
            container.insertBefore(tagsContainer, input);
        }

        if (input) {
            // Store instance on the input element for later access
            input.keywordInput = new KeywordInput(input, tagsContainer);
        }
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KeywordInput;
}
