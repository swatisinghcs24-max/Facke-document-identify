"""
PDF Report Generation Module using ReportLab.
Produces a formal screening audit report with project headers, extracted metadata,
verification checklist, risk score, and automated screening disclaimer.
"""

import os
from datetime import datetime
from typing import Dict, Any

from backend.config import REPORTS_FOLDER

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
except ImportError:
    letter = None


def generate_pdf_report(screening_data: Dict[str, Any]) -> str:
    """
    Generate a formal PDF report using ReportLab.
    Returns the absolute path to the generated PDF.
    """
    screening_id = screening_data.get("id", "SCR-UNKNOWN")
    pdf_filename = f"report_{screening_id}.pdf"
    pdf_path = os.path.join(REPORTS_FOLDER, pdf_filename)

    if letter is None:
        # Fallback text representation if reportlab is not installed
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write(f"AI-Based Fake Identity & Document Screening Report\n")
            f.write(f"Screening ID: {screening_id}\n")
            f.write(f"Status: {screening_data.get('status')}\n")
            f.write(f"Risk Score: {screening_data.get('risk_score')}/100\n")
        return pdf_path

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#0f172a")     # Deep navy
    accent_color = colors.HexColor("#0284c7")      # Cyan/Blue
    muted_text = colors.HexColor("#475569")

    # Determine status color
    status = screening_data.get("status", "VERIFIED")
    if status == "VERIFIED":
        status_color = colors.HexColor("#16a34a")  # Green
    elif status == "NEEDS REVIEW":
        status_color = colors.HexColor("#d97706")  # Amber
    else:
        status_color = colors.HexColor("#dc2626")  # Red

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=muted_text,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SecHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=10,
        spaceAfter=6
    )

    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748b")
    )

    story = []

    # 1. Header
    story.append(Paragraph("AI-Based Fake Identity & Document Screening Report", title_style))
    story.append(Paragraph("Problem Statement ID: 26188 · B.Tech CSE Minor Project Prototype Audit", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceAfter=14))

    # 2. Executive Summary Bar
    summary_data = [
        [
            Paragraph("<b>Screening ID:</b> " + screening_id, cell_style),
            Paragraph("<b>Timestamp:</b> " + str(screening_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))), cell_style),
        ],
        [
            Paragraph("<b>Document Type:</b> " + str(screening_data.get("document_type", "Passport")), cell_style),
            Paragraph(f"<b>Final Status:</b> <font color='{status_color.hexval()}'><b>{status}</b></font>", cell_style),
        ],
        [
            Paragraph("<b>Risk Score:</b> " + str(screening_data.get("risk_score", 0)) + " / 100", cell_style),
            Paragraph("<b>Tampering Indicator:</b> " + str(screening_data.get("tamper_indicator", "LOW")), cell_style),
        ]
    ]

    t_summary = Table(summary_data, colWidths=[270, 270])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_summary)
    story.append(Spacer(1, 12))

    # 3. Document Extracted Information
    story.append(Paragraph("Extracted Document Information (OCR)", section_heading))
    info_data = [
        [Paragraph("Field", cell_bold), Paragraph("Extracted Value", cell_bold), Paragraph("Extraction Status", cell_bold)],
        [Paragraph("Holder Full Name", cell_style), Paragraph(str(screening_data.get("name", "Not detected")), cell_style), Paragraph("Detected" if screening_data.get("name") != "Not detected" else "Not detected", cell_style)],
        [Paragraph("Date of Birth (DOB)", cell_style), Paragraph(str(screening_data.get("dob", "Not detected")), cell_style), Paragraph("Detected" if screening_data.get("dob") != "Not detected" else "Not detected", cell_style)],
        [Paragraph("Document Number", cell_style), Paragraph(str(screening_data.get("doc_number", "Not detected")), cell_style), Paragraph("Detected" if screening_data.get("doc_number") != "Not detected" else "Not detected", cell_style)],
        [Paragraph("Nationality", cell_style), Paragraph(str(screening_data.get("nationality", "Not detected")), cell_style), Paragraph("Detected" if screening_data.get("nationality") != "Not detected" else "Not detected", cell_style)],
        [Paragraph("Expiry Date", cell_style), Paragraph(str(screening_data.get("expiry_date", "Not detected")), cell_style), Paragraph("Detected" if screening_data.get("expiry_date") != "Not detected" else "Not detected", cell_style)],
    ]
    t_info = Table(info_data, colWidths=[150, 240, 150])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_info)
    story.append(Spacer(1, 12))

    # 4. Multi-Layer Verification Audit
    story.append(Paragraph("Verification Analysis Breakdown", section_heading))
    face_sim_str = f"{screening_data.get('face_similarity'):.1f}%" if screening_data.get("face_similarity") is not None else "N/A (No selfie)"
    audit_data = [
        [Paragraph("Verification Check", cell_bold), Paragraph("Analysis Result", cell_bold), Paragraph("Risk Contribution", cell_bold)],
        [Paragraph("Document Quality (Sharpness/Exposure)", cell_style), Paragraph(str(screening_data.get("doc_quality", "GOOD")), cell_style), Paragraph("Nominal" if screening_data.get("doc_quality") == "GOOD" else "High penalty", cell_style)],
        [Paragraph("Tamper Indicator Analysis (OpenCV)", cell_style), Paragraph(str(screening_data.get("tamper_indicator", "LOW")), cell_style), Paragraph(f"Score {screening_data.get('tamper_score', 0):.1f}/100", cell_style)],
        [Paragraph("Biometric Face Verification", cell_style), Paragraph(f"{screening_data.get('face_match_status', 'N/A')} ({face_sim_str})", cell_style), Paragraph("Biometric correlation", cell_style)],
        [Paragraph("Expiry Date Status", cell_style), Paragraph("Checked against system date", cell_style), Paragraph("Valid" if "expired" not in str(screening_data.get("reasons", "")).lower() else "Expired Penalty", cell_style)],
    ]
    t_audit = Table(audit_data, colWidths=[200, 190, 150])
    t_audit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#f1f5f9")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_audit)
    story.append(Spacer(1, 12))

    # 5. Recommendation & Reason Observations
    story.append(Paragraph("Screening Observations & Recommendation", section_heading))
    reasons = screening_data.get("reasons", [])
    if isinstance(reasons, str):
        reasons = [reasons]
    reasons_text = "<br/>".join([f"• {r}" for r in reasons]) if reasons else "• All checks completed within standard parameters."
    story.append(Paragraph(reasons_text, cell_style))
    story.append(Spacer(1, 8))

    rec = screening_data.get("recommendation", "Manual verification recommended.")
    story.append(Paragraph(f"<b>System Recommendation:</b> {rec}", cell_bold))
    story.append(Spacer(1, 14))

    # 6. Important Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    disclaimer_text = (
        "<b>IMPORTANT NOTICE & DISCLAIMER:</b> This report represents an initial automated first-level screening indication "
        "generated by an academic prototype (Problem Statement 26188). It does NOT constitute official, conclusive, or legal proof "
        "of identity validity or fraud. Possible tampering indicators detected require certified manual verification by authorized personnel."
    )
    story.append(Paragraph(disclaimer_text, disclaimer_style))

    doc.build(story)
    return pdf_path
