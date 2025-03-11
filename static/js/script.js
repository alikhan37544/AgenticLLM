document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('startBtn');
    const controlArea = document.getElementById('controlArea');
    const progressArea = document.getElementById('progressArea');
    const progressBar = document.getElementById('progressBar');
    const statusMessage = document.getElementById('statusMessage');
    const errorMessage = document.getElementById('errorMessage');
    const resultsArea = document.getElementById('resultsArea');
    
    let statusCheckInterval;
    
    startBtn.addEventListener('click', function() {
        // Disable button and show progress area
        startBtn.disabled = true;
        progressArea.classList.remove('hidden');
        errorMessage.classList.add('hidden');
        resultsArea.classList.add('hidden');
        
        // Send request to start evaluation
        fetch('/start_evaluation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'started') {
                statusMessage.textContent = 'Evaluation started...';
                startStatusChecking();
            } else {
                showError(data.message || 'Failed to start evaluation');
            }
        })
        .catch(error => {
            showError('Error: ' + error.message);
        });
    });
    
    function startStatusChecking() {
        // Check status every 2 seconds
        statusCheckInterval = setInterval(checkStatus, 2000);
        checkStatus(); // Check immediately
    }
    
    function checkStatus() {
        fetch('/status')
            .then(response => response.json())
            .then(data => {
                // Update progress bar (interpolating if needed)
                updateProgressBar(data.progress);
                
                // Update status message
                if (data.message) {
                    statusMessage.textContent = data.message;
                }
                
                // Check for errors
                if (data.error) {
                    showError(data.error);
                    stopStatusChecking();
                    startBtn.disabled = false;
                }
                
                // Check if complete
                if (data.complete) {
                    updateProgressBar(100);
                    statusMessage.textContent = 'Evaluation completed successfully!';
                    resultsArea.classList.remove('hidden');
                    stopStatusChecking();
                    startBtn.disabled = false;
                }
                
                // If not running and not complete, something went wrong
                if (!data.running && !data.complete && !data.error) {
                    showError('Evaluation process stopped unexpectedly');
                    stopStatusChecking();
                    startBtn.disabled = false;
                }
            })
            .catch(error => {
                showError('Failed to check status: ' + error.message);
                stopStatusChecking();
                startBtn.disabled = false;
            });
    }
    
    function updateProgressBar(progress) {
        // If progress is not a number, use indeterminate progress
        if (isNaN(progress)) {
            progressBar.style.width = '100%';
            progressBar.textContent = 'Processing...';
        } else {
            let value = Math.min(Math.max(progress, 0), 100);
            progressBar.style.width = value + '%';
            progressBar.textContent = value + '%';
            progressBar.setAttribute('aria-valuenow', value);
        }
    }
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
    }
    
    function stopStatusChecking() {
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
            statusCheckInterval = null;
        }
    }
});