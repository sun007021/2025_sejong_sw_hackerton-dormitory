from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate


class StudentRepository:
    """Repository for Student data access operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, student_data: StudentCreate) -> Student:
        """
        Create a new student.

        Args:
            student_data: Student creation data

        Returns:
            Created student instance
        """
        student = Student(**student_data.model_dump())
        self.db.add(student)
        await self.db.flush()
        await self.db.refresh(student)
        return student

    async def get_by_id(self, student_uuid: UUID) -> Optional[Student]:
        """
        Get student by UUID.

        Args:
            student_uuid: Student UUID

        Returns:
            Student instance or None if not found
        """
        result = await self.db.execute(
            select(Student).where(Student.id == student_uuid)
        )
        return result.scalar_one_or_none()

    async def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """
        Get student by student ID (university ID).

        Args:
            student_id: University student ID

        Returns:
            Student instance or None if not found
        """
        result = await self.db.execute(
            select(Student).where(Student.student_id == student_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Student]:
        """
        Get all students with pagination and optional filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters (gender, is_smoker, major_name, is_matched)

        Returns:
            List of students
        """
        query = select(Student)

        # Apply filters
        if filters:
            conditions = []
            if "gender" in filters and filters["gender"] is not None:
                conditions.append(Student.gender == filters["gender"])
            if "is_smoker" in filters and filters["is_smoker"] is not None:
                conditions.append(Student.is_smoker == filters["is_smoker"])
            if "major_name" in filters and filters["major_name"] is not None:
                conditions.append(Student.major_name == filters["major_name"])
            if "is_matched" in filters and filters["is_matched"] is not None:
                conditions.append(Student.is_matched == filters["is_matched"])

            if conditions:
                query = query.where(and_(*conditions))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count total students with optional filters.

        Args:
            filters: Optional filters (gender, is_smoker, major_name, is_matched)

        Returns:
            Total count of students
        """
        query = select(func.count(Student.id))

        # Apply filters
        if filters:
            conditions = []
            if "gender" in filters and filters["gender"] is not None:
                conditions.append(Student.gender == filters["gender"])
            if "is_smoker" in filters and filters["is_smoker"] is not None:
                conditions.append(Student.is_smoker == filters["is_smoker"])
            if "major_name" in filters and filters["major_name"] is not None:
                conditions.append(Student.major_name == filters["major_name"])
            if "is_matched" in filters and filters["is_matched"] is not None:
                conditions.append(Student.is_matched == filters["is_matched"])

            if conditions:
                query = query.where(and_(*conditions))

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, student: Student, update_data: StudentUpdate) -> Student:
        """
        Update student information.

        Args:
            student: Student instance to update
            update_data: Update data (only non-None fields will be updated)

        Returns:
            Updated student instance
        """
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(student, key, value)

        await self.db.flush()
        await self.db.refresh(student)
        return student

    async def delete(self, student: Student) -> None:
        """
        Delete a student.

        Args:
            student: Student instance to delete
        """
        await self.db.delete(student)
        await self.db.flush()

    async def exists_by_student_id(self, student_id: str) -> bool:
        """
        Check if student exists by student ID.

        Args:
            student_id: University student ID

        Returns:
            True if student exists, False otherwise
        """
        result = await self.db.execute(
            select(func.count(Student.id)).where(Student.student_id == student_id)
        )
        count = result.scalar_one()
        return count > 0