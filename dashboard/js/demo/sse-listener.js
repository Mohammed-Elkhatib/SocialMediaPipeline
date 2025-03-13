const eventSource = new EventSource("http://127.0.0.1:8000/sse/home");
const eventSourceTwitter = new EventSource("http://127.0.0.1:8000/sse/twitter");
eventSource.onmessage = function(event) {
    UpdateAllForHome();
};
eventSourceTwitter.onmessage = function(event) {
    UpdateAllForTwitter();
};