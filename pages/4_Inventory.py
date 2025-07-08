# pages/4_Inventory.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# ------------------------------
# ✅ Custom CSS for background, sidebar, buttons, inputs
# ------------------------------
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
        color:#533d38;
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
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------------------
# ✅ Helper: style_df
# ------------------------------
def style_df(df):
    return df.style.set_properties(**{
        'background-color': '#8c7773',
        'color': 'white'
    }).set_table_styles(
        [{'selector': 'th',
          'props': [('background-color', '#8c7773'),
                    ('color', 'white')]}]
    )

# ------------------------------
# ✅ Title & description
# ------------------------------
st.title("📦 Inventory System — FIFO, LIFO, Weighted Average")

st.markdown("""
Calculate **COGS** & **Ending Inventory**  
using:
- FIFO, LIFO, Weighted Average
- Periodic & Perpetual
- Full **step-by-step flow**
- **Chart**
- **📥 Download Excel**
""")

# ------------------------------
# ✅ User Inputs
# ------------------------------
purchases_input = st.text_area(
    "📋 Purchases (Qty, Cost per Unit) — one per line",
    value="10, 5\n15, 6\n20, 7"
)

sales_input = st.text_area(
    "📋 Sales Quantities — one per line (for Perpetual, order matters)",
    value="20\n10"
)

method = st.selectbox("Inventory Method", ["FIFO", "LIFO", "Weighted Average"])
system = st.selectbox("Inventory System", ["Periodic", "Perpetual"])

# ------------------------------
# ✅ Parse Purchases & Sales
# ------------------------------
purchases_list = []
for line in purchases_input.strip().split("\n"):
    qty, cost = map(float, line.split(","))
    purchases_list.append({"Qty": qty, "Cost": cost})
df_purchases = pd.DataFrame(purchases_list)

sales_qty_list = [float(q) for q in sales_input.strip().split("\n") if q]

# ✅ Show Purchases
st.write("### ✅ Purchases")
st.markdown(style_df(df_purchases).to_html(), unsafe_allow_html=True)

# ✅ Show Sales as styled table
st.write("### ✅ Sales")
df_sales = pd.DataFrame({"Sales Qty": sales_qty_list})
st.markdown(style_df(df_sales).to_html(), unsafe_allow_html=True)


