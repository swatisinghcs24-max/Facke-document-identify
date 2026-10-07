"""
Database operations for the screening system using SQLite.
Stores screening metadata, extracted fields, quality scores, tamper scores, face scores, and final status.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.config import DATABASE_PATH


def get_db_connection() -> sqlite3.Connection:
    """Establish and return a SQLite database connection with row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite screening database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS screenings (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP NOT NULL,
            document_name TEXT NOT NULL,
            document_type TEXT NOT NULL,
            selfie_name TEXT,
            name TEXT,
            dob TEXT,
            doc_number TEXT,
            nationality TEXT,
            expiry_date TEXT,
            ocr_text TEXT,
            doc_quality TEXT NOT NULL,
            doc_quality_reasons TEXT,
            tamper_indicator TEXT NOT NULL,
            tamper_score REAL NOT NULL,
            face_similarity REAL,
            face_match_status TEXT,
            risk_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            reasons TEXT NOT NULL,
            recommendation TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def insert_screening(data: Dict[str, Any]) -> str:
    """Insert a new screening record into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO screenings (
            id, created_at, document_name, document_type, selfie_name,
            name, dob, doc_number, nationality, expiry_date, ocr_text,
            doc_quality, doc_quality_reasons, tamper_indicator, tamper_score,
            face_similarity, face_match_status, risk_score, status, reasons, recommendation
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?
        )
    """, (
        data.get("id"),
        data.get("created_at", datetime.now().isoformat()),
        data.get("document_name", "document.jpg"),
        data.get("document_type", "Passport"),
        data.get("selfie_name"),
        data.get("name", "Not detected"),
        data.get("dob", "Not detected"),
        data.get("doc_number", "Not detected"),
        data.get("nationality", "Not detected"),
        data.get("expiry_date", "Not detected"),
        data.get("ocr_text", ""),
        data.get("doc_quality", "GOOD"),
        json.dumps(data.get("doc_quality_reasons", [])),
        data.get("tamper_indicator", "LOW"),
        float(data.get("tamper_score", 0.0)),
        data.get("face_similarity"),
        data.get("face_match_status", "NOT COMPLETED"),
        int(data.get("risk_score", 0)),
        data.get("status", "VERIFIED"),
        json.dumps(data.get("reasons", [])),
        data.get("recommendation", "Automated screening complete.")
    ))

    conn.commit()
    conn.close()
    return data["id"]


def get_all_screenings(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve all recent screenings."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM screenings
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        try:
            item["reasons"] = json.loads(item["reasons"])
        except Exception:
            item["reasons"] = []
        try:
            item["doc_quality_reasons"] = json.loads(item["doc_quality_reasons"])
        except Exception:
            item["doc_quality_reasons"] = []
        result.append(item)

    return result


def get_screening_by_id(screening_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a single screening record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM screenings WHERE id = ?", (screening_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    item = dict(row)
    try:
        item["reasons"] = json.loads(item["reasons"])
    except Exception:
        item["reasons"] = []
    try:
        item["doc_quality_reasons"] = json.loads(item["doc_quality_reasons"])
    except Exception:
        item["doc_quality_reasons"] = []
    return item


def get_statistics() -> Dict[str, Any]:
    """Retrieve aggregated screening statistics for the dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) AS total FROM screenings")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS count FROM screenings WHERE status = 'VERIFIED'")
    verified = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM screenings WHERE status = 'NEEDS REVIEW'")
    needs_review = cursor.fetchone()["count"]

    cursor.execute("SELECT COUNT(*) AS count FROM screenings WHERE status = 'SUSPICIOUS'")
    suspicious = cursor.fetchone()["count"]

    cursor.execute("SELECT AVG(risk_score) AS avg_risk FROM screenings")
    avg_risk_row = cursor.fetchone()
    avg_risk = round(avg_risk_row["avg_risk"], 1) if avg_risk_row and avg_risk_row["avg_risk"] is not None else 0.0

    conn.close()

    return {
        "total_screenings": total,
        "verified_count": verified,
        "needs_review_count": needs_review,
        "suspicious_count": suspicious,
        "average_risk_score": avg_risk
    }
