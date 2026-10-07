"""
Synthetic Sample Document Generator for Testing.
Creates mock sample documents with Pillow/OpenCV for offline demonstration.
Does NOT use real people's identities or authentic government documents.
"""

import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SAMPLE_DIR = Path(__file__).resolve().parent


def create_demo_specimen():
    """Generate a clean synthetic specimen ID card."""
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Outer border & header banner
    draw.rectangle([(20, 20), (780, 480)], outline=(56, 189, 248), width=3)
    draw.rectangle([(20, 20), (780, 90)], fill=(30, 41, 59))

    # Header text
    draw.text((40, 35), "DEMO NATIONAL IDENTITY SPECIMEN", fill=(255, 255, 255))
    draw.text((40, 65), "FOR TESTING ONLY - PROBLEM STATEMENT 26188", fill=(148, 163, 184))

    # Photo Box placeholder
    draw.rectangle([(50, 120), (230, 340)], outline=(94, 234, 212), width=2, fill=(30, 58, 138))
    draw.text((80, 220), "[PHOTO BOX]", fill=(255, 255, 255))

    # Data fields
    fields = [
        ("NAME", "ROHIT KUMAR SHARMA"),
        ("DOB", "14/08/1998"),
        ("DOCUMENT NO", "ID-9821045X"),
        ("NATIONALITY", "INDIAN"),
        ("EXPIRY DATE", "15/10/2032")
    ]

    y = 130
    for label, val in fields:
        draw.text((270, y), f"{label}:", fill=(148, 163, 184))
        draw.text((420, y), val, fill=(241, 245, 249))
        y += 45

    # Footer MRZ
    draw.rectangle([(30, 410), (770, 470)], fill=(2, 6, 23))
    draw.text((40, 420), "I<IND9821045X3<<<<<<<<<<<<<<<<<<", fill=(226, 232, 240))
    draw.text((40, 442), "9808144M3210156IND<<<<<<<<<<<8", fill=(226, 232, 240))

    out_file = SAMPLE_DIR / "sample_id_generated.png"
    img.save(out_file)
    print(f"Generated synthetic specimen at: {out_file}")


if __name__ == "__main__":
    create_demo_specimen()
