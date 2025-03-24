// dashboard/js/sse-listener-home.js

const eventSource = new EventSource("http://127.0.0.1:8000/sse/home");

// Handle connection open
eventSource.onopen = function() {
    console.log("SSE connection established");
};

// Handle messages
eventSource.onmessage = function(event) {
    // Ignore heartbeat messages
    if (event.data === "heartbeat") {
        return;
    }
    
    console.log("SSE event received:", event.data);
    
    // Check if the message indicates a data refresh
    if (event.data.includes("Data refreshed")) {
        console.log("Data refresh detected, updating dashboard...");
        
        // Update all dashboard components
        UpdateAllForHome();
        
        // Show a notification to the user
        showRefreshNotification();
        
        // Update scheduler status
        updateSchedulerStatus();
    }
};

// Handle errors
eventSource.onerror = function(error) {
    console.error("SSE connection error:", error);
    
    // Try to reconnect after a delay
    setTimeout(() => {
        console.log("Attempting to reconnect to SSE...");
        eventSource.close();
        
        // Create a new connection
        const newEventSource = new EventSource("http://127.0.0.1:8000/sse/home");
        eventSource = newEventSource;
    }, 5000);
};