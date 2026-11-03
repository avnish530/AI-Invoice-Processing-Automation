import re
from datetime import datetime
from pathlib import Path

def _pdf_text(data: bytes) -> str:
    try:
        import pdfplumber
        import io
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        return ""

def _image_text(data: bytes) -> str:
    try:
        from PIL import Image
        import pytesseract
        import io
        return pytesseract.image_to_string(Image.open(io.BytesIO(data)))
    except Exception:
        return ""

def _first(patterns, text, flags=re.I):
    for pattern in patterns:
        match = re.search(pattern, text, flags)
        if match:
            return match.group(1).strip(" \t\n:|")
    return ""

def _amount(text, labels):
    for label in labels:
        pattern = rf"{label}\s*[:\-]?\s*(?:INR|Rs\.?|₹)?\s*([\d,]+(?:\.\d{{1,2}})?)"
        m = re.search(pattern, text, re.I)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                pass
    return None

def extract_invoice(data: bytes, filename: str) -> dict:
    suffix = Path(filename).suffix.lower()
    text = _pdf_text(data) if suffix == ".pdf" else _image_text(data)
    if not text.strip():
        text = ""

    vendor = _first([
        r"(?:vendor|supplier|from)\s*[:\-]\s*(.+)",
        r"^([A-Z][A-Za-z0-9 &.,'-]{2,})$"
    ], text, re.I | re.M)
    invoice_no = _first([
        r"(?:invoice\s*(?:no\.?|number|#)|bill\s*no\.?)\s*[:\-]?\s*([A-Z0-9\-\/]+)"
    ], text)
    date = _first([
        r"(?:invoice\s*date|date)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})"
    ], text)
    due_date = _first([
        r"(?:due\s*date|payment\s*due)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})"
    ], text)

    total = _amount(text, [r"grand\s*total", r"total\s*amount", r"amount\s*due", r"total"])
    tax = _amount(text, [r"tax", r"gst"])
    subtotal = _amount(text, [r"sub\s*total", r"subtotal"])

    # Normalize common date formats to ISO when possible.
    def normalize(value):
        if not value:
            return ""
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d",
                    "%d/%m/%y", "%d-%m-%y"):
            try:
                return datetime.strptime(value, fmt).date().isoformat()
            except ValueError:
                continue
        return value

    date, due_date = normalize(date), normalize(due_date)
    required = [vendor, invoice_no, date, total is not None]
    status = "Processed" if all(required) else "Needs review"
    return {
        "filename": filename,
        "vendor": vendor,
        "invoice_number": invoice_no,
        "invoice_date": date,
        "due_date": due_date,
        "subtotal": subtotal,
        "tax_amount": tax,
        "total_amount": total,
        "currency": "INR",
        "status": status,
        "extracted_text": text[:5000],
        "processed_at": datetime.now().isoformat(timespec="seconds"),
    }
