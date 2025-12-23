"""Blossom maximum weighted matching module.

This module uses NetworkX's max_weight_matching algorithm to find optimal
roommate pairings based on satisfaction scores.
"""
from typing import List, Tuple
import networkx as nx

from app.models.student import Student
from app.ml.scoring import calculate_individual_satisfaction, calculate_blossom_score


def blossom_match_cluster(students: List[Student]) -> Tuple[List[Tuple[Student, Student, float, float]], List[Student]]:
    """Match students within a cluster using Blossom algorithm.

    Args:
        students: List of students to match (should be from same cluster)

    Returns:
        Tuple of:
        - List of (student_a, student_b, satisfaction_a, satisfaction_b) tuples
        - List of unmatched students (empty if even number, one student if odd)
    """
    if len(students) < 2:
        return [], students

    # Create weighted graph
    G = nx.Graph()

    # Add all students as nodes
    for student in students:
        G.add_node(student.id)

    # Add edges with Blossom scores (average of both satisfactions)
    for i, student_a in enumerate(students):
        for student_b in students[i + 1:]:
            # Calculate individual satisfactions
            satisfaction_a = calculate_individual_satisfaction(student_a, student_b)
            satisfaction_b = calculate_individual_satisfaction(student_b, student_a)

            # Blossom score is the average
            blossom_score = (satisfaction_a + satisfaction_b) / 2

            # Add edge with weight (NetworkX maximizes weight)
            G.add_edge(student_a.id, student_b.id, weight=blossom_score,
                      sat_a=satisfaction_a, sat_b=satisfaction_b)

    # Run Blossom algorithm
    matching = nx.max_weight_matching(G, maxcardinality=True)

    # Build results
    matched_pairs = []
    matched_ids = set()

    for id_a, id_b in matching:
        # Find student objects
        student_a = next(s for s in students if s.id == id_a)
        student_b = next(s for s in students if s.id == id_b)

        # Get satisfaction scores from edge data
        edge_data = G[id_a][id_b]
        satisfaction_a = edge_data['sat_a']
        satisfaction_b = edge_data['sat_b']

        matched_pairs.append((student_a, student_b, satisfaction_a, satisfaction_b))
        matched_ids.add(id_a)
        matched_ids.add(id_b)

    # Find unmatched students
    unmatched = [s for s in students if s.id not in matched_ids]

    return matched_pairs, unmatched


def handle_remaining_students(students: List[Student]) -> Tuple[List[Tuple[Student, Student, float, float]], List[Student]]:
    """Match remaining unmatched students.

    This function is called after all clusters have been matched, to pair up
    any students that were left over (odd numbers in clusters).

    Args:
        students: List of unmatched students

    Returns:
        Tuple of:
        - List of (student_a, student_b, satisfaction_a, satisfaction_b) tuples
        - List of still unmatched students (0 or 1 student)
    """
    if len(students) < 2:
        return [], students

    # Use the same Blossom algorithm
    return blossom_match_cluster(students)


def match_students_by_groups(
    male_non_smoker: List[Student],
    male_smoker: List[Student],
    female_non_smoker: List[Student],
    female_smoker: List[Student],
) -> List[Tuple[Student, Student, float, float]]:
    """Match all students across all groups using clustering and Blossom algorithm.

    This is a helper function that orchestrates the entire matching pipeline:
    1. Apply clustering within each group
    2. Match within each cluster using Blossom
    3. Handle remaining unmatched students

    Args:
        male_non_smoker: Male non-smoking students
        male_smoker: Male smoking students
        female_non_smoker: Female non-smoking students
        female_smoker: Female smoking students

    Returns:
        List of (student_a, student_b, satisfaction_a, satisfaction_b) tuples
    """
    from app.ml.clustering import apply_draft_clustering, get_students_by_cluster

    all_matched_pairs = []
    all_remaining = []

    # Process each group
    for group in [male_non_smoker, male_smoker, female_non_smoker, female_smoker]:
        if not group:
            continue

        # Apply clustering
        apply_draft_clustering(group, target_size=100)

        # Get clusters
        clusters = get_students_by_cluster(group)

        # Match within each cluster
        group_remaining = []
        for cluster_students in clusters.values():
            matched_pairs, unmatched = blossom_match_cluster(cluster_students)
            all_matched_pairs.extend(matched_pairs)
            group_remaining.extend(unmatched)

        # Collect remaining students from this group
        all_remaining.extend(group_remaining)

    # Match remaining students across groups (within same gender only)
    if all_remaining:
        # Separate by gender
        male_remaining = [s for s in all_remaining if s.gender == "male"]
        female_remaining = [s for s in all_remaining if s.gender == "female"]

        # Match males
        if len(male_remaining) >= 2:
            male_pairs, male_leftover = handle_remaining_students(male_remaining)
            all_matched_pairs.extend(male_pairs)
            all_remaining = male_leftover
        else:
            all_remaining = male_remaining

        # Match females
        if len(female_remaining) >= 2:
            female_pairs, female_leftover = handle_remaining_students(female_remaining)
            all_matched_pairs.extend(female_pairs)
            all_remaining.extend(female_leftover)
        else:
            all_remaining.extend(female_remaining)

    # Final remaining students (should be 0 or very few)
    if all_remaining:
        # Log or handle final unmatched students
        pass

    return all_matched_pairs