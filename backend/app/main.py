"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import __version__
from app.routes import calculate, preferences
from app.models import HealthResponse


# Create FastAPI app
app = FastAPI(
    title="SleepCycle-Alarm API",
    description=(
        "Calculate optimal bedtimes based on sleep cycles. "
        "Helps you wake up refreshed by aligning wake time with sleep cycle completion."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend (served on a different port) to call this API
# NOTE: allow_origins=["*"] is for development/sharing with friends.
# For production, specify exact domains.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development only)
    allow_credentials=False,  # Must be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(calculate.router, prefix="/api/v1", tags=["Calculate"])
app.include_router(preferences.router, prefix="/api/v1", tags=["Preferences"])


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        version=__version__
    )


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=__version__
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
