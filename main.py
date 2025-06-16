from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.routes.health import router as health_router
from app.routes.requirements import router as requirements_router
from app.routes.design import router as design_router
from app.routes.screens import router as screens_router
from app.routes.models import router as models_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="TUX API",
    description="AI-Powered UX Design Generator API - Transform text requirements into UX wireframes and UI mockups",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://www.tuxonline.live",  # Production domain
        "https://tuxonline.live",  # Production domain without www
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to TUX API - AI-Powered UX Design Generator", 
        "version": "1.0.0",
        "status": "active"
    }

# Include routers
app.include_router(health_router, tags=["health"])
app.include_router(requirements_router, prefix="/api", tags=["requirements"])
app.include_router(design_router, prefix="/api", tags=["design"])
app.include_router(screens_router, prefix="/api", tags=["screens"])
app.include_router(models_router, prefix="/api", tags=["models"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    ) 