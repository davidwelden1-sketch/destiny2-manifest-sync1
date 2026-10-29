"""Configurable linear falloff approximation, not a verified Destiny curve."""
def linear_falloff(distance, start, end, min_multiplier):
    if start < 0 or end <= start or distance < 0 or not 0 < min_multiplier <= 1:
        raise ValueError("Invalid falloff inputs")
    if distance <= start:
        return 1.0
    if distance >= end:
        return min_multiplier
    return 1.0 - (1.0-min_multiplier)*(distance-start)/(end-start)
