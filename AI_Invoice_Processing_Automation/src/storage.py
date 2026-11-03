from pathlib import Path
import pandas as pd
import io

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "invoices.csv"

COLUMNS = [
    "filename", "vendor", "invoice_number", "invoice_date", "due_date",
    "subtotal", "tax_amount", "total_amount", "currency", "status",
    "stored_file", "extracted_text", "processed_at"
]

def load_records():
    if not CSV_PATH.exists():
        return pd.DataFrame(columns=COLUMNS)
    try:
        df = pd.read_csv(CSV_PATH)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS]
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_records(df):
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.reindex(columns=COLUMNS).to_csv(CSV_PATH, index=False)

def export_csv(df):
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()
