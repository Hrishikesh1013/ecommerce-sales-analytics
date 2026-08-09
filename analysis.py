"""
analysis.py
End-to-end cleaning + exploratory analysis of the raw e-commerce
order data, producing:
  - a cleaned CSV (data/ecommerce_orders_clean.csv)
  - a short text summary of cleaning steps + key insights
  - chart images saved to visuals/
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

RAW_PATH = "/home/claude/portfolio-project/data/ecommerce_orders_raw.csv"
CLEAN_PATH = "/home/claude/portfolio-project/data/ecommerce_orders_clean.csv"
VIS_DIR = "/home/claude/portfolio-project/visuals"
LOG_PATH = "/home/claude/portfolio-project/data/cleaning_log.txt"

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

df = pd.read_csv(RAW_PATH)
log(f"Raw rows loaded: {len(df)}")

# ---------- CLEANING ----------

# 1. Drop exact duplicate rows
before = len(df)
df = df.drop_duplicates()
log(f"Removed {before - len(df)} duplicate rows")

# 2. Standardize text casing
df["region"] = df["region"].str.strip().str.title()
df["payment_method"] = df["payment_method"].str.strip().str.title()
log("Standardized casing for 'region' and 'payment_method'")

# 3. Fix invalid quantities (negative -> treat as data entry error, drop)
before = len(df)
df = df[df["quantity"] > 0]
log(f"Removed {before - len(df)} rows with invalid (negative) quantity")

# 4. Handle price outliers using IQR method
q1, q3 = df["unit_price"].quantile([0.25, 0.75])
iqr = q3 - q1
upper_bound = q3 + 3 * iqr
outliers = df[df["unit_price"] > upper_bound]
log(f"Flagged {len(outliers)} unit_price outliers above {upper_bound:.2f} (likely entry errors) and capped them")
df["unit_price"] = np.where(df["unit_price"] > upper_bound, upper_bound, df["unit_price"])
df["revenue"] = (df["unit_price"] * df["quantity"]).round(2)

# 5. Handle missing values
missing_before = df.isna().sum()
log("Missing values before imputation:\n" + missing_before[missing_before > 0].to_string())

df["region"] = df["region"].fillna("Unknown")
df["customer_age"] = df["customer_age"].fillna(df["customer_age"].median())
df["delivery_days"] = df["delivery_days"].fillna(df["delivery_days"].median())
# rating: leave missing as NaN (don't fabricate satisfaction data), but track separately
log("Filled missing 'region' with 'Unknown', 'customer_age' and 'delivery_days' with median")
log("Left 'rating' missing values as-is (excluded from rating aggregates, not imputed)")

# 6. Correct dtypes
df["order_date"] = pd.to_datetime(df["order_date"])
df["customer_age"] = df["customer_age"].astype(int)
df["delivery_days"] = df["delivery_days"].astype(int)

df.to_csv(CLEAN_PATH, index=False)
log(f"\nClean rows saved: {len(df)} -> {CLEAN_PATH}")

# ---------- ANALYSIS + VISUALS ----------

# Revenue by category
rev_cat = df.groupby("product_category")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(8,5))
sns.barplot(x=rev_cat.values, y=rev_cat.index, palette="viridis")
plt.title("Total Revenue by Product Category")
plt.xlabel("Revenue (₹)")
plt.ylabel("")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/revenue_by_category.png", dpi=150)
plt.close()

# Monthly revenue trend
df["month"] = df["order_date"].dt.to_period("M").astype(str)
monthly = df.groupby("month")["revenue"].sum()
plt.figure(figsize=(10,5))
monthly.plot(marker="o", color="#2b6cb0")
plt.title("Monthly Revenue Trend")
plt.ylabel("Revenue (₹)")
plt.xlabel("Month")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/monthly_revenue_trend.png", dpi=150)
plt.close()

# Revenue by region
rev_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
plt.figure(figsize=(7,5))
sns.barplot(x=rev_region.index, y=rev_region.values, palette="crest")
plt.title("Revenue by Region")
plt.ylabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/revenue_by_region.png", dpi=150)
plt.close()

# Top 10 products by revenue
top_products = df.groupby("product_name")["revenue"].sum().sort_values(ascending=False).head(10)
plt.figure(figsize=(8,5))
sns.barplot(x=top_products.values, y=top_products.index, palette="magma")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/top_10_products.png", dpi=150)
plt.close()

# Rating distribution
plt.figure(figsize=(6,5))
sns.countplot(x="rating", data=df.dropna(subset=["rating"]), palette="Blues")
plt.title("Customer Rating Distribution")
plt.xlabel("Rating (1-5)")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/rating_distribution.png", dpi=150)
plt.close()

# Payment method share
plt.figure(figsize=(6,6))
df["payment_method"].value_counts().plot.pie(autopct="%1.1f%%", ylabel="")
plt.title("Orders by Payment Method")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/payment_method_share.png", dpi=150)
plt.close()

# Delivery days vs rating (does faster delivery mean better ratings?)
plt.figure(figsize=(7,5))
sns.boxplot(x="rating", y="delivery_days", data=df.dropna(subset=["rating"]), palette="Set2")
plt.title("Delivery Days vs Customer Rating")
plt.tight_layout()
plt.savefig(f"{VIS_DIR}/delivery_vs_rating.png", dpi=150)
plt.close()

# ---------- KEY INSIGHTS ----------
total_revenue = df["revenue"].sum()
avg_order_value = df["revenue"].mean()
top_category = rev_cat.idxmax()
top_region = rev_region.idxmax()
avg_rating = df["rating"].mean()
low_rating_avg_delivery = df[df["rating"] <= 2]["delivery_days"].mean()
high_rating_avg_delivery = df[df["rating"] >= 4]["delivery_days"].mean()

insights = f"""
KEY INSIGHTS
------------
- Total revenue across {len(df)} orders: ₹{total_revenue:,.2f}
- Average order value: ₹{avg_order_value:,.2f}
- Top-performing category: {top_category} (₹{rev_cat.max():,.2f})
- Top-performing region: {top_region} (₹{rev_region.max():,.2f})
- Average customer rating: {avg_rating:.2f} / 5
- Avg delivery time for low ratings (1-2): {low_rating_avg_delivery:.1f} days
- Avg delivery time for high ratings (4-5): {high_rating_avg_delivery:.1f} days
  -> {"Slower delivery is associated with lower ratings" if (low_rating_avg_delivery - high_rating_avg_delivery) > 0.3 else "No clear delivery-rating relationship found in this data"}
"""
log(insights)

with open(LOG_PATH, "w") as f:
    f.write("\n".join(log_lines))

print("\nAnalysis complete. Charts saved to visuals/, cleaning log saved to data/cleaning_log.txt")
