"""Satisfaction scoring module for dormitory roommate matching.

This module implements asymmetric satisfaction scoring where each student
evaluates their potential roommate based on their own weights and preferences.
"""
from app.models.student import Student


def calculate_noise_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate noise-related dissatisfaction from evaluator's perspective (asymmetric).

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    dissatisfaction = 0.0

    # Sensitivity difference (symmetric component)
    sensitivity_diff = abs(evaluator.noise_sensitivity - partner.noise_sensitivity) / 4 * 100
    dissatisfaction += sensitivity_diff * 0.2

    # Partner's snoring → evaluator's sensitivity (asymmetric!)
    if partner.snores:
        snore_impact = evaluator.noise_sensitivity / 5 * 100 * 0.4
        dissatisfaction += snore_impact

    # Partner's call frequency → evaluator's sensitivity (asymmetric!)
    call_impact = (partner.call_frequency / 7) * (evaluator.noise_sensitivity / 5) * 100
    dissatisfaction += call_impact * 0.4

    return min(100.0, dissatisfaction)


def calculate_lifestyle_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate lifestyle rhythm dissatisfaction (symmetric).

    Sleep/wake times and drinking/late-night habits affect both students equally.

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    total_diff = 0.0

    # Sleep/wake time differences (hours: 0-23)
    total_diff += abs(int(evaluator.weekday_sleep_time) - int(partner.weekday_sleep_time))
    total_diff += abs(int(evaluator.weekday_wake_time) - int(partner.weekday_wake_time))
    total_diff += abs(int(evaluator.weekend_sleep_time) - int(partner.weekend_sleep_time))
    total_diff += abs(int(evaluator.weekend_wake_time) - int(partner.weekend_wake_time))

    # Late-night/drinking frequency differences (days per week: 0-7)
    total_diff += abs(evaluator.late_night_return_frequency - partner.late_night_return_frequency)
    total_diff += abs(evaluator.drinking_frequency - partner.drinking_frequency)

    # Normalize (max possible diff: 4*23 + 2*7 = 106)
    dissatisfaction = min(100.0, total_diff / 106 * 100)
    return dissatisfaction


def calculate_cleaning_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate cleaning frequency dissatisfaction (symmetric).

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    diff = abs(evaluator.cleaning_frequency - partner.cleaning_frequency)
    return diff / 7 * 100


def calculate_age_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate age difference dissatisfaction (symmetric).

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    diff = abs(evaluator.age - partner.age)
    return min(100.0, diff / 10 * 100)


def calculate_personality_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate personality extroversion dissatisfaction (symmetric).

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    diff = abs(evaluator.personality_extroversion - partner.personality_extroversion)
    return diff / 4 * 100


def calculate_major_dissatisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate major match dissatisfaction based on evaluator's preference (individual preference).

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Dissatisfaction score (0-100, lower is better)
    """
    same_major = (evaluator.major_name == partner.major_name)

    if evaluator.prefers_same_major and same_major:
        return 0.0  # Bonus: got what they wanted
    elif evaluator.prefers_same_major and not same_major:
        return 100.0  # Penalty: wanted same major but didn't get it
    else:
        return 50.0  # Neutral: doesn't care about major matching


def calculate_weekend_bonus(evaluator: Student, partner: Student) -> float:
    """Calculate weekend home bonus (symmetric).

    If one goes home and one stays, both benefit from extra personal space.

    Args:
        evaluator: Student evaluating the match
        partner: Potential roommate being evaluated

    Returns:
        Bonus score (0-100, higher is better)
    """
    if evaluator.goes_home_on_weekend != partner.goes_home_on_weekend:
        return 100.0  # Best: extra personal space on weekends
    else:
        return 50.0  # Neutral: same preference


def calculate_individual_satisfaction(evaluator: Student, partner: Student) -> float:
    """Calculate individual satisfaction score from evaluator's perspective.

    This is the main function that combines all dissatisfaction scores using
    the evaluator's personal weights.

    Args:
        evaluator: Student evaluating the match (uses their weights)
        partner: Potential roommate being evaluated

    Returns:
        Satisfaction score (0-100, higher is better)
    """
    # Calculate all dissatisfaction scores
    noise_dissatisfaction = calculate_noise_dissatisfaction(evaluator, partner)
    lifestyle_dissatisfaction = calculate_lifestyle_dissatisfaction(evaluator, partner)
    cleaning_dissatisfaction = calculate_cleaning_dissatisfaction(evaluator, partner)
    age_dissatisfaction = calculate_age_dissatisfaction(evaluator, partner)
    personality_dissatisfaction = calculate_personality_dissatisfaction(evaluator, partner)
    major_dissatisfaction = calculate_major_dissatisfaction(evaluator, partner)
    weekend_bonus = calculate_weekend_bonus(evaluator, partner)

    # Use evaluator's weights (not averaged!)
    total_weight = (
        evaluator.weight_noise +
        evaluator.weight_lifestyle_rhythm +
        evaluator.weight_cleaning +
        evaluator.weight_age +
        evaluator.weight_personality +
        evaluator.weight_major +
        20  # Fixed weight for weekend bonus
    )

    # Convert dissatisfaction to satisfaction (100 - dissatisfaction)
    # Apply weights and calculate weighted average
    satisfaction = (
        (100 - noise_dissatisfaction) * evaluator.weight_noise +
        (100 - lifestyle_dissatisfaction) * evaluator.weight_lifestyle_rhythm +
        (100 - cleaning_dissatisfaction) * evaluator.weight_cleaning +
        (100 - age_dissatisfaction) * evaluator.weight_age +
        (100 - personality_dissatisfaction) * evaluator.weight_personality +
        (100 - major_dissatisfaction) * evaluator.weight_major +
        weekend_bonus * 20
    ) / total_weight

    return satisfaction


def calculate_blossom_score(student_a: Student, student_b: Student) -> float:
    """Calculate combined score for Blossom algorithm (average of both satisfactions).

    This function calculates both students' individual satisfaction scores and
    returns their average, which is used by the Blossom matching algorithm.

    Args:
        student_a: First student
        student_b: Second student

    Returns:
        Average satisfaction score (0-100, higher is better)
    """
    satisfaction_a = calculate_individual_satisfaction(student_a, student_b)
    satisfaction_b = calculate_individual_satisfaction(student_b, student_a)

    return (satisfaction_a + satisfaction_b) / 2