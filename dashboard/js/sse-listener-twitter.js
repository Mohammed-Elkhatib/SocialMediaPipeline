
const eventSourceTwitter = new EventSource("http://127.0.0.1:8000/sse/twitter");

eventSourceTwitter.onmessage = function(event) {
    UpdateAllForTwitter();
};