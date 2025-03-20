const eventSource = new EventSource("http://127.0.0.1:8000/sse/home");
eventSource.onmessage = function(event) {
    UpdateAllForHome();
};
