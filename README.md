# E-commerce Sales & Customer Analytics

An end-to-end data analysis project: cleaning a messy raw orders export, exploring revenue and customer behavior patterns, and answering business questions using both **Python** and **SQL**.

## Business Questions Answered

- Which product categories and regions drive the most revenue?
- How does revenue trend month over month?
- Who are the highest-value customers?
- Does delivery speed relate to customer satisfaction (rating)?
- Which products are expensive but under-performing on ratings?

## Key Insights

- **Total revenue:** ₹1.28 crore across ~3,000 orders (avg order value ≈ ₹4,284)
- **Top category:** Electronics, followed closely by Fashion
- **Top region:** East
- **Average rating:** 4.04 / 5
- **Delivery speed vs. rating:** no meaningful relationship found in this dataset — a reminder to test assumptions rather than assume them
- Full breakdown in [`data/cleaning_log.txt`](data/cleaning_log.txt)

## Repository Structure

```
├── data/
│   ├── ecommerce_orders_raw.csv      # raw, intentionally messy export
│   ├── ecommerce_orders_clean.csv    # cleaned dataset
│   ├── ecommerce.db                  # SQLite DB of the cleaned data
│   └── cleaning_log.txt              # step-by-step cleaning log + insights
├── notebooks/
│   └── ecommerce_analysis.ipynb      # interactive walkthrough
├── scripts/
│   ├── generate_data.py              # synthetic data generator
│   └── analysis.py                   # cleaning + EDA + chart generation
├── sql/
│   └── queries.sql                   # 7 business-question SQL queries
├── visuals/                          # exported chart images
└── requirements.txt
```

## Data Cleaning Process

The raw data intentionally mimics real-world export issues:

| Issue | Rows affected | Fix |
|---|---|---|
| Exact duplicate rows | 25 | Dropped |
| Inconsistent text casing (`region`, `payment_method`) | ~360 | Standardized to title case |
| Invalid negative quantities | 5 | Dropped as data-entry errors |
| Extreme price outliers | 8 | Capped using the IQR method |
| Missing `region`, `customer_age`, `delivery_days`, `rating` | ~390 total | Categorical → `"Unknown"`; numeric → median; `rating` left as missing rather than fabricated |

Full log: [`data/cleaning_log.txt`](data/cleaning_log.txt)

## Sample Visuals

**Revenue by Category**
![Revenue by category](visuals/revenue_by_category.png)

**Monthly Revenue Trend**
![Monthly revenue trend](visuals/monthly_revenue_trend.png)

## SQL Analysis

`sql/queries.sql` contains 7 queries against the cleaned data (loaded into `data/ecommerce.db`), covering aggregation, `RANK()` window functions, CTEs, and correlated subqueries — e.g., finding high-revenue products with below-average ratings.

## Tech Stack

Python (Pandas, NumPy, Matplotlib, Seaborn) · SQL (SQLite) · Jupyter Notebook

## How to Run

```bash
pip install -r requirements.txt
python scripts/generate_data.py   # generates data/ecommerce_orders_raw.csv
python scripts/analysis.py        # cleans data, saves charts to visuals/
```

Then open `notebooks/ecommerce_analysis.ipynb` to explore interactively, or run the queries in `sql/queries.sql` against `data/ecommerce.db`.

## Note on the Data

This dataset is synthetically generated (see `scripts/generate_data.py`) to closely resemble a real e-commerce orders export, including realistic messiness. It is not real customer data.
