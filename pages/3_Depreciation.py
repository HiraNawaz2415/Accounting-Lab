# pages/3_Depreciation.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
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
        /* Inputs, text areas, select boxes — white text & dark background */
    input, textarea, select {
        color: #ffffff !important;
        background-color:#8c7773 !important;
    }

    /* Streamlit widgets often use divs inside labels */
    .stTextInput > div > input,
    .stSelectbox > div > div > div {
        color: #ffffff !important;
        background-color: #8c7773!important;
    }

    /* Adjust placeholder text if needed */
    ::placeholder {
        color: #dddddd !important;
        opacity: 1;
    }
      /* ✅ Streamlit button style */
    div.stButton > button {
        background-color: #8c7773;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5em 1em;
    }

    /* Optional: change hover effect */
    div.stButton > button:hover {
        background-color: #735c58; /* darker shade for hover */
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧮 Depreciation Calculator")

method = st.selectbox(
    "Choose Depreciation Method",
    ["Straight-Line", "Double Declining Balance", "Units of Production"]
)

cost = st.number_input("Asset Cost", min_value=0.0, value=10000.0, step=100.0)
salvage = st.number_input("Salvage Value", min_value=0.0, value=1000.0, step=100.0)
useful_life = st.number_input("Useful Life (years)", min_value=1, value=5, step=1)

if method == "Units of Production":
    total_units = st.number_input("Estimated Total Units", min_value=1, value=10000, step=100)
    units_per_year = []
    for i in range(useful_life):
        units = st.number_input(f"Units produced in Year {i+1}", min_value=0, value=2000, step=100)
        units_per_year.append(units)

schedule = []

if st.button("Calculate"):
    if method == "Straight-Line":
        annual_dep = (cost - salvage) / useful_life
        for year in range(1, useful_life + 1):
            schedule.append({"Year": year, "Depreciation": annual_dep})

    elif method == "Double Declining Balance":
        book_value = cost
        rate = 2 / useful_life
        for year in range(1, useful_life + 1):
            dep = book_value * rate
            if book_value - dep < salvage:
                dep = book_value - salvage
            schedule.append({"Year": year, "Depreciation": dep})
            book_value -= dep

    elif method == "Units of Production":
        dep_per_unit = (cost - salvage) / total_units
        for year, units in enumerate(units_per_year, start=1):
            dep = units * dep_per_unit
            schedule.append({"Year": year, "Depreciation": dep})

    df = pd.DataFrame(schedule)
    st.write("### Depreciation Schedule")
    st.dataframe(df, use_container_width=True)

    fig, ax = plt.subplots()
    ax.bar(df["Year"], df["Depreciation"], color='skyblue')
    ax.set_title(f"{method} Depreciation")
    ax.set_xlabel("Year")
    ax.set_ylabel("Depreciation Expense")
    st.pyplot(fig)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Schedule as CSV", csv, "depreciation_schedule.csv", "text/csv")
