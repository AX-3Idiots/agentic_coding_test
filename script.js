class Timer {
    constructor() {
        this.timeLeft = 10;
        this.isRunning = false;
        this.intervalId = null;
        
        this.timerDisplay = document.getElementById('timerDisplay');
        this.startButton = document.getElementById('startButton');
        
        this.initializeEventListeners();
        this.updateDisplay();
    }
    
    initializeEventListeners() {
        this.startButton.addEventListener('click', () => {
            this.startTimer();
        });
    }
    
    startTimer() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.startButton.disabled = true;
        this.startButton.textContent = 'Running...';
        
        this.intervalId = setInterval(() => {
            this.timeLeft--;
            this.updateDisplay();
            
            if (this.timeLeft <= 0) {
                this.stopTimer();
            }
        }, 1000);
    }
    
    stopTimer() {
        this.isRunning = false;
        clearInterval(this.intervalId);
        this.intervalId = null;
        
        this.startButton.disabled = false;
        this.startButton.textContent = 'Start';
        
        // Reset timer for restart
        this.timeLeft = 10;
        this.updateDisplay();
    }
    
    updateDisplay() {
        this.timerDisplay.textContent = this.timeLeft;
    }
}

// Initialize timer when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Timer();
});