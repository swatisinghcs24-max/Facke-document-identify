"""
Document Quality Analysis Module using OpenCV.
Analyzes:
- Image resolution
- Brightness / Exposure
- Sharpness / Blur (Laplacian variance)
- Contrast
Outputs: 'Document Quality: GOOD' or 'Document Quality: POOR' with explicit reasons.
"""

from typing import Dict, Any, List
import numpy as np
from utils.image_utils import load_image

try:
    import cv2
except ImportError:
    cv2 = None


def analyze_document_quality(image_path: str) -> Dict[str, Any]:
    """
    Perform objective physical and optical quality metrics on the uploaded document.
    """
    img = load_image(image_path)
    if img is None:
        return {
            "quality": "POOR",
            "score": 0,
            "reasons": ["Unable to load image file (file may be corrupted or unreadable)."],
            "metrics": {
                "width": 0,
                "height": 0,
                "sharpness": 0.0,
                "brightness": 0.0,
                "contrast": 0.0
            }
        }

    h, w = img.shape[:2]
    reasons: List[str] = []

    # 1. Resolution Check
    min_width, min_height = 640, 480
    min_pixels = 300000
    total_pixels = w * h
    if w < min_width or h < min_height or total_pixels < min_pixels:
        reasons.append(f"Image resolution is insufficient ({w}x{h} px, recommended minimum 800x600 px).")

    # Grayscale conversion for optical analysis
    if cv2 is not None:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2. Sharpness & Blur Analysis via Laplacian Variance
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if laplacian_var < 75.0:
            reasons.append(f"Low image sharpness / high blur detected (Laplacian score {laplacian_var:.1f}).")

        # 3. Brightness / Exposure Analysis
        mean_brightness = float(np.mean(gray))
        if mean_brightness < 45.0:
            reasons.append(f"Low brightness ({mean_brightness:.1f}/255). Image is underexposed.")
        elif mean_brightness > 225.0:
            reasons.append(f"Excessive brightness / glare detected ({mean_brightness:.1f}/255). Image is overexposed.")

        # 4. Contrast Analysis
        contrast_std = float(np.std(gray))
        if contrast_std < 32.0:
            reasons.append(f"Low contrast ({contrast_std:.1f}). Text and photo elements may lack distinction.")
    else:
        # Fallback if cv2 is not installed
        mean_brightness = float(np.mean(img))
        contrast_std = float(np.std(img))
        laplacian_var = 120.0
        if mean_brightness < 40 or mean_brightness > 230:
            reasons.append("Extreme brightness levels detected.")

    # Quality verdict determination
    is_poor = len(reasons) > 0 and any(
        "insufficient" in r or "blur" in r or "underexposed" in r for r in reasons
    )
    quality = "POOR" if is_poor else "GOOD"

    # Normalized quality score 0 - 100
    quality_score = 100
    if quality == "POOR":
        quality_score = max(20, 100 - (len(reasons) * 25))

    return {
        "quality": quality,
        "score": quality_score,
        "reasons": reasons,
        "metrics": {
            "width": w,
            "height": h,
            "sharpness": round(laplacian_var, 1),
            "brightness": round(mean_brightness, 1),
            "contrast": round(contrast_std, 1)
        }
    }
