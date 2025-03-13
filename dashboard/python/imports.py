from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import time
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from .sse_router import router as sse_router  # Import the router
from fastapi import APIRouter
print("Initializing imports...")

app=FastAPI()