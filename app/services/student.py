from typing import List, Dict, Any, Optional, Tuple

from app.models.student import Student
from app.repositories.student import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate
from app.exceptions.student import (
    StudentNotFoundException,
    StudentAlreadyExistsException,
)


class StudentService:
    """Service layer for student business logic."""

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    async def create_student(self, student_data: StudentCreate) -> Student:
        """
        Create a new student.

        Args:
            student_data: Student creation data

        Returns:
            Created student instance

        Raises:
            StudentAlreadyExistsException: If student ID already exists
        """
        # Check if student already exists
        if await self.repository.exists_by_student_id(student_data.student_id):
            raise StudentAlreadyExistsException(student_data.student_id)

        return await self.repository.create(student_data)

    async def get_student_by_student_id(self, student_id: str) -> Student:
        """
        Get student by student ID.

        Args:
            student_id: University student ID

        Returns:
            Student instance

        Raises:
            StudentNotFoundException: If student not found
        """
        student = await self.repository.get_by_student_id(student_id)
        if not student:
            raise StudentNotFoundException(student_id)
        return student

    async def get_students(
        self,
        skip: int = 0,
        limit: int = 100,
        gender: Optional[str] = None,
        is_smoker: Optional[bool] = None,
        major_name: Optional[str] = None,
        is_matched: Optional[bool] = None,
    ) -> Tuple[List[Student], int]:
        """
        Get all students with pagination and filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            gender: Filter by gender
            is_smoker: Filter by smoking status
            major_name: Filter by major
            is_matched: Filter by matching status

        Returns:
            Tuple of (list of students, total count)
        """
        # Build filters
        filters: Dict[str, Any] = {}
        if gender is not None:
            filters["gender"] = gender
        if is_smoker is not None:
            filters["is_smoker"] = is_smoker
        if major_name is not None:
            filters["major_name"] = major_name
        if is_matched is not None:
            filters["is_matched"] = is_matched

        # Validate limit
        if limit > 1000:
            limit = 1000

        # Get students and count
        students = await self.repository.get_all(
            skip=skip, limit=limit, filters=filters
        )
        total = await self.repository.count(filters=filters)

        return students, total

    async def update_student(
        self, student_id: str, update_data: StudentUpdate
    ) -> Student:
        """
        Update student information.

        Args:
            student_id: University student ID
            update_data: Update data

        Returns:
            Updated student instance

        Raises:
            StudentNotFoundException: If student not found
        """
        student = await self.repository.get_by_student_id(student_id)
        if not student:
            raise StudentNotFoundException(student_id)

        return await self.repository.update(student, update_data)

    async def delete_student(self, student_id: str) -> None:
        """
        Delete a student.

        Args:
            student_id: University student ID

        Raises:
            StudentNotFoundException: If student not found
        """
        student = await self.repository.get_by_student_id(student_id)
        if not student:
            raise StudentNotFoundException(student_id)

        await self.repository.delete(student)