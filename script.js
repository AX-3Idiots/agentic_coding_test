class Timer {
    constructor() {
        // DOM 요소들
        this.timerDisplay = document.getElementById('timerDisplay');
        this.minutesInput = document.getElementById('minutes');
        this.secondsInput = document.getElementById('seconds');
        this.startBtn = document.getElementById('startBtn');
        this.pauseBtn = document.getElementById('pauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.completionMessage = document.getElementById('completionMessage');
        this.alertSound = document.getElementById('alertSound');
        
        // 타이머 상태
        this.totalSeconds = 0;
        this.currentSeconds = 0;
        this.isRunning = false;
        this.intervalId = null;
        
        this.init();
    }
    
    init() {
        // 이벤트 리스너 등록
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
        
        // 입력 필드 이벤트 리스너
        this.minutesInput.addEventListener('input', () => this.updateDisplay());
        this.secondsInput.addEventListener('input', () => this.updateDisplay());
        
        // 입력 필드 검증
        this.minutesInput.addEventListener('blur', () => this.validateInput(this.minutesInput, 59));
        this.secondsInput.addEventListener('blur', () => this.validateInput(this.secondsInput, 59));
        
        // 엔터 키로 시작
        this.minutesInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.start();
        });
        this.secondsInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.start();
        });
        
        this.updateButtonStates();
    }
    
    validateInput(input, max) {
        let value = parseInt(input.value);
        if (isNaN(value) || value < 0) {
            input.value = 0;
        } else if (value > max) {
            input.value = max;
        }
        this.updateDisplay();
    }
    
    updateDisplay() {
        if (!this.isRunning) {
            const minutes = parseInt(this.minutesInput.value) || 0;
            const seconds = parseInt(this.secondsInput.value) || 0;
            this.totalSeconds = minutes * 60 + seconds;
            this.currentSeconds = this.totalSeconds;
        }
        
        const displayMinutes = Math.floor(this.currentSeconds / 60);
        const displaySeconds = this.currentSeconds % 60;
        
        this.timerDisplay.textContent = 
            `${displayMinutes.toString().padStart(2, '0')}:${displaySeconds.toString().padStart(2, '0')}`;
    }
    
    start() {
        if (this.isRunning) return;
        
        // 입력값에서 시간 설정 (처음 시작할 때만)
        if (this.currentSeconds === 0) {
            const minutes = parseInt(this.minutesInput.value) || 0;
            const seconds = parseInt(this.secondsInput.value) || 0;
            this.totalSeconds = minutes * 60 + seconds;
            this.currentSeconds = this.totalSeconds;
        }
        
        if (this.currentSeconds <= 0) {
            alert('시간을 설정해주세요!');
            return;
        }
        
        this.isRunning = true;
        this.completionMessage.classList.add('hidden');
        
        this.intervalId = setInterval(() => {
            this.currentSeconds--;
            this.updateDisplay();
            
            if (this.currentSeconds <= 0) {
                this.complete();
            }
        }, 1000);
        
        this.updateButtonStates();
    }
    
    pause() {
        if (!this.isRunning) return;
        
        this.isRunning = false;
        clearInterval(this.intervalId);
        this.updateButtonStates();
    }
    
    reset() {
        this.isRunning = false;
        clearInterval(this.intervalId);
        
        this.currentSeconds = 0;
        this.totalSeconds = 0;
        this.minutesInput.value = 0;
        this.secondsInput.value = 0;
        
        this.updateDisplay();
        this.completionMessage.classList.add('hidden');
        this.updateButtonStates();
    }
    
    complete() {
        this.isRunning = false;
        clearInterval(this.intervalId);
        
        // 완료 메시지 표시
        this.completionMessage.classList.remove('hidden');
        
        // 알림음 재생
        this.playAlertSound();
        
        this.updateButtonStates();
    }
    
    playAlertSound() {
        // 브라우저 내장 알림음 사용
        try {
            this.alertSound.play().catch(() => {
                // 알림음 재생 실패 시 기본 알림 사용
                if ('Notification' in window) {
                    new Notification('타이머 완료!', {
                        body: '타이머가 완료되었습니다.',
                        icon: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyUzYuNDggMjIgMTIgMjJTMjIgMTcuNTIgMjIgMTJTMTcuNTIgMiAxMiAyWk0xMyAxN0gxMVYxNUgxM1YxN1pNMTMgMTNIMTFWN0gxM1YxM1oiIGZpbGw9IiM0Q0FGNTAIILN2Zz4K'
                    });
                } else {
                    // Notification API 미지원 시 브라우저 알림 사용
                    alert('타이머가 완료되었습니다!');
                }
            });
        } catch (error) {
            // 모든 알림 실패 시 기본 alert 사용
            alert('타이머가 완료되었습니다!');
        }
    }
    
    updateButtonStates() {
        if (this.isRunning) {
            this.startBtn.disabled = true;
            this.pauseBtn.disabled = false;
            this.resetBtn.disabled = false;
            this.minutesInput.disabled = true;
            this.secondsInput.disabled = true;
        } else {
            this.startBtn.disabled = false;
            this.pauseBtn.disabled = true;
            this.resetBtn.disabled = false;
            this.minutesInput.disabled = false;
            this.secondsInput.disabled = false;
        }
    }
}

// 페이지 로드 시 타이머 초기화
document.addEventListener('DOMContentLoaded', () => {
    new Timer();
    
    // 알림 권한 요청 (옵션)
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});