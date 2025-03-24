// dashboard/js/start.js

function UpdateAllForHome() {
    console.log("Updating all dashboard components...");
    updateChart();
    updateHeatmap();
    createProgressBars();
    updateSocialData();
    updateWordCloud();
    updateChartData('comments'); // Updated to match the function name in chart-bar-demo.js
    updateBubbleChart();
}

// Function to show a notification when new data is available
function showRefreshNotification() {
    // You can implement a more sophisticated notification here
    // This is a simple example using the browser's notification API
    if ("Notification" in window && Notification.permission === "granted") {
        new Notification("Dashboard Updated", {
            body: "New social media data has been loaded.",
            icon: "/dashboard/img/refresh-icon.png" // Add an appropriate icon
        });
    }
    
    // Alternatively, you could show an on-screen notification
    const notification = document.createElement('div');
    notification.classList.add('refresh-notification');
    notification.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <strong>Data Refreshed!</strong> Dashboard has been updated with the latest data.
            <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
    `;
    
    // Append to the top of the page
    document.body.insertBefore(notification, document.body.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Get scheduler status and display it
async function updateSchedulerStatus() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/scheduler-status');
        const status = await response.json();
        
        // Update UI with scheduler status if you have status elements
        const statusElement = document.getElementById('scheduler-status');
        if (statusElement) {
            statusElement.textContent = status.running ? 'Running' : 'Stopped';
            statusElement.className = status.running ? 'text-success' : 'text-danger';
        }
        
        const lastRefreshElement = document.getElementById('last-refresh');
        if (lastRefreshElement && status.last_refresh) {
            const refreshTime = new Date(status.last_refresh);
            lastRefreshElement.textContent = refreshTime.toLocaleString();
        }
        
        const intervalElement = document.getElementById('refresh-interval');
        if (intervalElement) {
            intervalElement.textContent = `${status.interval_minutes} minutes`;
        }
    } catch (error) {
        console.error('Error fetching scheduler status:', error);
    }
}

// Add event listener for manual refresh button if it exists
document.addEventListener('DOMContentLoaded', function() {
    const refreshButton = document.getElementById('manual-refresh');
    if (refreshButton) {
        refreshButton.addEventListener('click', async function() {
            try {
                const response = await fetch('http://127.0.0.1:8000/api/refresh-data', {
                    method: 'POST'
                });
                const result = await response.json();
                console.log('Manual refresh triggered:', result);
                
                // Show loading indicator
                refreshButton.disabled = true;
                refreshButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
                
                // Re-enable after 5 seconds
                setTimeout(() => {
                    refreshButton.disabled = false;
                    refreshButton.innerHTML = 'Refresh Data';
                }, 5000);
            } catch (error) {
                console.error('Error triggering manual refresh:', error);
            }
        });
    }
    
    // Initial status update
    updateSchedulerStatus();
    
    // Schedule status updates every minute
    setInterval(updateSchedulerStatus, 60000);
});