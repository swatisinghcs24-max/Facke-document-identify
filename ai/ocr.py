"""
OCR Module using EasyOCR with entity extraction for identity documents.
Extracts: Name, Date of Birth, Document Number, Nationality, Expiry Date.
Compares expiry date with the current date to determine expiry status.
"""

import re
from datetime import datetime
from typing import Dict, Any, List, Optional

_reader = None


def get_ocr_reader():
    """Lazy initialization of EasyOCR reader instance."""
    global _reader
    if _reader is None:
        try:
            import easyocr
            # Initialize with English, GPU=False for cross-platform portability
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception:
            _reader = False
    return _reader


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date strings across common identity document formats."""
    date_str = date_str.strip().replace(".", "/").replace("-", "/")
    patterns = [
        "%d/%m/%Y", "%d/%m/%y", "%Y/%m/%d", "%m/%d/%Y",
        "%d %b %Y", "%d %B %Y", "%b %d %Y"
    ]
    for fmt in patterns:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def check_expiry_status(expiry_str: str) -> Dict[str, Any]:
    """
    Compare extracted expiry date with the current date.
    Returns status: 'NOT EXPIRED', 'EXPIRED', or 'NOT DETECTED'.
    """
    if not expiry_str or expiry_str.lower() in ["not detected", "none", "unknown", ""]:
        return {
            "status": "NOT DETECTED",
            "is_expired": False,
            "is_missing": True,
            "message": "Expiry date could not be identified from document text."
        }

    parsed = parse_date(expiry_str)
    if not parsed:
        return {
            "status": "NOT DETECTED",
            "is_expired": False,
            "is_missing": True,
            "message": f"Could not parse extracted date format '{expiry_str}'."
        }

    now = datetime.now()
    if parsed < now:
        return {
            "status": "EXPIRED",
            "is_expired": True,
            "is_missing": False,
            "message": f"Document expired on {parsed.strftime('%d/%m/%Y')}."
        }
    else:
        return {
            "status": "NOT EXPIRED",
            "is_expired": False,
            "is_missing": False,
            "message": f"Document valid until {parsed.strftime('%d/%m/%Y')}."
        }


def extract_entities_from_text(lines: List[str], full_text: str) -> Dict[str, str]:
    """
    Extract structured identity fields using rule-based parsing and regular expressions.
    Never invents data: returns 'Not detected' if a field is absent.
    """
    name = "Not detected"
    dob = "Not detected"
    doc_number = "Not detected"
    nationality = "Not detected"
    expiry_date = "Not detected"

    # Known nationality terms
    nationalities_list = [
        "INDIAN", "AMERICAN", "BRITISH", "CANADIAN", "AUSTRALIAN", "GERMAN",
        "FRENCH", "JAPANESE", "SINGAPOREAN", "ITALIAN", "SPANISH", "MEXICAN",
        "BRAZILIAN", "CHINESE", "SOUTH AFRICAN", "EMIRATI", "IND"
    ]

    for line in lines:
        cleaned = line.strip().upper()

        # Nationality detection
        if nationality == "Not detected":
            for nat in nationalities_list:
                if nat in cleaned:
                    nationality = "Indian" if nat in ["INDIAN", "IND"] else nat.title()
                    break

        # Document number detection (Passport format: [A-Z][0-9]{7,8} or ID format: [A-Z0-9]{8,12})
        if doc_number == "Not detected":
            doc_match = re.search(r'\b([A-Z][0-9]{7,8})\b', cleaned)
            if not doc_match:
                doc_match = re.search(r'(?:PASSPORT|DOC|NO|NUMBER|ID)[\s.:#-]*([A-Z0-9]{7,12})', cleaned)
            if doc_match:
                doc_number = doc_match.group(1).upper()

        # Date of Birth detection
        if dob == "Not detected":
            dob_match = re.search(r'(?:DOB|BIRTH|BORN|DATE OF BIRTH)[\s.:-]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})', cleaned)
            if dob_match:
                dob = dob_match.group(1).replace("-", "/")

        # Expiry Date detection
        if expiry_date == "Not detected":
            exp_match = re.search(r'(?:EXP|EXPIRY|VALID UNTIL|EXPIRATION|UNTIL)[\s.:-]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})', cleaned)
            if exp_match:
                expiry_date = exp_match.group(1).replace("-", "/")

        # Name detection
        if name == "Not detected":
            name_match = re.search(r'(?:NAME|GIVEN NAME|SURNAME|HOLDER)[\s.:-]*([A-Z\s]{3,35})', cleaned)
            if name_match:
                candidate = name_match.group(1).strip()
                if candidate and not any(k in candidate for k in ["PASSPORT", "REPUBLIC", "IDENTITY", "CARD"]):
                    name = candidate.title()

    # Fallback to search general text if dates/numbers weren't found on labeled lines
    if dob == "Not detected":
        all_dates = re.findall(r'\b([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{4})\b', full_text)
        if len(all_dates) >= 1:
            dob = all_dates[0].replace("-", "/")
        if len(all_dates) >= 2 and expiry_date == "Not detected":
            expiry_date = all_dates[1].replace("-", "/")

    # Passport MRZ (Machine Readable Zone) parsing fallback
    # Line format: P<INDLASTNAME<<FIRSTNAME<<<<<<<<<<<<<
    mrz_match = re.search(r'P<([A-Z]{3})([A-Z<]+)', full_text.replace(" ", "").upper())
    if mrz_match:
        if nationality == "Not detected":
            code = mrz_match.group(1)
            if code == "IND":
                nationality = "Indian"
            elif code == "USA":
                nationality = "American"
            elif code == "GBR":
                nationality = "British"
            else:
                nationality = code

        raw_names = mrz_match.group(2).replace("<", " ").strip()
        if raw_names and name == "Not detected":
            name = " ".join(raw_names.split()[:3]).title()

    return {
        "name": name,
        "dob": dob,
        "doc_number": doc_number,
        "nationality": nationality,
        "expiry_date": expiry_date
    }


def perform_ocr(image_path: str) -> Dict[str, Any]:
    """
    Run EasyOCR on the specified image and extract structured identity fields.
    Falls back gracefully if EasyOCR is not available.
    """
    reader = get_ocr_reader()
    extracted_text_lines: List[str] = []

    if reader and reader is not False:
        try:
            results = reader.readtext(image_path, detail=0)
            extracted_text_lines = [str(r) for r in results]
        except Exception as e:
            print(f"[OCR] EasyOCR processing warning: {e}")
            extracted_text_lines = []

    full_text = "\n".join(extracted_text_lines)
    fields = extract_entities_from_text(extracted_text_lines, full_text)
    expiry_check = check_expiry_status(fields["expiry_date"])

    # Missing information checklist
    missing_fields = []
    checks = {
        "name": fields["name"] != "Not detected",
        "dob": fields["dob"] != "Not detected",
        "doc_number": fields["doc_number"] != "Not detected",
        "nationality": fields["nationality"] != "Not detected",
        "expiry_date": fields["expiry_date"] != "Not detected",
    }
    for field_name, is_detected in checks.items():
        if not is_detected:
            missing_fields.append(field_name)

    return {
        "raw_text": full_text,
        "lines": extracted_text_lines,
        "fields": fields,
        "expiry_check": expiry_check,
        "checks": checks,
        "missing_fields": missing_fields
    }
