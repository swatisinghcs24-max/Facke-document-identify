"""
Main Flask Application Server.
AI-Based Fake Identity & Document Screening System (Problem Statement ID: 26188)
Runs on http://127.0.0.1:5000
"""

import os
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, render_template, redirect, url_for

from backend.config import (
    BASE_DIR, HOST, PORT, DEBUG, SECRET_KEY,
    MAX_CONTENT_LENGTH, DATABASE_PATH
)
from backend.database import init_db, insert_screening, get_statistics
from backend.routes import api

# Initialize Flask app pointing static folder to frontend
frontend_dir = os.path.join(BASE_DIR, "frontend")
app = Flask(__name__, static_folder=frontend_dir, static_url_path="")
app.config["SECRET_KEY"] = SECRET_KEY
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# Register API blueprint
app.register_blueprint(api, url_prefix="/api")


def seed_demo_data_if_empty():
    """Seed initial realistic mock screenings for academic demonstration."""
    stats = get_statistics()
    if stats["total_screenings"] == 0:
        now = datetime.now()
        samples = [
            {
                "id": "SCR-20261005-A1092F",
                "created_at": (now - timedelta(days=2)).isoformat(),
                "document_name": "sample_passport_rohit.jpg",
                "document_type": "Passport",
                "selfie_name": "selfie_rohit.jpg",
                "name": "Rohit Sharma",
                "dob": "14/08/1996",
                "doc_number": "Z8921045",
                "nationality": "Indian",
                "expiry_date": "24/11/2032",
                "ocr_text": "REPUBLIC OF INDIA PASSPORT P<INDR OHIT<<SHARMA<<<<<<< Z8921045",
                "doc_quality": "GOOD",
                "doc_quality_reasons": [],
                "tamper_indicator": "LOW",
                "tamper_score": 8.5,
                "face_similarity": 91.4,
                "face_match_status": "MATCH",
                "risk_score": 14,
                "status": "VERIFIED",
                "reasons": [
                    "All key identity fields successfully extracted via OCR.",
                    "Document is valid and unexpired.",
                    "Document resolution, brightness, and sharpness meet screening standards.",
                    "Image edge density and noise metrics are within nominal ranges.",
                    "Biometric facial match confirmed (91.4% similarity)."
                ],
                "recommendation": "Document passed initial automated screening. Nominal risk parameters observed."
            },
            {
                "id": "SCR-20261005-B7419C",
                "created_at": (now - timedelta(days=1)).isoformat(),
                "document_name": "sample_visa_david.jpg",
                "document_type": "Visa",
                "selfie_name": "selfie_david.jpg",
                "name": "David Miller",
                "dob": "21/03/1988",
                "doc_number": "V4490123",
                "nationality": "American",
                "expiry_date": "10/01/2024",
                "ocr_text": "TOURIST VISA V4490123 EXP 10/01/2024 DAVID MILLER",
                "doc_quality": "GOOD",
                "doc_quality_reasons": [],
                "tamper_indicator": "LOW",
                "tamper_score": 12.0,
                "face_similarity": 84.2,
                "face_match_status": "MATCH",
                "risk_score": 49,
                "status": "NEEDS REVIEW",
                "reasons": [
                    "All key identity fields successfully extracted via OCR.",
                    "Document validity check failed: Document expired on 10/01/2024 (+35 risk).",
                    "Document resolution, brightness, and sharpness meet screening standards.",
                    "Image edge density and noise metrics are within nominal ranges.",
                    "Biometric facial match confirmed (84.2% similarity)."
                ],
                "recommendation": "Manual verification is recommended. Document has passed its expiration threshold."
            },
            {
                "id": "SCR-20261006-C9821E",
                "created_at": (now - timedelta(hours=5)).isoformat(),
                "document_name": "sample_id_tampered.png",
                "document_type": "ID Card",
                "selfie_name": "selfie_unknown.jpg",
                "name": "Not detected",
                "dob": "01/01/2000",
                "doc_number": "ID-991200",
                "nationality": "Not detected",
                "expiry_date": "Not detected",
                "ocr_text": "SAMPLE CARD 991200",
                "doc_quality": "POOR",
                "doc_quality_reasons": ["Low image sharpness / high blur detected.", "Inconsistent brightness."],
                "tamper_indicator": "HIGH",
                "tamper_score": 68.0,
                "face_similarity": 38.5,
                "face_match_status": "NO MATCH",
                "risk_score": 82,
                "status": "SUSPICIOUS",
                "reasons": [
                    "Required field 'Name' was not detected (+15 risk).",
                    "Required field 'Nationality' was not detected (+8 risk).",
                    "Document optical quality flagged as POOR (+20 risk).",
                    "Elevated structural/edge tampering indicators detected (+40 risk).",
                    "Biometric face mismatch: similarity is only 38.5% (+40 risk)."
                ],
                "recommendation": "High risk indicators detected. Mandatory physical or certified human verification required."
            }
        ]
        for s in samples:
            insert_screening(s)


# Frontend static page routes
@app.route("/")
def index():
    return send_from_directory(frontend_dir, "index.html")


@app.route("/upload")
def upload_page():
    return send_from_directory(frontend_dir, "upload.html")


@app.route("/processing")
def processing_page():
    return send_from_directory(frontend_dir, "processing.html")


@app.route("/result")
def result_page():
    return send_from_directory(frontend_dir, "result.html")


@app.route("/dashboard")
def dashboard_page():
    return send_from_directory(frontend_dir, "dashboard.html")


@app.route("/history")
def history_page():
    return send_from_directory(frontend_dir, "history.html")


@app.route("/report")
def report_page():
    return send_from_directory(frontend_dir, "report.html")


# Serve sample data for quick testing
@app.route("/sample_data/<path:filename>")
def serve_sample(filename):
    sample_dir = os.path.join(BASE_DIR, "sample_data")
    return send_from_directory(sample_dir, filename)


# Initialize SQLite Database upon import/startup
init_db()
seed_demo_data_if_empty()

if __name__ == "__main__":
    print(f"\n=======================================================")
    print(f"  AI-Based Fake Identity & Document Screening System")
    print(f"  Problem Statement ID: 26188 | B.Tech CSE Minor Project")
    print(f"  Server starting on: http://127.0.0.1:{PORT}")
    print(f"=======================================================\n")
    app.run(host=HOST, port=PORT, debug=DEBUG)
