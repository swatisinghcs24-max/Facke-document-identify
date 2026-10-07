# AI-Based Fake Identity & Document Screening System

**Problem Statement ID:** 26188  
**Project Category:** B.Tech CSE Minor Project  
**Domain:** Cybersecurity / Applied Computer Vision / Identity Document Verification  

---

## 1. Project Introduction

Identity fraud in digital onboarding, travel processing, and KYC workflows is a major cybersecurity vulnerability. The **AI-Based Fake Identity & Document Screening System** provides a first-level automated verification pipeline designed to flag anomalies in identity documents such as passports, entry visas, and national identity cards.

The system combines:
1. **EasyOCR** for automated text and machine-readable zone (MRZ) entity extraction.
2. **OpenCV Computer Vision** for image quality assurance (sharpness via Laplacian variance, resolution, and exposure).
3. **Prototype Tampering Analysis** checking edge density anomalies, localized noise inconsistencies, and compression artifacts.
4. **Biometric Face Verification** correlating the document photograph with an applicant selfie.
5. **Risk Engine (`risk_engine.py`)** scoring cumulative risk on a normalized 0–100 scale with full explainability.

> **CRITICAL LEGAL NOTICE & DISCLAIMER:**  
> This system is an automated **first-level screening indicator** and does **not constitute official legal proof of fraud**. All highlighted anomalies are intended as screening flags to assist human adjudicators and require certified manual verification.

---

## 2. Main User Flow

```text
HOME
  ↓
DOCUMENT UPLOAD or LIVE CAMERA CAPTURE (MediaDevices API)
  ↓
SELFIE UPLOAD or LIVE WEBCAM SELFIE (MediaDevices API)
  ↓
FILE VALIDATION (Type, size, integrity)
  ↓
OCR PROCESSING (EasyOCR)
  ↓
INFORMATION EXTRACTION (Name, DOB, Doc No, Nationality, Expiry)
  ↓
DOCUMENT QUALITY CHECK (Resolution, blur, lighting)
  ↓
EXPIRY CHECK (Checked against real-time clock)
  ↓
MISSING INFORMATION CHECK
  ↓
TAMPERING INDICATOR ANALYSIS (Edge density, noise variance)
  ↓
FACE VERIFICATION (OpenCV Haar/Feature similarity)
  ↓
RISK ANALYSIS (0–100 Normalized Engine)
  ↓
FINAL RESULT (VERIFIED / NEEDS REVIEW / SUSPICIOUS)
  ↓
SAVE RESULT TO DATABASE (SQLite)
  ↓
GENERATE REPORT (ReportLab PDF)
```

---

## 3. Technology Stack

- **Backend:** Python 3.10+, Flask 2.3+
- **OCR Engine:** EasyOCR (English + Latin models)
- **Computer Vision:** OpenCV (`cv2`), NumPy, Pillow
- **Database:** SQLite (`database/screening.db`)
- **Report Engine:** ReportLab (vector PDF generation)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Chart.js
- **Camera Capture:** HTML5 MediaDevices API (`navigator.mediaDevices.getUserMedia`) with live document framing guide & biometric face alignment
- **Design System:** Cybersecurity Dark Navy Theme with Glassmorphism Cards

---

## 4. Complete Project Directory Structure

