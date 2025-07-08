# pages/1_Financial_Statements.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO

st.set_page_config(layout="wide")

# ✅ Global custom theme
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
    .hero {
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 600px;
        margin: 50px auto;
        text-align: center;
        font-size: 18px;
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
    
/* ✅ File uploader outer container */
section[data-testid="stFileUploader"] {
  background-color: #8c7773 !important;
  border-radius: 8px;
  padding: 1rem;
  color: #ffffff !important;
}

/* ✅ File uploader label text */
section[data-testid="stFileUploader"] label {
  color: #ffffff !important;
}

/* ✅ File uploader input button */
section[data-testid="stFileUploader"] button {
  background-color: #ffffff !important;
  color: #8c7773 !important;
  border: none;
  border-radius: 6px;
  padding: 0.5em 1em;
}

/* ✅ Hover effect for the upload button */
section[data-testid="stFileUploader"] button:hover {
  background-color: #f2eefe !important;
  color: #8c7773 !important;
}

/* ✅ Text inside uploader */
section[data-testid="stFileUploader"] div {
  color: #ffffff !important;
}

    </style>
    """,
    unsafe_allow_html=True
)

st.title("📄 Financial Statements Generator")

st.markdown("""
Upload your **Trial Balance** as **CSV** or **Excel**, or use our **built-in sample**!

Your file must have:
- `Account`
- `Type` (Asset, Liability, Equity, Revenue, Expense, Non-Cash)
- `Amount`

This app generates:
✅ Income Statement  
✅ Balance Sheet  
✅ Cash Flow Statement  
✅ Charts & PDF Export
""")

uploaded_file = st.file_uploader("Upload Trial Balance (.csv or .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        tb = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        tb = pd.read_excel(uploaded_file)
    else:
        st.error("❌ Unsupported file type.")
        st.stop()
    st.success("✅ File uploaded successfully!")
else:
    st.info("ℹ️ No file uploaded — using built-in sample data!")
    tb = pd.DataFrame({
        "Account": ["Cash", "Accounts Receivable", "Supplies", "Equipment",
                    "Accounts Payable", "Owner's Capital", "Revenue",
                    "Rent Expense", "Depreciation Expense"],
        "Type": ["Asset", "Asset", "Asset", "Asset",
                 "Liability", "Equity", "Revenue",
                 "Expense", "Non-Cash"],
        "Amount": [5000, 2000, 800, 3000, 1500, 5000, 8000, 2000, 500]
    })

# ✅ Unified style helper
def style_df(df):
    return df.style.set_properties(**{
        'background-color': '#8c7773',
        'color': 'white'
    }).set_table_styles(
        [{'selector': 'th',
          'props': [('background-color', '#8c7773'),
                    ('color', 'white')]}]
    )

st.write("### 📋 Trial Balance")
st.markdown(style_df(tb).to_html(), unsafe_allow_html=True)

# ✅ Income Statement
st.subheader("📑 Income Statement")
revenues = tb[tb["Type"] == "Revenue"]
expenses = tb[tb["Type"] == "Expense"]

total_revenue = revenues["Amount"].sum()
total_expenses = expenses["Amount"].sum()
net_income = total_revenue - total_expenses

income_statement = pd.concat([
    pd.DataFrame({"Description": revenues["Account"], "Amount": revenues["Amount"]}),
    pd.DataFrame({"Description": expenses["Account"], "Amount": -expenses["Amount"]})
])

income_statement.loc["Total Revenue"] = ["Total Revenue", total_revenue]
income_statement.loc["Total Expenses"] = ["Total Expenses", -total_expenses]
income_statement.loc["Net Income"] = ["Net Income", net_income]

st.markdown(style_df(income_statement.reset_index(drop=True)).to_html(), unsafe_allow_html=True)

# ✅ Balance Sheet
st.subheader("📊 Balance Sheet")
assets_df = tb[tb["Type"] == "Asset"].copy()
liabilities_df = tb[tb["Type"] == "Liability"].copy()
equity_df = tb[tb["Type"] == "Equity"].copy()

# Add Net Income to Equity
equity_df = pd.concat([
    equity_df,
    pd.DataFrame({"Account": ["Net Income"], "Amount": [net_income]})
])

total_assets = assets_df["Amount"].sum()
total_liabilities = liabilities_df["Amount"].sum()
total_equity = equity_df["Amount"].sum()

balance_sheet = pd.concat([
    pd.DataFrame({"Section": "Assets", "Account": assets_df["Account"], "Amount": assets_df["Amount"]}),
    pd.DataFrame({"Section": "Liabilities", "Account": liabilities_df["Account"], "Amount": liabilities_df["Amount"]}),
    pd.DataFrame({"Section": "Equity", "Account": equity_df["Account"], "Amount": equity_df["Amount"]})
]).reset_index(drop=True)


st.markdown(style_df(balance_sheet).to_html(), unsafe_allow_html=True)

st.write(f"**Total Assets:** ${total_assets:.2f}")
st.write(f"**Total Liabilities:** ${total_liabilities:.2f}")
st.write(f"**Total Equity:** ${total_equity:.2f}")
st.write(f"**Liabilities + Equity:** ${total_liabilities + total_equity:.2f}")

if abs(total_assets - (total_liabilities + total_equity)) < 1e-2:
    st.success("✅ Balance Sheet balances!")
else:
    st.error("⚠️ Balance Sheet does NOT balance! Double-check your Trial Balance.")

# ✅ Cash Flow
st.subheader("💧 Cash Flow Statement (Indirect)")
non_cash_expenses = tb[tb["Type"] == "Non-Cash"]["Amount"].sum()
changes_in_assets = -assets_df["Amount"].sum()
changes_in_liabilities = liabilities_df["Amount"].sum()
net_cash_from_ops = net_income + non_cash_expenses + changes_in_assets + changes_in_liabilities

cash_flow = pd.DataFrame({
    "Item": ["Net Income", "Non-Cash Expenses", "Changes in Assets", "Changes in Liabilities", "Net Cash from Ops"],
    "Amount": [net_income, non_cash_expenses, changes_in_assets, changes_in_liabilities, net_cash_from_ops]
})

st.markdown(style_df(cash_flow).to_html(), unsafe_allow_html=True)

# ✅ Charts
st.subheader("📈 Visuals")

fig1, ax1 = plt.subplots()
ax1.bar(["Revenue", "Expenses", "Net Income"], [total_revenue, total_expenses, net_income], color=["green", "red", "blue"])
ax1.set_title("Income Statement Summary")
st.pyplot(fig1)

fig2, ax2 = plt.subplots()
ax2.bar(["Assets", "Liabilities", "Equity"], [total_assets, total_liabilities, total_equity], color=["blue", "orange", "green"])
ax2.set_title("Balance Sheet Summary")
st.pyplot(fig2)

# ✅ PDF Export
st.subheader("📥 Export PDF Report")
if st.button("Generate PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Financial Statements Report", ln=True, align="C")
    pdf.cell(200, 10, txt="", ln=True)

    pdf.cell(200, 10, txt="Income Statement", ln=True)
    for _, row in income_statement.iterrows():
        pdf.cell(200, 10, txt=f"{row['Description']}: ${row['Amount']:.2f}", ln=True)

    pdf.cell(200, 10, txt="", ln=True)
    pdf.cell(200, 10, txt="Balance Sheet", ln=True)
    pdf.cell(200, 10, txt=f"Total Assets: ${total_assets:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Liabilities: ${total_liabilities:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Total Equity: ${total_equity:.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Liabilities + Equity: ${total_liabilities + total_equity:.2f}", ln=True)

    pdf.cell(200, 10, txt="", ln=True)
    pdf.cell(200, 10, txt="Cash Flow Statement", ln=True)
    for _, row in cash_flow.iterrows():
        pdf.cell(200, 10, txt=f"{row['Item']}: ${row['Amount']:.2f}", ln=True)

    pdf_output = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_bytes)
    pdf_output.seek(0)

    st.download_button(
        "📥 Download PDF",
        pdf_output,
        "financial_statements.pdf",
        "application/pdf"
    )
