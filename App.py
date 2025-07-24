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

        gross_revenue = emp_df.drop_duplicates('order')['order_amount'].sum()
        tips = emp_df.drop_duplicates('order')['order_tip_amount'].sum() if 'order_tip_amount' in emp_df.columns else 0
        revenue = gross_revenue - tips

        summary.append({
            "Rep Name": employee,
            "Revenue": revenue,
            "Cases Total": cases_total,
            "Kicker by Item": f"{kicker_by_item:.2f}",
            "Kicker Total": kicker_total,
            "Total Orders": transactions
        })

    return pd.DataFrame(summary)
