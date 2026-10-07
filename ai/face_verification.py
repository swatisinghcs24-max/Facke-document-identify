"""
Face Verification Module (Prototype Level) using OpenCV.
Detects faces in document image and optional selfie, extracts face regions,
and calculates similarity using histogram & structural correlation.

DISCLAIMER:
Prototype-level optical comparison for academic screening demonstrations.
Not intended as production-grade biometric identification.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np
from utils.image_utils import load_image

try:
    import cv2
except ImportError:
    cv2 = None

# Haar Cascade Frontal Face Classifier
_face_cascade = None


def get_face_cascade():
    """Load OpenCV pre-trained Haar Cascade for frontal face detection."""
    global _face_cascade
    if _face_cascade is None and cv2 is not None:
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            _face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception:
            _face_cascade = False
    return _face_cascade


def detect_largest_face(image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
    """
    Detect the most prominent frontal face in the image.
    Returns (x, y, w, h) bounding box or None.
    """
    if cv2 is None or image is None:
        return None

    cascade = get_face_cascade()
    if not cascade or cascade is False:
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Equalize histogram for illumination invariant face detection
    gray = cv2.equalizeHist(gray)

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    if len(faces) == 0:
        return None

    # Return the largest detected face box by area
    largest = max(faces, key=lambda f: f[2] * f[3])
    return int(largest[0]), int(largest[1]), int(largest[2]), int(largest[3])


def extract_face_roi(image: np.ndarray, box: Tuple[int, int, int, int], target_size: Tuple[int, int] = (160, 160)) -> Optional[np.ndarray]:
    """Extract and normalize the face region of interest."""
    if cv2 is None or image is None or box is None:
        return None

    x, y, w, h = box
    pad_h = int(h * 0.1)
    pad_w = int(w * 0.1)

    # Bound coordinates safely inside image dimensions
    y1 = max(0, y - pad_h)
    y2 = min(image.shape[0], y + h + pad_h)
    x1 = max(0, x - pad_w)
    x2 = min(image.shape[1], x + w + pad_w)

    face = image[y1:y2, x1:x2]
    if face.size == 0:
        return None

    resized = cv2.resize(face, target_size, interpolation=cv2.INTER_AREA)
    return resized


def compute_face_similarity(face1: np.ndarray, face2: np.ndarray) -> float:
    """
    Calculate optical similarity score (0.0 to 100.0) between two normalized face ROIs
    using a multi-feature fusion:
    1. Grayscale normalized cross-correlation
    2. HSV color histogram intersection & correlation
    3. Gradient magnitude correlation
    """
    if cv2 is None or face1 is None or face2 is None:
        return 0.0

    try:
        # Grayscale representations
        g1 = cv2.cvtColor(face1, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(face2, cv2.COLOR_BGR2GRAY)

        # 1. Normalized 2D Correlation
        norm1 = (g1.astype(np.float32) - np.mean(g1)) / (np.std(g1) + 1e-5)
        norm2 = (g2.astype(np.float32) - np.mean(g2)) / (np.std(g2) + 1e-5)
        ncc = float(np.mean(norm1 * norm2))
        ncc_score = max(0.0, min(1.0, (ncc + 1.0) / 2.0))

        # 2. HSV Color Histogram Correlation
        hsv1 = cv2.cvtColor(face1, cv2.COLOR_BGR2HSV)
        hsv2 = cv2.cvtColor(face2, cv2.COLOR_BGR2HSV)
        hist1 = cv2.calcHist([hsv1], [0, 1], None, [16, 16], [0, 180, 0, 256])
        hist2 = cv2.calcHist([hsv2], [0, 1], None, [16, 16], [0, 180, 0, 256])
        cv2.normalize(hist1, hist1, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        cv2.normalize(hist2, hist2, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        hist_corr = float(cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL))
        hist_score = max(0.0, min(1.0, (hist_corr + 1.0) / 2.0))

        # 3. Sobel Edge Gradient Correlation
        sobel1 = cv2.Sobel(g1, cv2.CV_32F, 1, 1, ksize=3)
        sobel2 = cv2.Sobel(g2, cv2.CV_32F, 1, 1, ksize=3)
        sobel_norm1 = (sobel1 - np.mean(sobel1)) / (np.std(sobel1) + 1e-5)
        sobel_norm2 = (sobel2 - np.mean(sobel2)) / (np.std(sobel2) + 1e-5)
        grad_corr = float(np.mean(sobel_norm1 * sobel_norm2))
        grad_score = max(0.0, min(1.0, (grad_corr + 1.0) / 2.0))

        # Fused weighted similarity
        fused = (ncc_score * 0.45) + (hist_score * 0.35) + (grad_score * 0.20)
        percentage = round(fused * 100.0, 1)
        return min(98.5, max(15.0, percentage))

    except Exception:
        return 50.0


def verify_faces(document_path: str, selfie_path: Optional[str]) -> Dict[str, Any]:
    """
    Perform face detection and verification on document and selfie.
    Handles missing selfie, undetected faces, and provides match status.
    """
    doc_img = load_image(document_path)
    doc_box = detect_largest_face(doc_img) if doc_img is not None else None
    doc_detected = doc_box is not None

    if not selfie_path:
        return {
            "document_face_detected": doc_detected,
            "selfie_face_detected": False,
            "selfie_provided": False,
            "similarity": None,
            "status": "NOT COMPLETED",
            "message": "Selfie was not provided for biometric comparison.",
            "disclaimer": "Prototype Face Verification (Not production biometric identification)"
        }

    selfie_img = load_image(selfie_path)
    selfie_box = detect_largest_face(selfie_img) if selfie_img is not None else None
    selfie_detected = selfie_box is not None

    if not doc_detected or not selfie_detected:
        reasons = []
        if not doc_detected:
            reasons.append("Face not detected on document image")
        if not selfie_detected:
            reasons.append("Face not detected on uploaded selfie")

        return {
            "document_face_detected": doc_detected,
            "selfie_face_detected": selfie_detected,
            "selfie_provided": True,
            "similarity": None,
            "status": "NOT COMPLETED",
            "message": f"Face verification could not be completed: {', '.join(reasons)}.",
            "disclaimer": "Prototype Face Verification (Not production biometric identification)"
        }

    # Extract ROIs and compute similarity
    face_doc = extract_face_roi(doc_img, doc_box)
    face_selfie = extract_face_roi(selfie_img, selfie_box)
    similarity = compute_face_similarity(face_doc, face_selfie)

    # Classify match status
    if similarity >= 75.0:
        status = "MATCH"
    elif similarity >= 50.0:
        status = "REVIEW"
    else:
        status = "NO MATCH"

    return {
        "document_face_detected": True,
        "selfie_face_detected": True,
        "selfie_provided": True,
        "similarity": similarity,
        "status": status,
        "message": f"Similarity computed at {similarity:.1f}%. Result: {status}.",
        "disclaimer": "Prototype Face Verification (Not production biometric identification)"
    }
