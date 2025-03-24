# dashboard/python/sse_router.py
import time
import os
from fastapi import APIRouter, BackgroundTasks
from starlette.responses import StreamingResponse
from datetime import datetime
from src.analytics.service import AnalyticsService
from dashboard.python.scheduler import get_scheduler

router = APIRouter()

# Keep track of the last modification time of the trigger file
last_trigger_check = 0
last_trigger_time = 0


def get_trigger_time():
    """Get the last modification time of the trigger file"""
    global last_trigger_check, last_trigger_time

    # Only check the file every few seconds to reduce I/O
    current_time = time.time()
    if current_time - last_trigger_check < 3:  # Check every 3 seconds
        return last_trigger_time

    trigger_file = os.path.join(os.path.dirname(__file__), "sse_trigger.txt")

    try:
        if os.path.exists(trigger_file):
            mtime = os.path.getmtime(trigger_file)
            last_trigger_time = mtime
        else:
            # If file doesn't exist, create it
            with open(trigger_file, "w") as f:
                f.write(f"Initial trigger at {datetime.now().isoformat()}")
            last_trigger_time = time.time()
    except Exception:
        pass

    last_trigger_check = current_time
    return last_trigger_time


@router.get("/sse/home")
def sse_home():
    # Get the initial trigger time
    last_update = get_trigger_time()

    def event_stream():
        nonlocal last_update

        # Send initial message
        yield f"data: Connected to SSE. Server time is {time.ctime()}\n\n"

        while True:
            # Check if there's been a data update
            current_update = get_trigger_time()

            if current_update > last_update:
                analytics_service = AnalyticsService()
                success = analytics_service.run_all_analyses(time_period="day", platform="x")

                if success:
                    print("Analytics successfully completed.")
                else:
                    print("Analytics failed. Check logs for details.")
                # Data has been updated, send notification to client
                yield f"data: Data refreshed at {datetime.fromtimestamp(current_update).isoformat()}\n\n"
                last_update = current_update

            # Send a heartbeat every 30 seconds to keep the connection alive
            yield f"data: heartbeat\n\n"

            # Sleep for a short interval
            time.sleep(5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# Add a new endpoint to manually trigger data refresh
@router.post("/api/refresh-data")
async def refresh_data(background_tasks: BackgroundTasks):
    """Manually trigger a data refresh"""
    scheduler = get_scheduler()

    # Run the refresh in a background task to avoid blocking
    background_tasks.add_task(scheduler.run_main_script)

    return {"status": "Data refresh started"}


# Add a new endpoint to get scheduler status
@router.get("/api/scheduler-status")
def get_scheduler_status():
    """Get the current status of the scheduler"""
    scheduler = get_scheduler()
    return scheduler.get_status()


# Add endpoints to start/stop the scheduler
@router.post("/api/scheduler/start")
def start_scheduler(interval_minutes: int = 10):
    """Start the scheduler with the specified interval"""
    scheduler = get_scheduler()
    scheduler.interval_minutes = interval_minutes
    scheduler.start()
    return {"status": "Scheduler started", "interval_minutes": interval_minutes}


@router.post("/api/scheduler/stop")
def stop_scheduler():
    """Stop the scheduler"""
    scheduler = get_scheduler()
    scheduler.stop()
    return {"status": "Scheduler stopped"}
