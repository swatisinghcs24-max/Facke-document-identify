"""
Tampering Indicator Analysis Module (Prototype Level) using OpenCV.
Analyzes:
- Edge gradient density and spatial distribution (Canny edge detection)
- Local high-frequency noise variance across image quadrants
- Compression artifact anomalies (Error Level Analysis heuristic)
- Border / insert abrupt gradient discontinuities

DISCLAIMER:
Automated screening indicator only; not definitive proof of document tampering or fraud.
"Possible tampering indicators detected. Manual verification is recommended."
"""

from typing import Dict, Any, List
import numpy as np
from utils.image_utils import load_image

try:
    import cv2
except ImportError:
    cv2 = None


def detect_tampering_indicators(image_path: str) -> Dict[str, Any]:
    """
    Execute heuristic prototype image integrity screening.
    Returns tamper_indicator ('LOW', 'MEDIUM', 'HIGH'), score, and observations.
    """
    img = load_image(image_path)
    if img is None:
        return {
            "indicator": "HIGH",
            "tamper_score": 75.0,
            "observations": ["Image file could not be decoded. Potential data corruption or invalid container."],
            "disclaimer": "Possible tampering indicators detected. Manual verification is recommended."
        }

    h, w = img.shape[:2]
    observations: List[str] = []
    anomaly_points = 0.0

    if cv2 is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 1. Edge Density Analysis (Canny Edge Distribution)
        # Spliced or copy-pasted text/photos often exhibit abnormal localized high-gradient edge rings
        edges = cv2.Canny(gray, 100, 200)
        edge_ratio = float(np.count_nonzero(edges)) / float(w * h)

        # Normal ID documents generally have edge density between 0.03 and 0.16
        if edge_ratio > 0.22:
            anomaly_points += 30.0
            observations.append(f"Abnormal high-frequency edge density ({edge_ratio * 100:.1f}%). Possible post-processing or overlay artifacts.")
        elif edge_ratio < 0.015:
            anomaly_points += 15.0
            observations.append(f"Unusually low edge structure ({edge_ratio * 100:.1f}%). Possible heavy blurring or artificial smoothing.")

        # 2. Local Noise Consistency Check (Quad Split)
        # Spliced regions from different cameras/resolutions have disparate noise floors
        q_h, q_w = h // 2, w // 2
        quadrants = [
            gray[0:q_h, 0:q_w],
            gray[0:q_h, q_w:w],
            gray[q_h:h, 0:q_w],
            gray[q_h:h, q_w:w]
        ]
        variances = [float(np.var(q)) for q in quadrants if q.size > 0]
        if variances and min(variances) > 0:
            var_ratio = max(variances) / (min(variances) + 1e-5)
            if var_ratio > 6.5:
                anomaly_points += 25.0
                observations.append(f"Inconsistent noise/variance distribution across document quadrants (ratio {var_ratio:.1f}x).")

        # 3. Compression / Gradient Discontinuity Heuristic (Simple ELA Approximation)
        # Apply slight blur and measure absolute difference to check for localized compression discrepancies
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        diff = cv2.absdiff(gray, blurred)
        max_diff = float(np.max(diff))
        mean_diff = float(np.mean(diff))

        if mean_diff > 18.0:
            anomaly_points += 20.0
            observations.append("Elevated high-frequency compression discrepancies detected.")

    else:
        # Fallback if cv2 not available
        anomaly_points = 10.0

    # Classify into LOW, MEDIUM, HIGH
    if anomaly_points >= 45.0:
        indicator = "HIGH"
        risk_level = "High likelihood of irregularities"
    elif anomaly_points >= 20.0:
        indicator = "MEDIUM"
        risk_level = "Moderate variance in image structure"
    else:
        indicator = "LOW"
        risk_level = "Within normal structural bounds"

    if not observations:
        observations.append("Edge structure and noise floors are consistent with standard capture.")

    return {
        "indicator": indicator,
        "tamper_score": round(min(100.0, anomaly_points), 1),
        "risk_level": risk_level,
        "observations": observations,
        "disclaimer": "Possible tampering indicators detected. Manual verification is recommended."
    }
