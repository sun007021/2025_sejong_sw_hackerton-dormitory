import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, UUID, CheckConstraint, Index
)
from sqlalchemy.sql import func
from app.models.base import Base


class Student(Base):
    """Student model for dormitory matching system."""

    __tablename__ = "students"

    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Basic Information
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)

    # Hard Filters (Must Match)
    gender = Column(String(10), nullable=False, index=True)
    is_smoker = Column(Boolean, nullable=False, default=False, index=True)

    # Lifestyle Rhythm (00-23 hour format)
    weekday_sleep_time = Column(String(2), nullable=False)
    weekday_wake_time = Column(String(2), nullable=False)
    weekend_sleep_time = Column(String(2), nullable=False)
    weekend_wake_time = Column(String(2), nullable=False)
    goes_home_on_weekend = Column(Boolean, nullable=False, default=False)
    late_night_return_frequency = Column(Integer, nullable=False, default=0)
    drinking_frequency = Column(Integer, nullable=False, default=0)

    # Noise
    noise_sensitivity = Column(Integer, nullable=False)
    call_frequency = Column(Integer, nullable=False, default=0)
    snores = Column(Boolean, nullable=False, default=False)

    # Major
    prefers_same_major = Column(Boolean, nullable=False, default=False)
    major_name = Column(String(100), nullable=False, index=True)

    # Other Preferences
    cleaning_frequency = Column(Integer, nullable=False, default=0)
    personality_extroversion = Column(Integer, nullable=False)

    # Weights (0-100 scale for matching algorithm)
    weight_lifestyle_rhythm = Column(Integer, default=50)
    weight_noise = Column(Integer, default=50)
    weight_major = Column(Integer, default=50)
    weight_cleaning = Column(Integer, default=50)
    weight_age = Column(Integer, default=50)
    weight_personality = Column(Integer, default=50)

    # Matching Status (for future use)
    is_matched = Column(Boolean, default=False, index=True)
    matched_room_id = Column(UUID(as_uuid=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint('age >= 18 AND age <= 100', name='check_age_range'),
        CheckConstraint("gender IN ('male', 'female', 'other')", name='check_gender'),
        CheckConstraint('late_night_return_frequency >= 0 AND late_night_return_frequency <= 7', name='check_late_night_range'),
        CheckConstraint('drinking_frequency >= 0 AND drinking_frequency <= 7', name='check_drinking_range'),
        CheckConstraint('noise_sensitivity >= 1 AND noise_sensitivity <= 5', name='check_noise_sensitivity_range'),
        CheckConstraint('call_frequency >= 0 AND call_frequency <= 7', name='check_call_frequency_range'),
        CheckConstraint('cleaning_frequency >= 0 AND cleaning_frequency <= 7', name='check_cleaning_range'),
        CheckConstraint('personality_extroversion >= 1 AND personality_extroversion <= 5', name='check_personality_range'),
        CheckConstraint('weight_lifestyle_rhythm >= 0 AND weight_lifestyle_rhythm <= 100', name='check_weight_lifestyle'),
        CheckConstraint('weight_noise >= 0 AND weight_noise <= 100', name='check_weight_noise'),
        CheckConstraint('weight_major >= 0 AND weight_major <= 100', name='check_weight_major'),
        CheckConstraint('weight_cleaning >= 0 AND weight_cleaning <= 100', name='check_weight_cleaning'),
        CheckConstraint('weight_age >= 0 AND weight_age <= 100', name='check_weight_age'),
        CheckConstraint('weight_personality >= 0 AND weight_personality <= 100', name='check_weight_personality'),
    )

    def __repr__(self) -> str:
        return f"<Student(student_id='{self.student_id}', name='{self.name}', major='{self.major_name}')>"