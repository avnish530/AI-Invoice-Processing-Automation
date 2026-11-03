# AI Invoice Processing Automation

A beginner-friendly local web app that extracts invoice details from PDFs and images, lets a user review/correct the results, and exports reports.

## Features
- Upload multiple PDF, PNG, JPG, or JPEG invoices.
- Extract vendor, invoice number, invoice date, due date, subtotal, tax, and total.
- Review and edit extracted fields before saving.
- View vendor and monthly totals.
- Export CSV and JSON reports.
- Keep invoice files and records locally.

> This starter uses text extraction and OCR-assisted extraction, not a trained AI model. Invoice layouts vary, so extraction is best-effort and every record should be reviewed before accounting or payment.

## Setup

### 1. Create a virtual environment
```bash
python -m venv .venv
```
Activate it:
- Windows: `.venv\\Scripts\\activate`
- macOS/Linux: `source .venv/bin/activate`

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

For image OCR, install the Tesseract OCR engine separately:
- Windows: install Tesseract and add it to PATH.
- macOS: `brew install tesseract`
- Ubuntu/Debian: `sudo apt-get install tesseract-ocr`

PDFs with selectable text work without Tesseract. Scanned PDFs may need OCR conversion in a future enhancement.

### 3. Run the app
```bash
streamlit run app.py
```
Open the local URL shown in the terminal.

## Project structure
```text
AI_Invoice_Processing_Automation/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── __init__.py
│   ├── extractor.py
│   └── storage.py
├── data/
│   └── invoices/
└── reports/
```

## Suggested next improvements
1. Add OCR for scanned PDF pages.
2. Use an LLM with a strict JSON schema for difficult invoice layouts.
3. Add vendor master data and GSTIN validation.
4. Detect duplicate invoice numbers and flag them for review.
5. Add user login, role-based access, and encrypted storage before deployment.
6. Connect an approval workflow through n8n or email.

## Data and security
The app stores uploaded files and extracted data in the project directory. Do not upload confidential invoices to an external AI service without authorization. Back up the `data/` directory and apply appropriate access controls for real business use.
