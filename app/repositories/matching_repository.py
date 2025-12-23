"""Repository for matching-related database operations."""
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student


class MatchingRepository:
    """Repository for matching operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db

    async def get_all_students(self) -> List[Student]:
        """Get all students.

        Returns:
            List of all students
        """
        result = await self.db.execute(select(Student))
        return list(result.scalars().all())

    async def get_unmatched_students(
        self,
        gender: Optional[str] = None,
        is_smoker: Optional[bool] = None
    ) -> List[Student]:
        """Get unmatched students with optional filters.

        Args:
            gender: Filter by gender (optional)
            is_smoker: Filter by smoking status (optional)

        Returns:
            List of unmatched students matching the criteria
        """
        query = select(Student).where(Student.is_matched == False)

        if gender is not None:
            query = query.where(Student.gender == gender)

        if is_smoker is not None:
            query = query.where(Student.is_smoker == is_smoker)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def assign_matches(
        self,
        assignments: List[tuple]  # List of (student_a, student_b, room_id, sat_a, sat_b)
    ) -> int:
        """Assign room matches to students.

        Args:
            assignments: List of tuples containing:
                (student_a, student_b, room_id, satisfaction_a, satisfaction_b)

        Returns:
            Number of students updated
        """
        count = 0

        for student_a, student_b, room_id, sat_a, sat_b in assignments:
            # Update student A
            student_a.is_matched = True
            student_a.matched_room_id = room_id
            student_a.my_satisfaction_score = sat_a
            student_a.partner_satisfaction_score = sat_b

            # Update student B
            student_b.is_matched = True
            student_b.matched_room_id = room_id
            student_b.my_satisfaction_score = sat_b
            student_b.partner_satisfaction_score = sat_a

            count += 2

        await self.db.commit()
        return count

    async def reset_all_matches(self) -> int:
        """Reset all matching data (set is_matched=False, clear room_id and scores).

        Returns:
            Number of students reset
        """
        result = await self.db.execute(
            update(Student)
            .values(
                is_matched=False,
                matched_room_id=None,
                my_satisfaction_score=None,
                partner_satisfaction_score=None,
                cluster_id=None
            )
        )
        await self.db.commit()
        return result.rowcount

    async def get_matching_statistics(self) -> dict:
        """Get current matching statistics.

        Returns:
            Dictionary with statistics about current matching state
        """
        # Get all students
        all_students = await self.get_all_students()
        total = len(all_students)

        # Count matched students
        matched = sum(1 for s in all_students if s.is_matched)
        unmatched = total - matched

        # Calculate matching rate
        matching_rate = (matched / total * 100) if total > 0 else 0.0

        return {
            "total_students": total,
            "matched_students": matched,
            "unmatched_students": unmatched,
            "matching_rate": matching_rate
        }

    async def get_matched_students_by_room(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get matched students grouped by room with pagination.

        Args:
            skip: Number of rooms to skip
            limit: Maximum number of rooms to return

        Returns:
            List of room assignment dictionaries
        """
        # Get all matched students
        query = select(Student).where(Student.is_matched == True).order_by(Student.matched_room_id)
        result = await self.db.execute(query)
        matched_students = list(result.scalars().all())

        # Group by room
        rooms_dict = {}
        for student in matched_students:
            room_id = student.matched_room_id
            if room_id not in rooms_dict:
                rooms_dict[room_id] = []
            rooms_dict[room_id].append(student)

        # Build room assignments
        rooms = []
        for room_id in sorted(rooms_dict.keys()):
            students_in_room = rooms_dict[room_id]
            if len(students_in_room) == 2:
                student_a, student_b = students_in_room
                rooms.append({
                    "room_id": room_id,
                    "student_a_id": student_a.student_id,
                    "student_a_name": student_a.name,
                    "student_a_satisfaction": student_a.my_satisfaction_score,
                    "student_b_id": student_b.student_id,
                    "student_b_name": student_b.name,
                    "student_b_satisfaction": student_b.my_satisfaction_score,
                    "average_satisfaction": (
                        student_a.my_satisfaction_score + student_b.my_satisfaction_score
                    ) / 2 if student_a.my_satisfaction_score and student_b.my_satisfaction_score else 0.0
                })

        # Apply pagination
        return rooms[skip:skip + limit]

    async def count_matched_rooms(self) -> int:
        """Count the number of matched rooms.

        Returns:
            Number of rooms with matched students
        """
        query = select(Student).where(Student.is_matched == True)
        result = await self.db.execute(query)
        matched_students = list(result.scalars().all())

        # Count unique room IDs
        room_ids = set(s.matched_room_id for s in matched_students if s.matched_room_id is not None)
        return len(room_ids)

    async def get_detailed_statistics(self) -> dict:
        """Get detailed statistics about matching results.

        Returns:
            Dictionary with comprehensive statistics
        """
        import statistics

        # Get all matched students
        query = select(Student).where(Student.is_matched == True)
        result = await self.db.execute(query)
        matched_students = list(result.scalars().all())

        if not matched_students:
            return {
                "total_rooms": 0,
                "total_students": 0,
                "average_satisfaction": 0.0,
                "median_satisfaction": 0.0,
                "min_satisfaction": 0.0,
                "max_satisfaction": 0.0,
                "std_satisfaction": 0.0,
                "average_room_satisfaction": 0.0,
                "median_room_satisfaction": 0.0,
                "min_room_satisfaction": 0.0,
                "max_room_satisfaction": 0.0,
                "std_room_satisfaction": 0.0,
                "satisfaction_distribution": {
                    "0-20": 0,
                    "20-40": 0,
                    "40-60": 0,
                    "60-80": 0,
                    "80-100": 0
                }
            }

        # Collect individual satisfaction scores
        individual_scores = [
            s.my_satisfaction_score for s in matched_students
            if s.my_satisfaction_score is not None
        ]

        # Group by room and calculate room averages
        rooms_dict = {}
        for student in matched_students:
            room_id = student.matched_room_id
            if room_id not in rooms_dict:
                rooms_dict[room_id] = []
            rooms_dict[room_id].append(student)

        room_averages = []
        for room_id, students_in_room in rooms_dict.items():
            if len(students_in_room) == 2:
                student_a, student_b = students_in_room
                if student_a.my_satisfaction_score and student_b.my_satisfaction_score:
                    avg = (student_a.my_satisfaction_score + student_b.my_satisfaction_score) / 2
                    room_averages.append(avg)

        # Calculate individual statistics
        avg_satisfaction = statistics.mean(individual_scores) if individual_scores else 0.0
        median_satisfaction = statistics.median(individual_scores) if individual_scores else 0.0
        min_satisfaction = min(individual_scores) if individual_scores else 0.0
        max_satisfaction = max(individual_scores) if individual_scores else 0.0
        std_satisfaction = statistics.stdev(individual_scores) if len(individual_scores) > 1 else 0.0

        # Calculate room statistics
        avg_room = statistics.mean(room_averages) if room_averages else 0.0
        median_room = statistics.median(room_averages) if room_averages else 0.0
        min_room = min(room_averages) if room_averages else 0.0
        max_room = max(room_averages) if room_averages else 0.0
        std_room = statistics.stdev(room_averages) if len(room_averages) > 1 else 0.0

        # Calculate distribution
        distribution = {
            "0-20": 0,
            "20-40": 0,
            "40-60": 0,
            "60-80": 0,
            "80-100": 0
        }

        for score in individual_scores:
            if score < 20:
                distribution["0-20"] += 1
            elif score < 40:
                distribution["20-40"] += 1
            elif score < 60:
                distribution["40-60"] += 1
            elif score < 80:
                distribution["60-80"] += 1
            else:
                distribution["80-100"] += 1

        return {
            "total_rooms": len(rooms_dict),
            "total_students": len(matched_students),
            "average_satisfaction": round(avg_satisfaction, 2),
            "median_satisfaction": round(median_satisfaction, 2),
            "min_satisfaction": round(min_satisfaction, 2),
            "max_satisfaction": round(max_satisfaction, 2),
            "std_satisfaction": round(std_satisfaction, 2),
            "average_room_satisfaction": round(avg_room, 2),
            "median_room_satisfaction": round(median_room, 2),
            "min_room_satisfaction": round(min_room, 2),
            "max_room_satisfaction": round(max_room, 2),
            "std_room_satisfaction": round(std_room, 2),
            "satisfaction_distribution": distribution
        }