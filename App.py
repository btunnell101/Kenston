import streamlit as st
st.set_page_config(page_title="Clover Sales App", page_icon="📊", layout="centered", initial_sidebar_state="collapsed")
st.title("Clover Box-Adjusted Sales Summary")
st.info("Upload a CSV file below. This app is optimized for mobile devices. If you do not see the upload button, please refresh your browser.")

    layout="centered",\
    initial_sidebar_state="collapsed"\
)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- Your data processing function ---
def process_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    # (add your logic here from the process_data function)
    # I'll put your version below for you
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
    HOURS_PER_EVENT = 10

    df['sku'] = df['sku'].astype(str).str.lower().fillna('')
    df['item_name'] = df['item_name'].astype(str).str.lower().fillna('')
    df['employee'] = df['employee'].fillna("Unknown")
    df['order'] = df['order'].fillna("Unknown")
    df['item_net_amount'] = pd.to_numeric(df['item_net_amount'], errors='coerce').fillna(0)
    df['order_amount'] = pd.to_numeric(df['order_amount'], errors='coerce').fillna(0)

    df['is_bundle'] = df.apply(
        lambda row: row['sku'] in BUNDLE_SKUS or any(name in row['item_name'] for name in BUNDLE_NAMES), axis=1
    )
    df['is_promo'] = df.apply(
        lambda row: any(x in row['item_name'] for x in PROMO_KEYWORDS), axis=1
    )

    summary = []
    for employee, emp_df in df.groupby('employee'):
        all_items_count = len(emp_df)
        transactions = emp_df['order'].nunique()
        bundle_items = emp_df['is_bundle'].sum()
        promo_items = emp_df['is_promo'].sum()
        revenue = emp_df.drop_duplicates('order')['order_amount'].sum()
        high_value_orders = emp_df.groupby('order', group_keys=False)[['is_bundle', 'item_net_amount']].apply(
            lambda group: group['is_bundle'].any() and group['item_net_amount'].sum() >= 800
        )
        extra_cases = high_value_orders.sum()
        promo_cases = promo_items / 6
        total_cases = bundle_items + promo_cases + extra_cases
        avg_case_per_tx = round(total_cases / transactions, 2) if transactions > 0 else 0
        rph = revenue / HOURS_PER_EVENT if HOURS_PER_EVENT else 0

        summary.append({
            "Employee": employee,
            "Revenue": revenue,
            "Total Transactions": transactions,
            "All Items": all_items_count,
            "Bundle Items": bundle_items,
            "Promo Items": promo_items,
            "Promo Cases": round(promo_cases, 2),
            "Total Cases": round(total_cases, 2),
            "Avg Case Per Transaction": avg_case_per_tx,
            "RPH": rph
        })

    return pd.DataFrame(summary)

# --- Streamlit App UI ---
st.title("Clover Box-Adjusted Sales Summary")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    st.success("File uploaded successfully!")
    df_summary = process_data(uploaded_file)
    st.dataframe(df_summary)

    st.header("RPH by Employee")
    fig, ax = plt.subplots()
    ax.bar(df_summary['Employee'], df_summary['RPH'], color='skyblue')
    ax.set_ylabel('Revenue per Hour (RPH)')
    ax.set_xlabel('Employee')
    ax.set_title('RPH by Employee')
    plt.xticks(rotation=30, ha='right', fontsize=11)
    for i, v in enumerate(df_summary['RPH']):
        ax.text(i, v + max(df_summary['RPH']) * 0.01, f"${v:,.2f}", ha='center', fontsize=9, fontweight='bold')
    st.pyplot(fig)