# ------------------------------
# ✅ Calculate
# ------------------------------
if st.button("Calculate COGS & Ending Inventory"):
    if system == "Periodic":
        total_sales = sum(sales_qty_list)
        qty_needed = total_sales

        if method == "FIFO":
            cogs = 0
            layers = []
            for _, row in df_purchases.iterrows():
                if qty_needed == 0:
                    break
                use_qty = min(row["Qty"], qty_needed)
                cogs += use_qty * row["Cost"]
                layers.append({"Qty Used": use_qty, "Cost": row["Cost"], "Total Cost": use_qty * row["Cost"]})
                qty_needed -= use_qty

            ending_inv = 0
            for _, row in df_purchases.iterrows():
                used_qty = sum([l["Qty Used"] for l in layers if l["Cost"] == row["Cost"]])
                remaining_qty = row["Qty"] - used_qty
                if remaining_qty > 0:
                    ending_inv += remaining_qty * row["Cost"]

        elif method == "LIFO":
            cogs = 0
            layers = []
            for _, row in df_purchases[::-1].iterrows():
                if qty_needed == 0:
                    break
                use_qty = min(row["Qty"], qty_needed)
                cogs += use_qty * row["Cost"]
                layers.append({"Qty Used": use_qty, "Cost": row["Cost"], "Total Cost": use_qty * row["Cost"]})
                qty_needed -= use_qty

            ending_inv = 0
            for _, row in df_purchases.iterrows():
                used_qty = sum([l["Qty Used"] for l in layers if l["Cost"] == row["Cost"]])
                remaining_qty = row["Qty"] - used_qty
                if remaining_qty > 0:
                    ending_inv += remaining_qty * row["Cost"]

        elif method == "Weighted Average":
            total_qty = df_purchases["Qty"].sum()
            total_cost = (df_purchases["Qty"] * df_purchases["Cost"]).sum()
            avg_cost = total_cost / total_qty if total_qty else 0
            cogs = total_sales * avg_cost
            ending_inv = (total_qty - total_sales) * avg_cost
            layers = [{
                "Total Qty": total_qty,
                "Avg Cost": avg_cost,
                "Qty Sold": total_sales,
                "COGS": cogs,
                "Ending Inventory": ending_inv
            }]

        st.success(f"📌 Periodic COGS ({method}): ${cogs:.2f}")
        st.info(f"📦 Ending Inventory ({method}): ${ending_inv:.2f}")

        flow_df = pd.DataFrame(layers)

    elif system == "Perpetual":
        layers = df_purchases.copy().to_dict('records')
        cogs = 0
        flow_rows = []

        if method in ["FIFO", "LIFO"]:
            for sale_qty in sales_qty_list:
                qty_needed = sale_qty

                if method == "FIFO":
                    layer_iter = layers
                else:  # LIFO
                    layer_iter = layers[::-1]

                for layer in layer_iter:
                    if qty_needed == 0:
                        break
                    available = layer["Qty"]
                    use_qty = min(available, qty_needed)
                    flow_rows.append({
                        "Sale Qty": use_qty,
                        "Cost": layer["Cost"],
                        "Total Cost": use_qty * layer["Cost"]
                    })
                    cogs += use_qty * layer["Cost"]
                    layer["Qty"] -= use_qty
                    qty_needed -= use_qty

            ending_inv = sum([layer["Qty"] * layer["Cost"] for layer in layers])

        elif method == "Weighted Average":
            running_layers = []
            for purchase in layers:
                running_layers.append(purchase)

            total_qty = sum(p["Qty"] for p in running_layers)
            total_cost = sum(p["Qty"] * p["Cost"] for p in running_layers)

            for sale_qty in sales_qty_list:
                avg_cost = total_cost / total_qty if total_qty else 0
                flow_rows.append({
                    "Sale Qty": sale_qty,
                    "Avg Cost": avg_cost,
                    "COGS for Sale": sale_qty * avg_cost
                })
                cogs += sale_qty * avg_cost
                total_qty -= sale_qty
                total_cost -= sale_qty * avg_cost

            ending_inv = total_qty * avg_cost

        st.success(f"📌 Perpetual COGS ({method}): ${cogs:.2f}")
        st.info(f"📦 Ending Inventory ({method}): ${ending_inv:.2f}")

        flow_df = pd.DataFrame(flow_rows)

    # ✅ Show Step-by-Step Flow styled
    st.write("### 🧾 Step-by-Step Flow")
    st.markdown(style_df(flow_df).to_html(), unsafe_allow_html=True)

    # ✅ Download Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_purchases.to_excel(writer, sheet_name="Purchases", index=False)
        pd.DataFrame({"Sales Qty": sales_qty_list}).to_excel(writer, sheet_name="Sales", index=False)
        flow_df.to_excel(writer, sheet_name="Flow Steps", index=False)

        workbook = writer.book
        for sheet_name in ["Purchases", "Sales", "Flow Steps"]:
            worksheet = writer.sheets[sheet_name]
            header_format = workbook.add_format({'bold': True, 'border': 1})
            columns = (
                flow_df.columns if sheet_name == "Flow Steps"
                else df_purchases.columns if sheet_name == "Purchases"
                else ["Sales Qty"]
            )
            for col_num, value in enumerate(columns):
                worksheet.write(0, col_num, value, header_format)

    st.download_button(
        label="📥 Download Multi-Sheet Excel",
        data=buffer.getvalue(),
        file_name="inventory_multi_sheet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ✅ Chart
    fig, ax = plt.subplots()
    ax.bar(["COGS", "Ending Inventory"], [cogs, ending_inv], color=["red", "green"])
    ax.set_title(f"{system} — {method} — Cost Breakdown")
    st.pyplot(fig)
