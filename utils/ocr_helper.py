"""
OCR & Medical Lab Report Parser Utility for MediGuardian AI
Safely extracts text using PaddleOCR / Tesseract with graceful error-handling for Streamlit Cloud.
DISCLAIMER: Educational purpose only. Not medical advice. For emergency in India call 112.
"""

import io
import re
from typing import Tuple, List, Dict, Any
from PIL import Image

# Safe PaddleOCR import
PADDLE_AVAILABLE = False
try:
    from paddleocr import PaddleOCR
    # Initialize lazily when needed
    PADDLE_AVAILABLE = True
except Exception:
    PADDLE_AVAILABLE = False

# Safe Pytesseract import
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False


def extract_text(file_obj) -> Tuple[str, float]:
    """
    Attempts to extract text from an uploaded image or PDF file.
    Tries PaddleOCR first, then Pytesseract, then returns empty string with fallback warning.
    NEVER crashes, even if OCR binaries are missing on Streamlit Cloud.
    Returns: (extracted_text, confidence_percentage)
    """
    if file_obj is None:
        return ("", 0.0)

    # Convert uploaded file to PIL Image if possible
    image = None
    try:
        file_bytes = file_obj.read()
        file_obj.seek(0)  # reset pointer for any subsequent read
        image = Image.open(io.BytesIO(file_bytes))
    except Exception:
        # Might be PDF or raw text
        pass

    # Method 1: Try PaddleOCR if available
    if PADDLE_AVAILABLE and image:
        try:
            ocr = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
            img_bytes = io.BytesIO()
            image.save(img_bytes, format="PNG")
            result = ocr.ocr(img_bytes.getvalue(), cls=True)

            text_lines = []
            scores = []
            if result and len(result) > 0 and result[0]:
                for line in result[0]:
                    txt = line[1][0]
                    score = float(line[1][1])
                    text_lines.append(txt)
                    scores.append(score)

            if text_lines:
                avg_conf = (sum(scores) / len(scores)) * 100.0 if scores else 85.0
                return ("\n".join(text_lines), round(avg_conf, 1))
        except Exception as e:
            print(f"PaddleOCR attempt skipped or failed: {e}")

    # Method 2: Try Pytesseract if available
    if TESSERACT_AVAILABLE and image:
        try:
            # Check if tesseract binary can execute
            text = pytesseract.image_to_string(image)
            if text and text.strip():
                # Estimate confidence from image_to_data if possible
                try:
                    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
                    confs = [float(c) for c in data.get("conf", []) if str(c).isnumeric() and float(c) > 0]
                    avg_conf = sum(confs) / len(confs) if confs else 80.0
                except Exception:
                    avg_conf = 80.0
                return (text.strip(), round(avg_conf, 1))
        except Exception as e:
            print(f"Pytesseract attempt skipped or failed: {e}")

    # Method 3: If it's a text-based PDF or text document
    try:
        file_bytes = file_obj.read()
        file_obj.seek(0)
        decoded_text = file_bytes.decode("utf-8", errors="ignore").strip()
        if len(decoded_text) > 20 and any(keyword in decoded_text.lower() for keyword in ["blood", "test", "hemoglobin", "glucose", "cholesterol"]):
            return (decoded_text, 90.0)
    except Exception:
        pass

    return ("", 0.0)


def parse_lab_values(text: str) -> List[Dict[str, Any]]:
    """
    Extracts structured lab test records from raw OCR text using regex.
    Matches test name, numerical value, unit, and reference range.
    """
    records = []
    if not text or not text.strip():
        return records

    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Regex specified in requirements:
    # r"([A-Za-z %]+)\s+([\d\.]+)\s*([a-zA-Z/%]+)?\s*\(?([\d\.\-–\s]+)?\)?"
    pattern = re.compile(r"([A-Za-z\s\(\)/_-]+?)\s+([\d\.]+)\s*([a-zA-Z/%μ\^]+)?\s*(?:\(?([\d\.\-–\s<>=]+)\)?)?")

    for line in lines:
        # Ignore purely headers or short labels
        if len(line) < 3 or line.lower().startswith(("page", "date", "dr.", "patient", "name:", "age:")):
            continue

        match = pattern.search(line)
        if match:
            test_name = match.group(1).strip()
            val_str = match.group(2).strip()
            unit = (match.group(3) or "").strip()
            ref_range = (match.group(4) or "").strip().strip("()")

            # Exclude false positives (e.g. single words or dates like "Oct 2024")
            if len(test_name) < 2 or not val_str:
                continue

            try:
                numeric_val = float(val_str)
            except ValueError:
                numeric_val = None

            is_outside = evaluate_outside_range(numeric_val, ref_range)

            records.append({
                "test_name": test_name,
                "test_value": val_str,
                "test_value_numeric": numeric_val,
                "unit": unit,
                "ref_range": ref_range,
                "is_outside_range": is_outside,
                "is_verified": False
            })

    return records


def evaluate_outside_range(numeric_val: float, ref_range_str: str) -> bool:
    """
    Evaluates whether a numeric lab test value falls outside the defined reference range.
    Handles ranges like '70-100', '13.0 - 17.0', '< 200', '> 50'.
    """
    if numeric_val is None or not ref_range_str:
        return False

    clean_range = ref_range_str.replace("–", "-").replace("—", "-").strip()

    try:
        # Check < or <=
        if "<" in clean_range:
            cutoff = float(re.sub(r"[^\d\.]", "", clean_range))
            return numeric_val >= cutoff
        # Check > or >=
        if ">" in clean_range:
            cutoff = float(re.sub(r"[^\d\.]", "", clean_range))
            return numeric_val <= cutoff
        # Check hyphenated range min-max
        if "-" in clean_range:
            parts = [p.strip() for p in clean_range.split("-") if p.strip()]
            if len(parts) >= 2:
                low = float(re.sub(r"[^\d\.]", "", parts[0]))
                high = float(re.sub(r"[^\d\.]", "", parts[1]))
                return numeric_val < low or numeric_val > high
    except Exception:
        pass

    return False


def get_sample_lab_report_text() -> str:
    """Provides a realistic sample lab report string for quick user testing."""
    return """
METROPOLITAN CLINICAL DIAGNOSTIC LABORATORY
Patient Name: Demo User | Age: 35 | Gender: Male
Report Date: 2026-10-15

TEST DESCRIPTION                       RESULT    UNIT      REFERENCE RANGE
========================================================================
Hemoglobin                            14.2      g/dL      13.0 - 17.0
Fasting Blood Sugar                   115.0     mg/dL     70.0 - 100.0
HbA1c Glycated Hemoglobin             6.4       %         4.0 - 5.6
Total Cholesterol                     215.0     mg/dL     < 200.0
HDL Cholesterol                       45.0      mg/dL     40.0 - 60.0
LDL Cholesterol                       135.0     mg/dL     < 100.0
Triglycerides                         180.0     mg/dL     < 150.0
Serum Creatinine                      1.05      mg/dL     0.7 - 1.3
Serum Uric Acid                       6.1       mg/dL     3.5 - 7.2
Total Leukocyte Count (WBC)           7200      /cumm     4000 - 11000
Platelet Count                        260000    /cumm     150000 - 450000
TSH Thyroid Stimulating Hormone       2.45      uIU/mL    0.4 - 4.2
========================================================================
Verified by: Chief Pathologist (Educational Demo Mock Report)
"""
