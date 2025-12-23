"""Service for executing roommate matching algorithm."""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student import Student
from app.repositories.matching_repository import MatchingRepository
from app.ml.matching import match_students_by_groups
from app.exceptions.matching import InsufficientStudentsException, NoUnmatchedStudentsException
from app.schemas.matching import MatchingStatistics


class MatchingService:
    """Service for roommate matching operations."""

    def __init__(self, db: AsyncSession):
        """Initialize service with database session.

        Args:
            db: AsyncSession for database operations
        """
        self.db = db
        self.repository = MatchingRepository(db)

    async def execute_matching(self, dry_run: bool = False) -> dict:
        """Execute the full matching pipeline.

        Pipeline:
        1. Hard filter: Group by gender and smoking status (4 groups)
        2. Draft clustering: Apply KMeans within each group
        3. Blossom matching: Match within clusters
        4. Handle remaining: Match leftover students
        5. Save to DB: Assign room IDs and satisfaction scores

        Args:
            dry_run: If True, don't save results to database

        Returns:
            Dictionary with matching results and statistics

        Raises:
            InsufficientStudentsException: If there are too few students
            NoUnmatchedStudentsException: If all students are already matched
        """
        # Step 1: Get all unmatched students
        unmatched_students = await self.repository.get_unmatched_students()

        if len(unmatched_students) < 2:
            raise InsufficientStudentsException(
                f"Need at least 2 unmatched students, found {len(unmatched_students)}"
            )

        # Step 2: Hard filter by gender and smoking status
        male_non_smoker = [
            s for s in unmatched_students
            if s.gender == "male" and not s.is_smoker
        ]
        male_smoker = [
            s for s in unmatched_students
            if s.gender == "male" and s.is_smoker
        ]
        female_non_smoker = [
            s for s in unmatched_students
            if s.gender == "female" and not s.is_smoker
        ]
        female_smoker = [
            s for s in unmatched_students
            if s.gender == "female" and s.is_smoker
        ]

        # Step 3-4: Execute matching algorithm (clustering + Blossom + remaining)
        matched_pairs = match_students_by_groups(
            male_non_smoker=male_non_smoker,
            male_smoker=male_smoker,
            female_non_smoker=female_non_smoker,
            female_smoker=female_smoker
        )

        if not matched_pairs:
            raise NoUnmatchedStudentsException("No valid matches could be found")

        # Step 5: Assign room IDs sequentially
        assignments = []
        room_counter = await self._get_next_room_id()

        all_satisfactions = []
        for student_a, student_b, sat_a, sat_b in matched_pairs:
            assignments.append((student_a, student_b, room_counter, sat_a, sat_b))
            all_satisfactions.extend([sat_a, sat_b])
            room_counter += 1

        # Step 6: Save to database (unless dry run)
        students_updated = 0
        if not dry_run:
            students_updated = await self.repository.assign_matches(assignments)

        # Calculate statistics
        statistics = MatchingStatistics(
            total_students=len(unmatched_students),
            matched_students=len(matched_pairs) * 2,
            unmatched_students=len(unmatched_students) - (len(matched_pairs) * 2),
            total_rooms=len(matched_pairs),
            average_satisfaction=sum(all_satisfactions) / len(all_satisfactions) if all_satisfactions else 0.0,
            min_satisfaction=min(all_satisfactions) if all_satisfactions else 0.0,
            max_satisfaction=max(all_satisfactions) if all_satisfactions else 0.0
        )

        return {
            "success": True,
            "message": f"Successfully matched {len(matched_pairs) * 2} students into {len(matched_pairs)} rooms",
            "statistics": statistics,
            "dry_run": dry_run,
            "students_updated": students_updated
        }

    async def _get_next_room_id(self) -> int:
        """Get the next available room ID.

        Returns:
            Next room ID (starting from 1 if no rooms exist)
        """
        all_students = await self.repository.get_all_students()
        matched = [s for s in all_students if s.matched_room_id is not None]

        if not matched:
            return 1

        max_room_id = max(s.matched_room_id for s in matched)
        return max_room_id + 1

    async def get_matching_status(self) -> dict:
        """Get current matching status.

        Returns:
            Dictionary with matching statistics
        """
        return await self.repository.get_matching_statistics()

    async def reset_matching(self) -> dict:
        """Reset all matching data.

        Returns:
            Dictionary with reset results
        """
        students_reset = await self.repository.reset_all_matches()

        return {
            "success": True,
            "message": "Successfully reset matching for all students",
            "students_reset": students_reset
        }

    async def get_matching_results(self, skip: int = 0, limit: int = 100) -> dict:
        """Get paginated matching results.

        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return

        Returns:
            Dictionary with paginated room assignments
        """
        total_rooms = await self.repository.count_matched_rooms()
        rooms = await self.repository.get_matched_students_by_room(skip=skip, limit=limit)

        return {
            "total": total_rooms,
            "skip": skip,
            "limit": limit,
            "rooms": rooms
        }

    async def get_detailed_statistics(self) -> dict:
        """Get detailed statistics about matching results.

        Returns:
            Dictionary with comprehensive statistics including:
            - Average, median, min, max, standard deviation of satisfaction scores
            - Room-level statistics
            - Distribution of satisfaction scores
        """
        return await self.repository.get_detailed_statistics()