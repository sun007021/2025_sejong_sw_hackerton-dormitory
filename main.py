from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routers.api import api_router
from app.exceptions.student import (
    StudentNotFoundException,
    StudentAlreadyExistsException,
    InvalidStudentDataException,
)

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dormitory Roommate Matching System Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(StudentNotFoundException)
async def student_not_found_exception_handler(
    request: Request, exc: StudentNotFoundException
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.message},
    )


@app.exception_handler(StudentAlreadyExistsException)
async def student_already_exists_exception_handler(
    request: Request, exc: StudentAlreadyExistsException
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.message},
    )


@app.exception_handler(InvalidStudentDataException)
async def invalid_student_data_exception_handler(
    request: Request, exc: InvalidStudentDataException
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.message},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Dormitory Roommate Matching System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy"}
