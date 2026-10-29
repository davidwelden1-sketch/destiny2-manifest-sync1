"""Calibration of model predictions against compatible reported observations.

Never marks a model as validated solely because numerical error is small.
"""
from math import isfinite, sqrt

def calibration_report(predictions, observations):
    if not isinstance(predictions, (list, tuple)) or not isinstance(observations, (list, tuple)):
        raise TypeError("predictions and observations must be sequences")
    if not predictions or len(predictions) != len(observations):
        raise ValueError("matched nonempty samples required")
    errors = []
    for prediction, observed in zip(predictions, observations):
        if type(prediction) not in (float, int) or type(observed) not in (float, int):
            raise ValueError("numeric values required")
        if not isfinite(prediction) or not isfinite(observed):
            raise ValueError("finite values required")
        errors.append(prediction - observed)
    n = len(errors)
    return {"count": n, "mean_error": sum(errors) / n,
            "mean_absolute_error": sum(abs(e) for e in errors) / n,
            "root_mean_squared_error": sqrt(sum(e * e for e in errors) / n),
            "validated_in_game": False, "status": "descriptive_calibration_only"}
