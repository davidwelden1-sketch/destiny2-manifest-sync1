"""Bridge measurement summaries to calibrated model residuals, fail closed.

The model prediction must use exactly the same scenario and game version
as the measurement summary. A residual report is NOT a certified model.
"""
from math import isfinite
from simulator.calibration import calibration_report

def compare_predictions_to_summaries(pairs):
    if not isinstance(pairs, (list, tuple)) or not pairs:
        raise ValueError("nonempty prediction/summary pairs required")
    predicted, observed, contexts = [], [], []
    for pair in pairs:
        if not isinstance(pair, dict):
            raise ValueError("malformed pair")
        context = pair.get("context")
        summary = pair.get("measurement")
        if not isinstance(context, dict) or not isinstance(summary, dict):
            raise ValueError("context and measurement required")
        if context != summary.get("context"):
            raise ValueError("prediction and measurement contexts differ")
        if summary.get("count", 0) < 3 or summary.get("status") != "reported_measurements_not_independently_verified":
            raise ValueError("insufficient or unsupported measurement summary")
        prediction = pair.get("prediction")
        actual = summary.get("mean")
        if type(prediction) not in (int, float) or type(actual) not in (int, float) or not isfinite(prediction) or not isfinite(actual):
            raise ValueError("invalid prediction or observation")
        if not summary.get("source_urls"):
            raise ValueError("measurement provenance required")
        predicted.append(prediction)
        observed.append(actual)
        contexts.append(context)
    report = calibration_report(predicted, observed)
    report["contexts"] = contexts
    report["source_urls"] = sorted({url for pair in pairs for url in pair["measurement"]["source_urls"]})
    report["ready_for_certification"] = False
    return report
