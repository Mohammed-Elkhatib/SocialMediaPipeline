import time
from fastapi import APIRouter
from starlette.responses import StreamingResponse

router = APIRouter()

@router.get("/sse/home")
def sse_home():
    def event_stream():
        while True:
            time.sleep(100)  # Simulate live updates
            yield f"data: Server time is {time.ctime()}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")