from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from backend.src.routers import analysis

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Genomic Health Dashboard API",
    description="Backend API for Genomic Analysis and AI Health Coaching",
    version="1.0.0",
)

# Allow CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis.router)

@app.get("/api/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "Genomic Health Backend"}

if __name__ == "__main__":
    logger.info("Starting up Genomic Health Backend...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
