"""
AI Service - Mock implementation for dog monitoring
Provides vision processing and coaching endpoints with fake data
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import vision, coach, models

app = FastAPI(
    title="Dog Monitor AI Service",
    description="AI service for vision processing and coaching",
    version="1.0.0"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vision.router, prefix="/vision", tags=["vision"])
app.include_router(coach.router, prefix="/coach", tags=["coach"])
app.include_router(models.router, prefix="/models", tags=["models"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Dog Monitor AI Service",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
