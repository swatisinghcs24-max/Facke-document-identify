"""
File validation utilities for identity document uploads.
Enforces extension whitelisting, size restrictions, and secure naming conventions.
"""

import os
import uuid
import werkzeug.utils
from typing import Tuple
from backend.config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH


def allowed_file(filename: str) -> bool:
    """Check if the filename has an allowed image extension."""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def validate_file_upload(file_obj) -> Tuple[bool, str]:
    """
    Validate that an uploaded file exists, has a permitted filename,
    and complies with maximum size constraints.
    """
    if file_obj is None:
        return False, "No file provided in the request."

    if file_obj.filename == "":
        return False, "Empty filename. Please select a valid document image."

    if not allowed_file(file_obj.filename):
        return False, f"Unsupported file format. Permitted formats: {', '.join(sorted(ALLOWED_EXTENSIONS)).upper()}."

    # Seek to end to measure size if possible, then reset
    try:
        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        file_obj.seek(0)
        if size > MAX_CONTENT_LENGTH:
            max_mb = MAX_CONTENT_LENGTH / (1024 * 1024)
            return False, f"File exceeds maximum permissible size of {max_mb:.0f} MB."
    except Exception:
        pass

    return True, "Valid file."


def generate_unique_filename(prefix: str, original_filename: str) -> str:
    """
    Generate a sanitized, collision-free filename with uuid tag.
    """
    clean_name = werkzeug.utils.secure_filename(original_filename)
    ext = clean_name.rsplit(".", 1)[1].lower() if "." in clean_name else "jpg"
    unique_id = uuid.uuid4().hex[:10]
    return f"{prefix}_{unique_id}.{ext}"
