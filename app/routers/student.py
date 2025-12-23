from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.repositories.student import StudentRepository
from app.services.student import StudentService
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.schemas.common import PaginatedResponse
from app.exceptions.student import (
    StudentNotFoundException,
    StudentAlreadyExistsException,
)

router = APIRouter(prefix="/students", tags=["students"])


@router.post(
    "/",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Create a new student with all required information for dormitory matching",
)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new student.

    - **student_id**: University student ID (unique)
    - **name**: Student name
    - **age**: Student age (18-100)
    - **gender**: Gender (male, female, other)
    - **is_smoker**: Smoking status (hard filter)
    - Other fields: lifestyle, noise, major, cleaning, personality preferences
    - Weights: 0-100 for each category (0=doesn't matter, 100=most important)
    """
    repository = StudentRepository(db)
    service = StudentService(repository)

    try:
        new_student = await service.create_student(student)
        return new_student
    except StudentAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        )


@router.get(
    "/",
    response_model=PaginatedResponse[StudentResponse],
    summary="Get all students",
    description="Get all students with pagination and optional filters",
)
async def get_students(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    is_smoker: Optional[bool] = Query(None, description="Filter by smoking status"),
    major_name: Optional[str] = Query(None, description="Filter by major"),
    is_matched: Optional[bool] = Query(None, description="Filter by matching status"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all students with optional filtering.

    Query parameters:
    - **skip**: Offset for pagination (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    - **gender**: Filter by gender (optional)
    - **is_smoker**: Filter by smoking status (optional)
    - **major_name**: Filter by major name (optional)
    - **is_matched**: Filter by matching status (optional)
    """
    repository = StudentRepository(db)
    service = StudentService(repository)

    students, total = await service.get_students(
        skip=skip,
        limit=limit,
        gender=gender,
        is_smoker=is_smoker,
        major_name=major_name,
        is_matched=is_matched,
    )

    return PaginatedResponse(
        total=total,
        items=students,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Get student by student ID",
    description="Get a specific student by their university student ID",
)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific student by student ID.

    - **student_id**: University student ID (e.g., "20210001")
    """
    repository = StudentRepository(db)
    service = StudentService(repository)

    try:
        student = await service.get_student_by_student_id(student_id)
        return student
    except StudentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    summary="Update student information",
    description="Update student information (partial update supported)",
)
async def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update student information.

    - **student_id**: University student ID (path parameter)
    - Provide only the fields you want to update in the request body
    - All fields are optional for update
    """
    repository = StudentRepository(db)
    service = StudentService(repository)

    try:
        updated_student = await service.update_student(student_id, student_update)
        return updated_student
    except StudentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete student",
    description="Delete a student by their student ID",
)
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a student.

    - **student_id**: University student ID
    """
    repository = StudentRepository(db)
    service = StudentService(repository)

    try:
        await service.delete_student(student_id)
    except StudentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )