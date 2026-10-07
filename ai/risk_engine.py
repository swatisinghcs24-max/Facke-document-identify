"""
Risk Engine Module.
Synthesizes document verification signals into a normalized risk score (0-100).
Combines:
- Missing information penalties
- Expired document status penalties
- Document quality issues (resolution, blur, lighting)
- Tampering indicator level (LOW, MEDIUM, HIGH)
- Face similarity and biometric mismatch penalties

Thresholds:
- 0 to 29:   VERIFIED
- 30 to 64:  NEEDS REVIEW
- 65 to 100: SUSPICIOUS
"""

from typing import Dict, Any, List, Tuple
from backend.config import RISK_VERIFIED_THRESHOLD, RISK_REVIEW_THRESHOLD


def calculate_risk_score(
    ocr_result: Dict[str, Any],
    quality_result: Dict[str, Any],
    tamper_result: Dict[str, Any],
    face_result: Dict[str, Any]
) -> Tuple[int, str, List[str], str]:
    """
    Calculate consolidated risk score (0-100), classification status,
    explainable reasons list, and recommendation string.
    """
    risk_points = 0.0
    reasons: List[str] = []

    # 1. Missing Required Fields Analysis
    missing_fields = ocr_result.get("missing_fields", [])
    if missing_fields:
        penalty_per_field = {
            "name": 15,
            "dob": 12,
            "doc_number": 15,
            "expiry_date": 10,
            "nationality": 8
        }
        for field in missing_fields:
            pts = penalty_per_field.get(field, 10)
            risk_points += pts
            reasons.append(f"Required field '{field.replace('_', ' ').title()}' was not detected (+{pts} risk).")
    else:
        reasons.append("All key identity fields successfully extracted via OCR.")

    # 2. Expiry Status Analysis
    expiry_check = ocr_result.get("expiry_check", {})
    if expiry_check.get("is_expired", False):
        risk_points += 35.0
        reasons.append(f"Document validity check failed: {expiry_check.get('message', 'Document has expired')} (+35 risk).")
    elif expiry_check.get("is_missing", False):
        risk_points += 10.0
        reasons.append("Document expiry date is unverified or missing (+10 risk).")
    else:
        reasons.append("Document is valid and unexpired.")

    # 3. Document Quality Analysis
    doc_quality = quality_result.get("quality", "GOOD")
    quality_reasons = quality_result.get("reasons", [])
    if doc_quality == "POOR":
        risk_points += 20.0
        reasons.append(f"Document optical quality flagged as POOR: {', '.join(quality_reasons)} (+20 risk).")
    else:
        reasons.append("Document resolution, brightness, and sharpness meet screening standards.")

    # 4. Tampering Indicator Analysis
    tamper_indicator = tamper_result.get("indicator", "LOW")
    if tamper_indicator == "HIGH":
        risk_points += 40.0
        reasons.append("Elevated structural/edge tampering indicators detected (+40 risk).")
    elif tamper_indicator == "MEDIUM":
        risk_points += 20.0
        reasons.append("Moderate structural anomalies or noise inconsistencies observed (+20 risk).")
    else:
        reasons.append("Image edge density and noise metrics are within nominal ranges.")

    # 5. Face Verification Analysis
    if face_result.get("selfie_provided", False):
        if face_result.get("status") == "NO MATCH":
            similarity = face_result.get("similarity", 0.0) or 0.0
            risk_points += 40.0
            reasons.append(f"Biometric face mismatch: similarity is only {similarity:.1f}% (+40 risk).")
        elif face_result.get("status") == "REVIEW":
            similarity = face_result.get("similarity", 0.0) or 0.0
            risk_points += 18.0
            reasons.append(f"Biometric face similarity is moderate ({similarity:.1f}%) (+18 risk).")
        elif face_result.get("status") == "MATCH":
            reasons.append(f"Biometric facial match confirmed ({face_result.get('similarity', 0.0):.1f}% similarity).")
        else:
            risk_points += 15.0
            reasons.append("Face verification could not be completed on the uploaded images (+15 risk).")
    else:
        # Selfie was optional; slight informational note, no major penalty
        reasons.append("No selfie provided; applicant biometric matching skipped.")

    # Clamp risk score to bounds 0 - 100
    final_score = int(round(max(0.0, min(100.0, risk_points))))

    # Classification
    if final_score < RISK_VERIFIED_THRESHOLD:
        status = "VERIFIED"
        recommendation = "Document passed initial automated screening. Nominal risk parameters observed."
    elif final_score < RISK_REVIEW_THRESHOLD:
        status = "NEEDS REVIEW"
        recommendation = "Manual verification is recommended. Moderate risk indicators or missing fields detected."
    else:
        status = "SUSPICIOUS"
        recommendation = "High risk indicators detected. Mandatory physical or certified human verification required."

    return final_score, status, reasons, recommendation
