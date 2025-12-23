from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator


class StudentBase(BaseModel):
    """Base student schema with common attributes."""

    student_id: str = Field(..., min_length=1, max_length=20, description="University student ID")
    name: str = Field(..., min_length=1, max_length=100, description="Student name")
    age: int = Field(..., ge=18, le=100, description="Student age")

    # Hard Filters
    gender: str = Field(..., description="Gender (male, female, other)")
    is_smoker: bool = Field(..., description="Whether the student smokes")

    # Lifestyle Rhythm (00-23 hour format)
    weekday_sleep_time: str = Field(..., pattern="^(0[0-9]|1[0-9]|2[0-3])$", description="Weekday sleep hour (00-23)")
    weekday_wake_time: str = Field(..., pattern="^(0[0-9]|1[0-9]|2[0-3])$", description="Weekday wake hour (00-23)")
    weekend_sleep_time: str = Field(..., pattern="^(0[0-9]|1[0-9]|2[0-3])$", description="Weekend sleep hour (00-23)")
    weekend_wake_time: str = Field(..., pattern="^(0[0-9]|1[0-9]|2[0-3])$", description="Weekend wake hour (00-23)")
    goes_home_on_weekend: bool = Field(..., description="Whether student goes home on weekends")
    late_night_return_frequency: int = Field(..., ge=0, le=7, description="Late night returns per week")
    drinking_frequency: int = Field(..., ge=0, le=7, description="Drinking frequency per week")

    # Noise
    noise_sensitivity: int = Field(..., ge=1, le=5, description="Noise sensitivity (1-5)")
    call_frequency: int = Field(..., ge=0, le=7, description="Phone calls per day")
    snores: bool = Field(..., description="Whether student snores")

    # Major
    prefers_same_major: bool = Field(..., description="Prefers roommate with same major")
    major_name: str = Field(..., min_length=1, max_length=100, description="Major name")

    # Other Preferences
    cleaning_frequency: int = Field(..., ge=0, le=7, description="Cleaning frequency per week")
    personality_extroversion: int = Field(..., ge=1, le=5, description="Extroversion level (1=introverted, 5=extroverted)")

    # Weights
    weight_lifestyle_rhythm: int = Field(50, ge=0, le=100, description="Weight for lifestyle rhythm matching")
    weight_noise: int = Field(50, ge=0, le=100, description="Weight for noise matching")
    weight_major: int = Field(50, ge=0, le=100, description="Weight for major matching")
    weight_cleaning: int = Field(50, ge=0, le=100, description="Weight for cleaning matching")
    weight_age: int = Field(50, ge=0, le=100, description="Weight for age matching")
    weight_personality: int = Field(50, ge=0, le=100, description="Weight for personality matching")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        if v not in ["male", "female", "other"]:
            raise ValueError("Gender must be one of: male, female, other")
        return v

    model_config = {"from_attributes": True}


class StudentCreate(StudentBase):
    """Schema for creating a new student."""

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "student_id": "20210001",
                "name": "김철수",
                "age": 21,
                "gender": "male",
                "is_smoker": False,
                "weekday_sleep_time": "23",
                "weekday_wake_time": "07",
                "weekend_sleep_time": "01",
                "weekend_wake_time": "10",
                "goes_home_on_weekend": False,
                "late_night_return_frequency": 2,
                "drinking_frequency": 1,
                "noise_sensitivity": 3,
                "call_frequency": 5,
                "snores": False,
                "prefers_same_major": True,
                "major_name": "컴퓨터공학과",
                "cleaning_frequency": 3,
                "personality_extroversion": 4,
                "weight_lifestyle_rhythm": 70,
                "weight_noise": 80,
                "weight_major": 60,
                "weight_cleaning": 40,
                "weight_age": 30,
                "weight_personality": 50,
            }
        },
    }


class StudentUpdate(BaseModel):
    """Schema for updating a student (all fields optional)."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=100)
    gender: Optional[str] = None
    is_smoker: Optional[bool] = None

    weekday_sleep_time: Optional[str] = Field(None, pattern="^(0[0-9]|1[0-9]|2[0-3])$")
    weekday_wake_time: Optional[str] = Field(None, pattern="^(0[0-9]|1[0-9]|2[0-3])$")
    weekend_sleep_time: Optional[str] = Field(None, pattern="^(0[0-9]|1[0-9]|2[0-3])$")
    weekend_wake_time: Optional[str] = Field(None, pattern="^(0[0-9]|1[0-9]|2[0-3])$")
    goes_home_on_weekend: Optional[bool] = None
    late_night_return_frequency: Optional[int] = Field(None, ge=0, le=7)
    drinking_frequency: Optional[int] = Field(None, ge=0, le=7)

    noise_sensitivity: Optional[int] = Field(None, ge=1, le=5)
    call_frequency: Optional[int] = Field(None, ge=0, le=7)
    snores: Optional[bool] = None

    prefers_same_major: Optional[bool] = None
    major_name: Optional[str] = Field(None, min_length=1, max_length=100)

    cleaning_frequency: Optional[int] = Field(None, ge=0, le=7)
    personality_extroversion: Optional[int] = Field(None, ge=1, le=5)

    weight_lifestyle_rhythm: Optional[int] = Field(None, ge=0, le=100)
    weight_noise: Optional[int] = Field(None, ge=0, le=100)
    weight_major: Optional[int] = Field(None, ge=0, le=100)
    weight_cleaning: Optional[int] = Field(None, ge=0, le=100)
    weight_age: Optional[int] = Field(None, ge=0, le=100)
    weight_personality: Optional[int] = Field(None, ge=0, le=100)

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["male", "female", "other"]:
            raise ValueError("Gender must be one of: male, female, other")
        return v

    model_config = {"from_attributes": True}


class StudentResponse(StudentBase):
    """Schema for student response (includes id and timestamps)."""

    id: UUID = Field(..., description="Student UUID")
    is_matched: bool = Field(..., description="Whether student has been matched")
    matched_room_id: Optional[int] = Field(None, description="Matched room ID if matched")
    my_satisfaction_score: Optional[float] = Field(None, description="My satisfaction score with roommate")
    partner_satisfaction_score: Optional[float] = Field(None, description="Roommate's satisfaction score with me")
    cluster_id: Optional[int] = Field(None, description="Cluster ID for matching algorithm")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "20210001",
                "name": "김철수",
                "age": 21,
                "gender": "male",
                "is_smoker": False,
                "weekday_sleep_time": "23",
                "weekday_wake_time": "07",
                "weekend_sleep_time": "01",
                "weekend_wake_time": "10",
                "goes_home_on_weekend": False,
                "late_night_return_frequency": 2,
                "drinking_frequency": 1,
                "noise_sensitivity": 3,
                "call_frequency": 5,
                "snores": False,
                "prefers_same_major": True,
                "major_name": "컴퓨터공학과",
                "cleaning_frequency": 3,
                "personality_extroversion": 4,
                "weight_lifestyle_rhythm": 70,
                "weight_noise": 80,
                "weight_major": 60,
                "weight_cleaning": 40,
                "weight_age": 30,
                "weight_personality": 50,
                "is_matched": False,
                "matched_room_id": None,
                "my_satisfaction_score": None,
                "partner_satisfaction_score": None,
                "cluster_id": None,
                "created_at": "2025-12-23T14:30:00Z",
                "updated_at": "2025-12-23T14:30:00Z",
            }
        },
    }