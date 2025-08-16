class MemoApp {
    constructor() {
        this.memos = this.loadMemos();
        this.initializeElements();
        this.attachEventListeners();
        this.renderMemos();
    }

    initializeElements() {
        this.memoInput = document.getElementById('memoInput');
        this.saveBtn = document.getElementById('saveBtn');
        this.charCounter = document.getElementById('charCounter');
        this.memoList = document.getElementById('memoList');
    }

    attachEventListeners() {
        this.memoInput.addEventListener('input', () => this.updateCharCounter());
        this.memoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.saveMemo();
            }
        });
        this.saveBtn.addEventListener('click', () => this.saveMemo());
    }

    updateCharCounter() {
        const length = this.memoInput.value.length;
        this.charCounter.textContent = `${length}/140`;
        
        if (length > 120) {
            this.charCounter.classList.add('warning');
        } else {
            this.charCounter.classList.remove('warning');
        }
    }

    saveMemo() {
        const content = this.memoInput.value.trim();
        
        if (!content) {
            alert('메모 내용을 입력해주세요.');
            return;
        }

        const memo = {
            id: Date.now(),
            content: content,
            timestamp: new Date().toISOString(),
            displayTime: this.formatDateTime(new Date())
        };

        this.memos.unshift(memo); // Add to beginning for newest first
        this.saveMemos();
        this.renderMemos();
        
        // Clear input
        this.memoInput.value = '';
        this.updateCharCounter();
        this.memoInput.focus();
    }

    deleteMemo(id) {
        if (confirm('이 메모를 삭제하시겠습니까?')) {
            this.memos = this.memos.filter(memo => memo.id !== id);
            this.saveMemos();
            this.renderMemos();
        }
    }

    renderMemos() {
        if (this.memos.length === 0) {
            this.memoList.innerHTML = '<div class="empty-message">저장된 메모가 없습니다.</div>';
            return;
        }

        const memoHtml = this.memos.map(memo => {
            const truncatedContent = this.truncateText(memo.content, 140);
            
            return `
                <div class="memo-item" data-id="${memo.id}">
                    <div class="memo-content">${this.escapeHtml(truncatedContent)}</div>
                    <div class="memo-meta">
                        <span class="memo-time">${memo.displayTime}</span>
                        <button class="delete-btn" onclick="memoApp.deleteMemo(${memo.id})">삭제</button>
                    </div>
                </div>
            `;
        }).join('');

        this.memoList.innerHTML = memoHtml;
    }

    truncateText(text, maxLength) {
        if (text.length <= maxLength) {
            return text;
        }
        return text.substring(0, maxLength) + '...';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    formatDateTime(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
    }

    loadMemos() {
        try {
            const saved = localStorage.getItem('memos');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Failed to load memos:', error);
            return [];
        }
    }

    saveMemos() {
        try {
            localStorage.setItem('memos', JSON.stringify(this.memos));
        } catch (error) {
            console.error('Failed to save memos:', error);
            alert('메모 저장에 실패했습니다.');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.memoApp = new MemoApp();
});