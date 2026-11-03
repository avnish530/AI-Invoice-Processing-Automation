import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from src.extractor import extract_invoice
from src.storage import load_records, save_records, export_csv

ROOT = Path(__file__).parent
INVOICE_DIR = ROOT / "data" / "invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Invoice Processing Automation", page_icon="🧾", layout="wide")
st.title("🧾 AI Invoice Processing Automation")
st.caption("Upload invoices, extract key fields, review results, and export organized records.")

records = load_records()
c1, c2, c3 = st.columns(3)
c1.metric("Invoices processed", len(records))
c2.metric("Total invoice value", f"₹{pd.to_numeric(records.get('total_amount', pd.Series(dtype=float)), errors='coerce').fillna(0).sum():,.2f}")
c3.metric("Needs review", int((records.get("status", pd.Series(dtype=str)) == "Needs review").sum()))

st.subheader("1. Upload invoices")
uploads = st.file_uploader("Choose PDF, PNG, JPG, or JPEG files", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True)

if uploads and st.button("Extract invoice details", type="primary"):
    new_records = []
    progress = st.progress(0)
    for i, uploaded in enumerate(uploads):
        raw = uploaded.getvalue()
        target = INVOICE_DIR / uploaded.name
        # Avoid overwriting a file with the same name.
        if target.exists():
            target = INVOICE_DIR / f"{target.stem}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}{target.suffix}"
        target.write_bytes(raw)
        item = extract_invoice(raw, uploaded.name)
        item["stored_file"] = str(target.relative_to(ROOT))
        new_records.append(item)
        progress.progress((i + 1) / len(uploads))
    existing = load_records()
    combined = pd.concat([existing, pd.DataFrame(new_records)], ignore_index=True)
    save_records(combined)
    st.success(f"Processed {len(new_records)} invoice(s). Review extracted fields below.")

st.subheader("2. Review and correct extracted records")
records = load_records()
if records.empty:
    st.info("No invoices yet. Upload an invoice to get started. You can also try the sample invoice in the project folder.")
else:
    editable = st.data_editor(records, use_container_width=True, num_rows="dynamic", key="invoice_editor")
    if st.button("Save reviewed records"):
        save_records(editable)
        st.success("Records saved.")

    st.subheader("3. Reports")
    saved = load_records()
    amount = pd.to_numeric(saved.get("total_amount", pd.Series(dtype=float)), errors="coerce").fillna(0)
    left, right = st.columns(2)
    with left:
        st.write("**Invoice totals by vendor**")
        if "vendor" in saved.columns:
            chart = saved.assign(total_amount=amount).groupby("vendor", dropna=False)["total_amount"].sum()
            st.bar_chart(chart)
    with right:
        st.write("**Monthly invoice totals**")
        if "invoice_date" in saved.columns:
            dates = pd.to_datetime(saved["invoice_date"], errors="coerce")
            monthly = pd.DataFrame({"month": dates.dt.to_period("M").astype(str), "amount": amount})
            monthly = monthly[monthly["month"] != "NaT"].groupby("month")["amount"].sum()
            st.line_chart(monthly)

    csv_data = export_csv(saved)
    st.download_button("Download CSV report", csv_data, file_name="invoice_report.csv", mime="text/csv")
    st.download_button("Download JSON records", saved.to_json(orient="records", indent=2), file_name="invoice_records.json", mime="application/json")

st.divider()
st.caption("Privacy note: files and extracted records are stored locally in this project folder. Review all extracted values before using them for accounting or payment.")
