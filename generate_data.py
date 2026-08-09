"""
generate_data.py
Generates a synthetic but realistic e-commerce order dataset,
intentionally including the kinds of messiness real-world data has:
missing values, duplicate rows, inconsistent text casing, and outliers.
This mimics raw data exported from a sales/order system.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N = 3000

categories = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smartwatch", "Phone Case", "Power Bank"],
    "Fashion": ["Cotton T-Shirt", "Denim Jacket", "Running Shoes", "Leather Wallet", "Sunglasses"],
    "Home & Kitchen": ["Non-stick Pan", "LED Desk Lamp", "Coffee Maker", "Storage Boxes", "Wall Clock"],
    "Beauty": ["Face Serum", "Sunscreen SPF50", "Lip Balm Set", "Hair Dryer", "Makeup Kit"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Cricket Bat", "Football", "Resistance Bands"],
}

regions = ["North", "South", "East", "West", "Central"]
payment_methods = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Cash on Delivery"]

start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 12, 31)
date_range_days = (end_date - start_date).days

rows = []
for i in range(1, N + 1):
    category = np.random.choice(list(categories.keys()), p=[0.28, 0.24, 0.18, 0.15, 0.15])
    product = np.random.choice(categories[category])
    order_date = start_date + timedelta(days=int(np.random.randint(0, date_range_days)))
    price = round(np.random.uniform(150, 6000), 2)
    quantity = np.random.choice([1, 1, 1, 2, 2, 3, 5], p=[0.35, 0.2, 0.15, 0.15, 0.08, 0.05, 0.02])
    customer_age = int(np.random.normal(32, 9))
    customer_age = max(16, min(customer_age, 70))
    delivery_days = int(np.random.choice([1, 2, 3, 4, 5, 6, 7, 10], p=[0.1,0.2,0.25,0.2,0.1,0.07,0.05,0.03]))
    rating = np.random.choice([1,2,3,4,5], p=[0.03,0.05,0.15,0.37,0.40])
    region = np.random.choice(regions)
    payment = np.random.choice(payment_methods, p=[0.35,0.25,0.15,0.15,0.10])

    rows.append({
        "order_id": 1000 + i,
        "customer_id": f"CUST{np.random.randint(1, 900):04d}",
        "order_date": order_date.strftime("%Y-%m-%d"),
        "product_category": category,
        "product_name": product,
        "unit_price": price,
        "quantity": quantity,
        "region": region,
        "payment_method": payment,
        "customer_age": customer_age,
        "delivery_days": delivery_days,
        "rating": rating,
    })

df = pd.DataFrame(rows)
df["revenue"] = (df["unit_price"] * df["quantity"]).round(2)

# ---- Introduce realistic messiness ----

# 1. Missing values in a few columns
for col, frac in [("rating", 0.06), ("customer_age", 0.03), ("region", 0.02), ("delivery_days", 0.02)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

# 2. Inconsistent text casing / whitespace (common in raw exports)
mess_idx = df.sample(frac=0.15, random_state=2).index
df.loc[mess_idx, "region"] = df.loc[mess_idx, "region"].str.lower()
mess_idx2 = df.sample(frac=0.1, random_state=3).index
df.loc[mess_idx2, "payment_method"] = df.loc[mess_idx2, "payment_method"].str.upper()

# 3. A few outlier / bad-data rows
outlier_idx = df.sample(n=8, random_state=4).index
df.loc[outlier_idx, "unit_price"] = df.loc[outlier_idx, "unit_price"] * 50  # data entry errors
df.loc[df.sample(n=5, random_state=5).index, "quantity"] = -1  # invalid negative qty

# 4. Duplicate rows (common when systems re-export)
dupes = df.sample(n=25, random_state=6)
df = pd.concat([df, dupes], ignore_index=True)

# 5. Shuffle rows so it doesn't look artificially generated in order
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("/home/claude/portfolio-project/data/ecommerce_orders_raw.csv", index=False)
print(f"Generated {len(df)} rows -> data/ecommerce_orders_raw.csv")
print(df.head())
