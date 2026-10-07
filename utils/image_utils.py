"""
Image processing utilities for safe file loading, resizing, and color conversions.
"""

import os
from typing import Optional, Tuple
import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None


def load_image(filepath: str) -> Optional[np.ndarray]:
    """
    Safely load an image from disk using OpenCV.
    Handles Unicode file paths and returns None if corrupt.
    """
    if not os.path.exists(filepath):
        return None

    if cv2 is not None:
        try:
            # Using imdecode handles non-ASCII paths and avoids silent failures
            with open(filepath, "rb") as f:
                bytes_data = f.read()
            arr = np.frombuffer(bytes_data, dtype=np.uint8)
            img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            return img
        except Exception:
            return None

    return None


def resize_if_needed(image: np.ndarray, max_dim: int = 1600) -> np.ndarray:
    """
    Resize an image if either dimension exceeds max_dim, preserving aspect ratio.
    """
    if cv2 is None or image is None:
        return image

    h, w = image.shape[:2]
    if max(h, w) <= max_dim:
        return image

    scaling = max_dim / float(max(h, w))
    new_w = int(w * scaling)
    new_h = int(h * scaling)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def get_image_dimensions(image: np.ndarray) -> Tuple[int, int]:
    """Return (width, height) of an image array."""
    if image is None:
        return 0, 0
    h, w = image.shape[:2]
    return w, h
