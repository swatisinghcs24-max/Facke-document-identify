"""
API routes for the Screening System.
Implements:
- GET  /api/health
- POST /api/screen
- GET  /api/screenings
- GET  /api/screenings/<id>
- GET  /api/stats
- GET  /api/reports/<id>
"""

import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file, current_app

from backend.config import DOCUMENTS_FOLDER, SELFIES_FOLDER, REPORTS_FOLDER
from backend.database import insert_screening, get_all_screenings, get_screening_by_id, get_statistics
from backend.report_generator import generate_pdf_report
from utils.file_validation import validate_file_upload, generate_unique_filename
from ai.ocr import perform_ocr
from ai.document_detection import analyze_document_quality
from ai.tamper_detection import detect_tampering_indicators
from ai.face_verification import verify_faces
from ai.risk_engine import calculate_risk_score

api = Blueprint("api", __name__)


@api.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "healthy",
        "service": "AI-Based Fake Identity & Document Screening System",
        "problem_statement": "26188",
        "version": "1.0.0-prototype",
        "timestamp": datetime.now().isoformat()
    }), 200


@api.route("/screen", methods=["POST"])
def screen_document():
    """
    Main Screening Endpoint:
    Processes document + optional selfie through complete verification pipeline.
    """
    if "document" not in request.files:
        return jsonify({"error": "Document image file is required."}), 400

    doc_file = request.files["document"]
    selfie_file = request.files.get("selfie")
    doc_type = request.form.get("document_type", "Passport")

    # 1. File Validation
    is_valid, msg = validate_file_upload(doc_file)
    if not is_valid:
        return jsonify({"error": f"Document file validation failed: {msg}"}), 400

    doc_filename = generate_unique_filename("doc", doc_file.filename)
    doc_path = os.path.join(DOCUMENTS_FOLDER, doc_filename)
    doc_file.save(doc_path)

    selfie_filename = None
    selfie_path = None
    if selfie_file and selfie_file.filename != "":
        s_valid, s_msg = validate_file_upload(selfie_file)
        if s_valid:
            selfie_filename = generate_unique_filename("selfie", selfie_file.filename)
            selfie_path = os.path.join(SELFIES_FOLDER, selfie_filename)
            selfie_file.save(selfie_path)

    # 2. Pipeline Execution
    # OCR extraction
    ocr_result = perform_ocr(doc_path)

    # Quality check
    quality_result = analyze_document_quality(doc_path)

    # Tampering analysis
    tamper_result = detect_tampering_indicators(doc_path)

    # Face verification
    face_result = verify_faces(doc_path, selfie_path)

    # Risk Engine Synthesis
    risk_score, status, reasons, recommendation = calculate_risk_score(
        ocr_result=ocr_result,
        quality_result=quality_result,
        tamper_result=tamper_result,
        face_result=face_result
    )

    screening_id = f"SCR-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    record_data = {
        "id": screening_id,
        "created_at": datetime.now().isoformat(),
        "document_name": doc_filename,
        "document_type": doc_type,
        "selfie_name": selfie_filename,
        "name": ocr_result["fields"]["name"],
        "dob": ocr_result["fields"]["dob"],
        "doc_number": ocr_result["fields"]["doc_number"],
        "nationality": ocr_result["fields"]["nationality"],
        "expiry_date": ocr_result["fields"]["expiry_date"],
        "ocr_text": ocr_result.get("raw_text", ""),
        "doc_quality": quality_result["quality"],
        "doc_quality_reasons": quality_result["reasons"],
        "tamper_indicator": tamper_result["indicator"],
        "tamper_score": tamper_result["tamper_score"],
        "face_similarity": face_result.get("similarity"),
        "face_match_status": face_result.get("status", "NOT COMPLETED"),
        "risk_score": risk_score,
        "status": status,
        "reasons": reasons,
        "recommendation": recommendation
    }

    # 3. Save result to database
    try:
        insert_screening(record_data)
    except Exception as e:
        print(f"[Database Error]: {e}")

    # Return comprehensive response
    return jsonify({
        "screening_id": screening_id,
        "status": status,
        "risk_score": risk_score,
        "document_type": doc_type,
        "extracted_fields": ocr_result["fields"],
        "checks": ocr_result["checks"],
        "expiry_status": ocr_result["expiry_check"],
        "quality": quality_result,
        "tampering": tamper_result,
        "face_verification": face_result,
        "reasons": reasons,
        "recommendation": recommendation,
        "disclaimer": "This result is an automated first-level screening indication and not official proof of fraud. Manual verification is recommended."
    }), 201


@api.route("/screenings", methods=["GET"])
def get_screenings():
    """Retrieve list of historical screenings."""
    limit = request.args.get("limit", 50, type=int)
    screenings = get_all_screenings(limit)
    return jsonify({"screenings": screenings}), 200


@api.route("/screenings/<screening_id>", methods=["GET"])
def get_single_screening(screening_id):
    """Retrieve a specific screening record by ID."""
    record = get_screening_by_id(screening_id)
    if not record:
        return jsonify({"error": "Screening record not found."}), 404
    return jsonify({"screening": record}), 200


@api.route("/stats", methods=["GET"])
def get_stats():
    """Retrieve aggregate screening metrics for the dashboard."""
    stats = get_statistics()
    return jsonify(stats), 200


@api.route("/reports/<screening_id>", methods=["GET"])
def download_report(screening_id):
    """Generate and download the ReportLab PDF report for a screening."""
    record = get_screening_by_id(screening_id)
    if not record:
        return jsonify({"error": "Screening record not found for report generation."}), 404

    try:
        pdf_path = generate_pdf_report(record)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Screening_Report_{screening_id}.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"error": f"Failed to generate report: {str(e)}"}), 500
