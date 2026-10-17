from datetime import date

import pandas as pd
import requests
import streamlit as st
from pypdf.errors import PdfReadError

from invoice_utils import extract_invoice_details, extract_text


st.set_page_config(
    page_title="InvoiceMate AI",
    page_icon="📄",
    layout="wide",
)

st.title("InvoiceMate AI")
st.subheader("A private, local-first expense organizer")
st.write(
    "Turn invoice and receipt text into editable expense records, "
    "then review totals and export a CSV."
)
st.info(
    "Your document text is sent only to the Ollama service running on "
    "your computer by this app. Expenses stay in this browser session "
    "and are cleared when the session ends. Review every AI-extracted field."
)

if "expenses" not in st.session_state:
    st.session_state.expenses = []

tab_process, tab_dashboard = st.tabs(
    ["Process a document", "Expense dashboard"]
)

with tab_process:
    st.header("Add an invoice or receipt")
    uploaded_file = st.file_uploader(
        "Upload a PDF or text file",
        type=["pdf", "txt"],
        help="PDFs must contain selectable text. Scanned-image OCR is not supported yet.",
    )
    pasted_text = st.text_area(
        "Or paste invoice text",
        placeholder=(
            "Example: ABC Office Supplies, date 2026-10-10, "
            "total INR 850"
        ),
        height=140,
    )

    if st.button("Extract details with local AI", type="primary"):
        if pasted_text.strip():
            document_text = pasted_text
        elif uploaded_file is not None:
            try:
                document_text = extract_text(uploaded_file)
            except (UnicodeDecodeError, PdfReadError, ValueError) as error:
                st.error(f"Could not read this document: {error}")
                document_text = ""
        else:
            document_text = ""

        if document_text.strip():
            try:
                with st.spinner("Ollama is analyzing your document locally..."):
                    st.session_state.draft = extract_invoice_details(
                        document_text
                    )
            except (requests.exceptions.RequestException, ValueError) as error:
                st.error(f"Could not extract invoice details: {error}")
            else:
                st.success("Extraction complete. Review and correct the details.")
        elif uploaded_file is None or not pasted_text.strip():
            st.warning("Upload a document or paste its text first.")

    if "draft" in st.session_state:
        st.subheader("Review extracted details")
        draft = st.session_state.draft
        categories = [
            "Food",
            "Travel",
            "Software",
            "Office Supplies",
            "Utilities",
            "Other",
        ]
        category = draft["category"]
        if category not in categories:
            category = "Other"

        current_amount = draft["amount"]
        if current_amount is None:
            current_amount = 0.0

        with st.form("expense_form"):
            vendor = st.text_input("Vendor", value=draft["vendor"])
            expense_date = st.text_input(
                "Date (YYYY-MM-DD)", value=draft["date"]
            )
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                value=float(current_amount),
                step=10.0,
            )
            selected_category = st.selectbox(
                "Category",
                categories,
                index=categories.index(category),
            )
            description = st.text_input(
                "Description", value=draft["description"]
            )
            submitted = st.form_submit_button("Save expense")

        if submitted:
            if not vendor.strip():
                st.error("Enter a vendor before saving.")
            else:
                try:
                    if expense_date:
                        date.fromisoformat(expense_date)
                except ValueError:
                    st.error("Enter the date in YYYY-MM-DD format.")
                else:
                    st.session_state.expenses.append(
                        {
                            "Vendor": vendor.strip(),
                            "Date": expense_date,
                            "Amount": amount,
                            "Category": selected_category,
                            "Description": description.strip(),
                        }
                    )
                    del st.session_state["draft"]
                    st.success("Expense saved for this session.")
                    st.rerun()

with tab_dashboard:
    st.header("Your expenses")

    if st.session_state.expenses:
        expenses_df = pd.DataFrame(st.session_state.expenses)
        total_amount = expenses_df["Amount"].sum()
        col_count, col_total = st.columns(2)
        col_count.metric("Expenses", len(expenses_df))
        col_total.metric("Total amount", f"{total_amount:,.2f}")

        st.subheader("Saved expenses")
        st.dataframe(expenses_df, use_container_width=True, hide_index=True)

        st.subheader("Spend by category")
        st.bar_chart(expenses_df.groupby("Category")["Amount"].sum())

        st.download_button(
            label="Download expense report (CSV)",
            data=expenses_df.to_csv(index=False).encode("utf-8"),
            file_name="invoicemate_expenses.csv",
            mime="text/csv",
        )

        if st.button("Clear all expenses"):
            st.session_state.expenses = []
            st.rerun()
    else:
        st.info("No expenses saved yet. Process a document to get started.")

with st.sidebar:
    st.header("About InvoiceMate")
    st.write("Built for freelancers and small businesses.")
    st.write("Model: Qwen 2.5 3B through Ollama.")
    st.caption(
        "This app does not call a hosted AI API. Your local Ollama model "
        "must be installed and running. This MVP does not permanently store "
        "expenses."
    )
