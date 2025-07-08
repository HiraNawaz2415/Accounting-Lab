# pages/2_Accounting_Cycle.py

import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.set_page_config(layout="wide")

# ✅ Custom global style for dark theme
st.markdown(
    """
    <style>
    body {
        background-color: #e6defd;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #8c7773 0%, #f2eefe 100%);
    }
    .stApp {
        background-color: #ffffff;
    }
    .stApp, .stApp * {
        color: #533d38;
    }
    div[data-testid="metric-container"] {
        background: rgba(93, 64, 55, 0.05);
        border-radius: 8px;
        padding: 10px;
    }
    div.stButton > button {
        background-color: #8c7773;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5em 1em;
    }
    div.stButton > button:hover {
        background-color: #735c58;
    }
    textarea {
        background-color: #8c7773 !important;
        color: white !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #8c7773 !important;
        color: white !important;
    }
    div[data-baseweb="select"] span {
        color: white !important;
    }
    section[data-testid="stTextArea"] textarea {
        background-color: #8c7773 !important;
        color: #ffffff !important;
    }
    section[data-testid="stTextArea"] textarea::placeholder {
        color: #ffffff !important;
    }
    div[data-baseweb="select"] input {
        color: #ffffff !important;
    }
    /* Data editor dark style */
    [data-testid="stDataEditorContainer"] {
        background-color: #8c7773 !important;
        color: white !important;
    }
    [data-testid="stDataEditorContainer"] .cell {
        background-color: #8c7773 !important;
        color: white !important;
    }
    [data-testid="stDataEditorContainer"] .col-header {
        background-color: #8c7773 !important;
        color: white !important;
    }
    [data-testid="stDataEditorContainer"] input {
        background-color: #8c7773 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔄 Accounting Cycle — Journal, Ledger, ATB, Reports")

st.markdown("""
This page covers:  
✅ Journalize → ✅ Ledger → ✅ Adjusted TB → ✅ Income Statement → ✅ Balance Sheet → ✅ PDF Export
""")

# ✅ 1️⃣ Journal Entries
st.header("1️⃣ Journal Entries")
st.info("👇 Using simple sample transactions. You can edit them!")

sample_data = [
    {"Date": "2025-01-01", "Account": "Cash", "Debit": 5000, "Credit": 0},
    {"Date": "2025-01-01", "Account": "Owner's Capital", "Debit": 0, "Credit": 5000},
    {"Date": "2025-01-05", "Account": "Supplies", "Debit": 1200, "Credit": 0},
    {"Date": "2025-01-05", "Account": "Cash", "Debit": 0, "Credit": 1200},
    {"Date": "2025-01-10", "Account": "Revenue", "Debit": 0, "Credit": 2500},
    {"Date": "2025-01-10", "Account": "Cash", "Debit": 2500, "Credit": 0},
    {"Date": "2025-01-15", "Account": "Rent Expense", "Debit": 800, "Credit": 0},
    {"Date": "2025-01-15", "Account": "Cash", "Debit": 0, "Credit": 800},
]

journal_df = pd.DataFrame(sample_data)
edited_journal = st.data_editor(journal_df, use_container_width=True, num_rows="dynamic")

# ✅ Unified table style helper
def style_df(df):
    return df.style.set_properties(**{
        'background-color': '#8c7773',
        'color': 'white'
    }).set_table_styles(
        [{'selector': 'th',
          'props': [('background-color', '#8c7773'),
                    ('color', 'white')]}]
    )

# ✅ 2️⃣ Ledger
st.header("2️⃣ Ledger Accounts")
ledger = edited_journal.groupby("Account").agg({"Debit": "sum", "Credit": "sum"}).reset_index()
ledger["Balance"] = ledger["Debit"] - ledger["Credit"]
st.markdown(style_df(ledger).to_html(), unsafe_allow_html=True)

# ✅ 3️⃣ Adjusted Trial Balance
st.header("3️⃣ Adjusted Trial Balance")
atb = ledger.copy()
atb["DR"] = atb["Balance"].apply(lambda x: x if x > 0 else 0)
atb["CR"] = atb["Balance"].apply(lambda x: -x if x < 0 else 0)
atb = atb[["Account", "DR", "CR"]]
st.markdown(style_df(atb).to_html(), unsafe_allow_html=True)

# ✅ 4️⃣ Income Statement
st.header("4️⃣ Income Statement")
revenue_accounts = ["Revenue"]
expense_accounts = ["Rent Expense", "Supplies Expense"]
supplies_row = atb[atb["Account"] == "Supplies"]
if not supplies_row.empty:
    supplies_used = supplies_row["DR"].values[0]
    if supplies_used > 0:
        expense_accounts.append("Supplies")

total_revenue = atb[atb["Account"].isin(revenue_accounts)]["CR"].sum()
total_expenses = atb[atb["Account"].isin(expense_accounts)]["DR"].sum()
net_income = total_revenue - total_expenses

is_df = pd.DataFrame([
    ["Total Revenue", total_revenue],
    ["Total Expenses", total_expenses],
    ["Net Income", net_income]
], columns=["Description", "Amount"])

st.markdown(style_df(is_df).to_html(), unsafe_allow_html=True)

# ✅ 5️⃣ Balance Sheet
st.header("5️⃣ Balance Sheet")
assets = ["Cash", "Supplies"]
liabilities = ["Accounts Payable"]
equity = ["Owner's Capital"]

total_assets = atb[atb["Account"].isin(assets)]["DR"].sum()
total_liabilities = atb[atb["Account"].isin(liabilities)]["CR"].sum()
total_equity = atb[atb["Account"].isin(equity)]["CR"].sum() + net_income

bs_df = pd.DataFrame([
    ["Total Assets", total_assets],
    ["Total Liabilities", total_liabilities],
    ["Owner's Equity", total_equity],
    ["Liabilities + Equity", total_liabilities + total_equity]
], columns=["Description", "Amount"])

st.markdown(style_df(bs_df).to_html(), unsafe_allow_html=True)

# ✅ 6️⃣ PDF Export
st.header("6️⃣ Export PDF")
if st.button("Generate PDF Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Accounting Cycle Report", ln=True, align="C")

    pdf.cell(200, 10, txt="", ln=True)
    pdf.cell(200, 10, txt="Income Statement", ln=True)
    for _, row in is_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Description']}: ${row['Amount']:.2f}", ln=True)

    pdf.cell(200, 10, txt="", ln=True)
    pdf.cell(200, 10, txt="Balance Sheet", ln=True)
    for _, row in bs_df.iterrows():
        pdf.cell(200, 10, txt=f"{row['Description']}: ${row['Amount']:.2f}", ln=True)

    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    st.download_button(
        "📥 Download PDF",
        pdf_output,
        "accounting_cycle_report.pdf",
        "application/pdf"
    )
