# main.py
import streamlit as st

st.set_page_config(page_title="Financial Accounting Lab", layout="wide")

# Set custom style for background and sidebar
st.markdown(
    """
    <style>
    body {
        background-color: #e6defd;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #8c7773 0%, #f2eefe 100%);
    }
     
    /* Main content area: white */
    .stApp {
        background-color: #ffffff;
    }
      /* Main text: dark brown */
    .stApp, .stApp * {
        color:#533d38;
    }

    /* Metric container styling */
    div[data-testid="metric-container"] {
        background: rgba(93, 64, 55, 0.05);
        border-radius: 8px;
        padding: 10px;
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
    </style>
    """,
    unsafe_allow_html=True
)
st.title("📚 Practical Financial Accounting Lab")

st.markdown("""
This app helps you learn **Financial Accounting** by **practicing real concepts**:

- 📄 **Financial Statements Generator**
- 🔄 **Accounting Cycle** (with 10-Column Worksheet)
- 🧮 **Depreciation Methods**
- 📦 **Inventory Systems**

Use the sidebar to navigate!
""")
