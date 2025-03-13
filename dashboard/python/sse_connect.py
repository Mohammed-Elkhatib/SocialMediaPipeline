from imports import *
print("Initializing FastAPI app...")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use specific domains in production)
    allow_methods=["GET"],
    allow_headers=["*"],
)
import endpoints
app.include_router(sse_router)
# ✅ Keep the server running!
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
