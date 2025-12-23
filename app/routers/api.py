from fastapi import APIRouter
from app.routers import student

api_router = APIRouter()

# Include student router
api_router.include_router(student.router)