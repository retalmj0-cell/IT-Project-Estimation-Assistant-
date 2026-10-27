import math

PERT_RULES = {
    "description": "PERT weighted average formula: (Optimistic + 4 * Most Likely + Pessimistic) / 6",
    "unit": "days or hours"
}

CONTINGENCY_RATES = {
    "low_risk": 0.10,
    "medium_risk": 0.15,
    "high_risk": 0.25
}

AGILE_SPRINT_RULES = {
    "standard_working_hours_per_day": 8,
    "max_recommended_focus_factor": 0.85
}


def _valid_number(value, low, high):
    return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and math.isfinite(value)
            and low < value <= high
    )


def calculate_pert(optimistic: float, most_likely: float, pessimistic: float) -> dict:
    if not _valid_number(optimistic, 0, 1000) or not _valid_number(most_likely, 0, 1000) or not _valid_number(
            pessimistic, 0, 1000):
        return {"error": "All PERT values must be positive numbers up to 1000."}
    if not (optimistic <= most_likely <= pessimistic):
        return {"error": "Values must satisfy: Optimistic <= Most Likely <= Pessimistic."}

    expected_duration = (optimistic + (4 * most_likely) + pessimistic) / 6
    standard_deviation = (pessimistic - optimistic) / 6

    return {
        "expected_duration": round(expected_duration, 2),
        "standard_deviation": round(standard_deviation, 2),
        "optimistic": optimistic,
        "most_likely": most_likely,
        "pessimistic": pessimistic,
        "note": "Calculated using PERT estimation technique."
    }


def calculate_budget(hours: float, hourly_rate: float, contingency_percent: float) -> dict:
    if not _valid_number(hours, 0, 100000):
        return {"error": "Hours must be between 0 and 100,000."}
    if not _valid_number(hourly_rate, 0, 10000):
        return {"error": "Hourly rate must be valid."}
    if not _valid_number(contingency_percent, -1, 100):
        return {"error": "Contingency percent must be between 0 and 100."}

    base_cost = hours * hourly_rate
    contingency_amount = base_cost * (contingency_percent / 100)
    total_budget = base_cost + contingency_amount

    return {
        "base_cost": round(base_cost, 2),
        "contingency_amount": round(contingency_amount, 2),
        "total_budget": round(total_budget, 2),
        "unit": "USD",
        "note": "Includes base labor cost and project contingency reserve."
    }


def calculate_sprint(team_size: int, days: int, focus_factor: float) -> dict:
    if not isinstance(team_size, int) or isinstance(team_size, bool) or not 1 <= team_size <= 50:
        return {"error": "Team size must be an integer between 1 and 50."}
    if not isinstance(days, int) or isinstance(days, bool) or not 1 <= days <= 30:
        return {"error": "Sprint days must be an integer between 1 and 30."}
    if not _valid_number(focus_factor, 0, 1):
        return {"error": "Focus factor must be between 0 and 1 (e.g., 0.8)."}

    total_available_hours = team_size * days * 8 * focus_factor

    return {
        "team_size": team_size,
        "sprint_days": days,
        "focus_factor": focus_factor,
        "total_available_capacity_hours": round(total_available_hours, 2),
        "note": "Sprint capacity calculated based on available team hours and focus factor."
    }