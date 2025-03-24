from dashboard.python.imports import *
from dashboard.python.endpoints import *
from dashboard.python.scheduler import get_scheduler

print("Initializing FastAPI app...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_methods=["GET", "POST"],  # Added POST for the scheduler endpoints
    allow_headers=["*"],
)

app.include_router(sse_router)


@app.on_event("startup")
async def startup_event():
    """Initialize and start the scheduler when the application starts"""
    scheduler = get_scheduler()
    scheduler.start()
    print("Data refresh scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when the application shuts down"""
    scheduler = get_scheduler()
    scheduler.stop()
    print("Data refresh scheduler stopped")

# Keep the server running!
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
