"""Draft clustering module for reducing Blossom algorithm complexity.

This module groups students into clusters of ~100 students each to reduce
the O(n³) complexity of the Blossom algorithm.
"""
from typing import List
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

from app.models.student import Student


def calculate_global_average_weights(students: List[Student]) -> dict:
    """Calculate global average weights across all students.

    These averaged weights are used for clustering, while individual weights
    are used later for satisfaction scoring.

    Args:
        students: List of students to analyze

    Returns:
        Dictionary of average weights for each category
    """
    if not students:
        return {
            'lifestyle': 50.0,
            'cleaning': 50.0,
            'age': 50.0,
            'personality': 50.0,
        }

    total_lifestyle = sum(s.weight_lifestyle_rhythm for s in students)
    total_cleaning = sum(s.weight_cleaning for s in students)
    total_age = sum(s.weight_age for s in students)
    total_personality = sum(s.weight_personality for s in students)

    n = len(students)

    return {
        'lifestyle': total_lifestyle / n,
        'cleaning': total_cleaning / n,
        'age': total_age / n,
        'personality': total_personality / n,
    }


def prepare_clustering_features(students: List[Student], avg_weights: dict) -> pd.DataFrame:
    """Prepare weighted features for KMeans clustering.

    Features are normalized and weighted using global average weights.

    Args:
        students: List of students to cluster
        avg_weights: Average weights calculated from all students

    Returns:
        DataFrame with student IDs and weighted features
    """
    data = []

    for student in students:
        # Extract raw features
        weekday_sleep = int(student.weekday_sleep_time)
        weekday_wake = int(student.weekday_wake_time)
        cleaning = student.cleaning_frequency
        age = student.age
        late_night = student.late_night_return_frequency
        personality = student.personality_extroversion

        # Normalize features to 0-1 scale
        norm_sleep = weekday_sleep / 23
        norm_wake = weekday_wake / 23
        norm_cleaning = cleaning / 7
        norm_age = (age - 18) / (100 - 18)  # Assuming age range 18-100
        norm_late_night = late_night / 7
        norm_personality = (personality - 1) / (5 - 1)  # 1-5 scale

        # Apply average weights
        # Lifestyle includes sleep/wake times and late-night frequency
        weighted_sleep = norm_sleep * avg_weights['lifestyle'] / 100
        weighted_wake = norm_wake * avg_weights['lifestyle'] / 100
        weighted_late_night = norm_late_night * avg_weights['lifestyle'] / 100

        weighted_cleaning = norm_cleaning * avg_weights['cleaning'] / 100
        weighted_age = norm_age * avg_weights['age'] / 100
        weighted_personality = norm_personality * avg_weights['personality'] / 100

        data.append({
            'student_id': str(student.id),
            'sleep': weighted_sleep,
            'wake': weighted_wake,
            'late_night': weighted_late_night,
            'cleaning': weighted_cleaning,
            'age': weighted_age,
            'personality': weighted_personality,
        })

    return pd.DataFrame(data)


def apply_draft_clustering(students: List[Student], target_size: int = 100) -> None:
    """Apply KMeans clustering and assign cluster IDs to students.

    Modifies students in-place by setting their cluster_id attribute.

    Args:
        students: List of students to cluster (modified in-place)
        target_size: Target cluster size (default: 100)
    """
    if len(students) <= target_size:
        # Too few students, no clustering needed
        for student in students:
            student.cluster_id = 0
        return

    # Calculate number of clusters
    n_clusters = max(1, len(students) // target_size)

    # Calculate average weights
    avg_weights = calculate_global_average_weights(students)

    # Prepare features
    df = prepare_clustering_features(students, avg_weights)

    # Extract feature matrix (exclude student_id column)
    X = df.drop(columns=['student_id']).values

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X)

    # Assign cluster IDs to students
    for student, cluster_id in zip(students, cluster_labels):
        student.cluster_id = int(cluster_id)


def get_students_by_cluster(students: List[Student]) -> dict:
    """Group students by their cluster ID.

    Args:
        students: List of students with assigned cluster IDs

    Returns:
        Dictionary mapping cluster_id to list of students
    """
    clusters = {}
    for student in students:
        cluster_id = student.cluster_id if student.cluster_id is not None else 0
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        clusters[cluster_id].append(student)

    return clusters