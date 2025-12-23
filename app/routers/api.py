from fastapi import APIRouter
from app.routers import student, matching

api_router = APIRouter()

# Include routers
api_router.include_router(student.router)
api_router.include_router(matching.router)