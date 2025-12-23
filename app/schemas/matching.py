"""Matching request/response schemas."""
from typing import List, Optional
from pydantic import BaseModel, Field


class MatchingExecuteRequest(BaseModel):
    """Request schema for executing matching algorithm."""

    dry_run: bool = Field(False, description="If true, don't save results to database")

    model_config = {
        "json_schema_extra": {
            "example": {
                "dry_run": False
            }
        }
    }


class MatchingStatistics(BaseModel):
    """Matching statistics."""

    total_students: int = Field(..., description="Total number of students")
    matched_students: int = Field(..., description="Number of successfully matched students")
    unmatched_students: int = Field(..., description="Number of unmatched students")
    total_rooms: int = Field(..., description="Total number of rooms assigned")
    average_satisfaction: float = Field(..., description="Average satisfaction score across all matches")
    min_satisfaction: float = Field(..., description="Minimum satisfaction score")
    max_satisfaction: float = Field(..., description="Maximum satisfaction score")


class MatchingExecuteResponse(BaseModel):
    """Response schema for matching execution."""

    success: bool = Field(..., description="Whether matching was successful")
    message: str = Field(..., description="Status message")
    statistics: Optional[MatchingStatistics] = Field(None, description="Matching statistics")
    dry_run: bool = Field(..., description="Whether this was a dry run")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Successfully matched 720 students into 360 rooms",
                "statistics": {
                    "total_students": 720,
                    "matched_students": 720,
                    "unmatched_students": 0,
                    "total_rooms": 360,
                    "average_satisfaction": 78.5,
                    "min_satisfaction": 45.2,
                    "max_satisfaction": 98.7
                },
                "dry_run": False
            }
        }
    }


class MatchingStatusResponse(BaseModel):
    """Response schema for matching status."""

    total_students: int = Field(..., description="Total number of students")
    matched_students: int = Field(..., description="Number of matched students")
    unmatched_students: int = Field(..., description="Number of unmatched students")
    matching_rate: float = Field(..., description="Percentage of students matched")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_students": 720,
                "matched_students": 720,
                "unmatched_students": 0,
                "matching_rate": 100.0
            }
        }
    }


class RoomAssignment(BaseModel):
    """Room assignment information."""

    room_id: int = Field(..., description="Room number")
    student_a_id: str = Field(..., description="First student's student ID")
    student_a_name: str = Field(..., description="First student's name")
    student_a_satisfaction: float = Field(..., description="First student's satisfaction score")
    student_b_id: str = Field(..., description="Second student's student ID")
    student_b_name: str = Field(..., description="Second student's name")
    student_b_satisfaction: float = Field(..., description="Second student's satisfaction score")
    average_satisfaction: float = Field(..., description="Average satisfaction score")

    model_config = {
        "json_schema_extra": {
            "example": {
                "room_id": 1,
                "student_a_id": "20210001",
                "student_a_name": "김철수",
                "student_a_satisfaction": 85.3,
                "student_b_id": "20210002",
                "student_b_name": "이영희",
                "student_b_satisfaction": 82.7,
                "average_satisfaction": 84.0
            }
        }
    }


class MatchingResultsResponse(BaseModel):
    """Paginated matching results."""

    total: int = Field(..., description="Total number of rooms")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Number of items per page")
    rooms: List[RoomAssignment] = Field(..., description="List of room assignments")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 360,
                "skip": 0,
                "limit": 100,
                "rooms": [
                    {
                        "room_id": 1,
                        "student_a_id": "20210001",
                        "student_a_name": "김철수",
                        "student_a_satisfaction": 85.3,
                        "student_b_id": "20210002",
                        "student_b_name": "이영희",
                        "student_b_satisfaction": 82.7,
                        "average_satisfaction": 84.0
                    }
                ]
            }
        }
    }


class ResetMatchingResponse(BaseModel):
    """Response schema for matching reset."""

    success: bool = Field(..., description="Whether reset was successful")
    message: str = Field(..., description="Status message")
    students_reset: int = Field(..., description="Number of students reset")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Successfully reset matching for all students",
                "students_reset": 720
            }
        }
    }


class MatchingStatisticsDetailResponse(BaseModel):
    """Detailed statistics for current matching results."""

    total_rooms: int = Field(..., description="Total number of matched rooms")
    total_students: int = Field(..., description="Total number of matched students")

    # Individual satisfaction statistics
    average_satisfaction: float = Field(..., description="Average satisfaction score across all students")
    median_satisfaction: float = Field(..., description="Median satisfaction score")
    min_satisfaction: float = Field(..., description="Minimum satisfaction score")
    max_satisfaction: float = Field(..., description="Maximum satisfaction score")
    std_satisfaction: float = Field(..., description="Standard deviation of satisfaction scores")

    # Room average satisfaction statistics
    average_room_satisfaction: float = Field(..., description="Average of room average satisfactions")
    median_room_satisfaction: float = Field(..., description="Median of room average satisfactions")
    min_room_satisfaction: float = Field(..., description="Minimum room average satisfaction")
    max_room_satisfaction: float = Field(..., description="Maximum room average satisfaction")
    std_room_satisfaction: float = Field(..., description="Standard deviation of room average satisfactions")

    # Distribution
    satisfaction_distribution: dict = Field(..., description="Distribution of satisfaction scores by range")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_rooms": 360,
                "total_students": 720,
                "average_satisfaction": 78.5,
                "median_satisfaction": 79.2,
                "min_satisfaction": 45.3,
                "max_satisfaction": 98.7,
                "std_satisfaction": 12.4,
                "average_room_satisfaction": 78.5,
                "median_room_satisfaction": 79.0,
                "min_room_satisfaction": 50.2,
                "max_room_satisfaction": 96.5,
                "std_room_satisfaction": 10.8,
                "satisfaction_distribution": {
                    "0-20": 0,
                    "20-40": 5,
                    "40-60": 45,
                    "60-80": 320,
                    "80-100": 350
                }
            }
        }
    }