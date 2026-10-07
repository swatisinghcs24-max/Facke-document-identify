"""
Configuration module for AI-Based Fake Identity & Document Screening System.
Problem Statement ID: 26188
B.Tech CSE Minor Project
"""

import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Flask Configuration
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY", "btech_minor_project_secret_key_26188")
HOST = "0.0.0.0"
PORT = 5000

# File Upload Configuration
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOCUMENTS_FOLDER = os.path.join(UPLOAD_FOLDER, "documents")
SELFIES_FOLDER = os.path.join(UPLOAD_FOLDER, "selfies")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")
SAMPLE_DATA_FOLDER = os.path.join(BASE_DIR, "sample_data")

# Security Constraints
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB maximum upload size

# Database Configuration
DATABASE_FOLDER = os.path.join(BASE_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_FOLDER, "screening.db")

# Risk Engine Thresholds
RISK_VERIFIED_THRESHOLD = 30    # 0 - 29: VERIFIED
RISK_REVIEW_THRESHOLD = 65      # 30 - 64: NEEDS REVIEW
                                # 65 - 100: SUSPICIOUS

# Ensure directories exist
for folder in [UPLOAD_FOLDER, DOCUMENTS_FOLDER, SELFIES_FOLDER, REPORTS_FOLDER, DATABASE_FOLDER, SAMPLE_DATA_FOLDER]:
    os.makedirs(folder, exist_ok=True)
