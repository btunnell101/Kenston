import streamlit as st
import pandas as pd
import math

st.set_page_config(
    page_title="Clover Sales App",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Clover Box-Adjusted Sales Summary")
st.info("Upload a CSV file below. This app is optimized for mobile devices. If you do not see the upload button, please refresh your browser.")

def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    df.columns = [col.lower().strip() for col in df.columns]

    BUNDLE_SKUS = {
        "chicken_bundle": 1,
        "natural_choice": 1,
        "pork_bundle": 1,
        "prime_bundle": 1,
        "seafood_bundle": 1
    }
    PROMO_KEYWORDS = ["ribeye", "shrimp", "crab"]
    BUNDLE_NAMES = [
        "chicken bundle", "natural choice", "pork bundle",
        "prime bundle", "seafood bundle"
    ]

    df['sku'] = df['sku'].astype(str).str.lower().fillna('')
    df['item_name'] = df['item_name'].astype(str).str.lower().fillna('')
    df['employee'] = df['employee'].fillna("Unknown")
    df['order'] = df['order'].fillna("Unknown")
    df['item_net_amount'] = pd.to_numeric(df['item_net_amount'], errors='coerce').fillna(0)
    df['order_amount'] = pd.to_numeric(df['order_amount'], errors='coerce').fillna(0)

    # New: handle Order_Tot2 logic
    # Make sure to use the exact lowercase column name from your file for 'Order_Tot2'
    if 'order_tot2' in df.columns:
        df['order_tot2'] = pd.to_numeric(df['order_tot2'], errors='coerce').fillna(0)
        df['revenue_amt'] = df.apply(
            lambda row: row['order_tot2'] if row['order_tot2'] != 0 else row['order_amount'], axis=1
        )
    else:
        df['revenue_amt'] = df['order_amount']

    if 'order_tip_amount' in df.columns:
        df['order_tip_amount'] = pd.to_numeric(df['order_tip_amount'], errors='coerce').fillna(0)

    df['is_bundle'] = df.apply(
        lambda row: row['sku'] in BUNDLE_SKUS or any(name in row['item_name'] for name in BUNDLE_NAMES), axis=1
    )
    df['is_promo'] = df.apply(
        lambda row: any(x in row['item_name'] for x in PROMO_KEYWORDS), axis=1
    )

    summary = []
    for employee, emp_df in df.groupby('employee'):
        transactions = emp_df['order'].nunique()
        bundle_items = emp_df['is_bundle'].sum()
        promo_items = emp_df['is_promo'].sum()
        kicker_by_item = round(promo_items / 6, 2)
        kicker_total = round(kicker_by_item * 6)
        high_value_orders = emp_df.groupby('order', group_keys=False)[['is_bundle', 'item_net_amount']].apply(
            lambda group: group['is_bundle'].any() and group['item_net_amount'].sum() >= 800
        )
        extra_cases = high_value_orders.sum()
        cases_total = math.floor(bundle_items + extra_cases + kicker_by_item)

        # Use the new revenue calculation
        gross_revenue = emp_df.drop_duplicates('order')['revenue_amt'].sum()
        revenue = gross_revenue

        summary.append({
            "Rep Name": employee,
            "Revenue": revenue,
            "Cases Total": cases_total,
            "Kicker by Item": f"{kicker_by_item:.2f}",
            "Kicker Total": kicker_total,
            "Total Orders": transactions
        })

    return pd.DataFrame(summary)

def format_currency(val):
    """Format number as currency"""
    return f"${val:,.2f}"

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    st.success("File uploaded successfully!")
    df_summary = process_data(uploaded_file)
    if df_summary.empty:
        st.warning("No data found! Check your CSV column headers. Required: employee, sku, item_name, order, item_net_amount, order_amount, order_tot2, order_tip_amount")
    else:
        # Format Revenue as currency for display
        df_display = df_summary.copy()
        df_display["Revenue"] = df_display["Revenue"].apply(format_currency)
        st.dataframe(df_display, use_container_width=True)

        # Export as CSV (remove currency formatting for export)
        df_export = df_summary.copy()
        csv = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Export as CSV",
            data=csv,
            file_name='clover_sales_summary.csv',
            mime='text/csv'
        )
else:
    st.warning("No file uploaded yet.")