```text
Fake-Identity-Detection/
│
├── frontend/
│   ├── index.html           # Cybersecurity landing page
│   ├── upload.html          # Document & selfie upload interface with presets
│   ├── processing.html      # Animated pipeline audit checklist
│   ├── result.html          # Explainable screening result & risk dial
│   ├── dashboard.html       # Security admin telemetry with Chart.js
│   ├── history.html         # SQLite audit log with search & filters
│   ├── report.html          # In-browser printable report view
│   ├── style.css            # Dark-navy cybersecurity styling
│   └── script.js            # Frontend API client and DOM renderer
│
├── backend/
│   ├── __init__.py          # Backend package initializer
│   ├── app.py               # Flask application server (serves frontend & APIs)
│   ├── routes.py            # RESTful API endpoints (/api/screen, /api/stats, etc.)
│   ├── database.py          # SQLite schema creation & CRUD operations
│   ├── report_generator.py  # ReportLab PDF report builder
│   └── config.py            # Global paths, thresholds, and security parameters
│
├── ai/
│   ├── __init__.py          # AI package initializer
│   ├── ocr.py               # EasyOCR wrapper, regex entity parser & expiry check
│   ├── document_detection.py# OpenCV optical quality (blur, exposure, resolution)
│   ├── tamper_detection.py  # Prototype image integrity & edge density heuristic
│   ├── face_verification.py # OpenCV face detection & histogram similarity
│   └── risk_engine.py       # 0–100 multi-signal risk synthesizer
│
├── utils/
│   ├── file_validation.py   # Whitelist extension, size & sanitization checks
│   └── image_utils.py       # Safe OpenCV image loading & resizing
│
├── database/
│   └── screening.db         # Persistent SQLite database
│
├── uploads/
│   ├── documents/           # Stored identity documents
│   └── selfies/             # Stored applicant selfies
│
├── reports/                 # Output directory for generated PDF audit reports
├── sample_data/             # Synthetic test documents & generator script
│   ├── sample_manifest.json # Catalog of test cases (clean, expired, tampered)
│   └── generate_samples.py  # Script to generate synthetic test ID cards
│
├── requirements.txt         # Python package dependencies
├── README.md                # Project documentation & run guide
└── .gitignore               # Ignored artifacts & environment directories
```

---

## 5. Local Setup & Installation (Windows / VS Code)

Follow these steps to run the complete Flask application locally on Windows:

### Step 1: Open Terminal in VS Code
Open VS Code in the project root folder.

### Step 2: Create a Virtual Environment
```powershell
py -m venv .venv
```

### Step 3: Activate the Virtual Environment
On Windows PowerShell:
```powershell
.venv\Scripts\activate
```
*(On macOS/Linux: `source .venv/bin/activate`)*

### Step 4: Upgrade Pip & Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Run the Screening Server
```powershell
python -m backend.app
```

### Step 6: Open in Browser
Navigate to:
```text
http://127.0.0.1:5000
```

---

## 6. REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System status and service metadata |
| `POST` | `/api/screen` | Multipart upload (`document`, optional `selfie`, `document_type`) returning analysis JSON |
| `GET` | `/api/screenings` | List recent screening records from SQLite |
| `GET` | `/api/screenings/<id>` | Retrieve full forensic record for a single screening |
| `GET` | `/api/stats` | Aggregated telemetry counts (`verified`, `needs_review`, `suspicious`) |
| `GET` | `/api/reports/<id>` | Download formal ReportLab PDF audit report |

---

## 7. Risk Engine Scoring & Classification

The risk engine (`ai/risk_engine.py`) aggregates penalty points from all inspection layers:

- **Missing Mandatory Fields:** +8 to +15 points per undetected field (Name, DOB, Doc Number, Expiry).
- **Expired Document:** +35 points penalty.
- **Document Optical Quality POOR:** +20 points penalty (severe blur or underexposure).
- **Tampering Anomaly:** +20 points (Medium) or +40 points (High).
- **Face Similarity Mismatch:** +18 to +40 points penalty.

### Classification Thresholds:
- **`0 – 29`:** **`VERIFIED`** (Passed automated screening; nominal risk)
- **`30 – 64`:** **`NEEDS REVIEW`** (Moderate risk; manual officer review recommended)
- **`65 – 100`:** **`SUSPICIOUS`** (High risk; physical document verification required)

---

## 8. Limitations & Future Scope

### Known Prototype Limitations:
1. **OCR Heuristics:** Highly stylized or handwritten fonts may result in `Not detected` for certain fields.
2. **OpenCV Face Verification:** Utilizes classical histogram and gradient correlation; intended for prototype demonstration rather than production biometric liveness checks.
3. **Tamper Indicators:** Based on edge gradient variance and noise floor distribution; not capable of detecting state-of-the-art AI deepfakes without specialized neural networks.

### Future Scope:
1. Integration with official government verification APIs (e.g., DigiLocker, ICAO Public Key Directory).
2. Deep learning-based Error Level Analysis (ELA) and CNN-based copy-move forgery detection.
3. Active 3D facial liveness detection (blink/head motion challenges) to defeat printed photo presentation attacks.

---

**Developed for B.Tech Computer Science and Engineering Minor Project Submission.**
