from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="RetailPulse | Retail Analytics", page_icon="RP", layout="wide")

@st.cache_data
def make_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    products = [
        ("Wireless Earbuds", "Electronics", 2499, 1450),
        ("Bluetooth Speaker", "Electronics", 3299, 2050),
        ("Smart Watch", "Electronics", 5999, 3900),
        ("Laptop Stand", "Electronics", 1499, 760),
        ("Bedsheet Set", "Home", 1899, 950),
        ("Table Lamp", "Home", 1299, 620),
        ("Cookware Set", "Home", 3499, 2200),
        ("Cotton T-Shirt", "Fashion", 699, 280),
        ("Running Shoes", "Fashion", 2799, 1550),
        ("Backpack", "Fashion", 1599, 820),
        ("Face Serum", "Beauty", 899, 340),
        ("Skincare Kit", "Beauty", 1699, 760),
        ("Yoga Mat", "Sports", 999, 420),
        ("Water Bottle", "Sports", 599, 190),
    ]
    n = 3000
    chosen = rng.integers(0, len(products), size=n)
    prod = [products[i] for i in chosen]
    dates = pd.to_datetime(rng.choice(pd.date_range("2024-01-01", "2025-12-31"), n))
    qty = rng.choice([1, 2, 3, 4, 5], n, p=[.62, .23, .09, .04, .02])
    discount = np.clip(rng.beta(1.5, 8, n) * .55, 0, .35).round(3)
    status = rng.choice(["Delivered", "Returned", "Cancelled", "Pending"], n, p=[.89, .045, .04, .025])
    df = pd.DataFrame({
        "order_id": [f"ORD{i:05d}" for i in range(1, n + 1)],
        "order_date": dates,
        "customer_id": rng.choice([f"C{i:04d}" for i in range(1, 651)], n),
        "product_name": [p[0] for p in prod],
        "category": [p[1] for p in prod],
        "region": rng.choice(["North", "South", "East", "West", "Central"], n),
        "quantity": qty,
        "unit_price": [p[2] for p in prod],
        "unit_cost": [p[3] for p in prod],
        "discount_pct": discount,
        "order_status": status,
        "payment_method": rng.choice(["UPI", "Credit Card", "Debit Card", "Cash on Delivery"], n),
    })
    df["gross_sales"] = df["quantity"] * df["unit_price"]
    df["net_sales"] = df["gross_sales"] * (1 - df["discount_pct"])
    delivered = df["order_status"].eq("Delivered")
    df["revenue"] = df["net_sales"].where(delivered, 0.0)
    df["profit"] = (df["net_sales"] - df["quantity"] * df["unit_cost"]).where(delivered, 0.0)
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df

st.markdown("""
<style>
.block-container {padding-top: 2rem; padding-bottom: 2rem;}
.hero {padding: 24px; border-radius: 16px; background: linear-gradient(115deg, rgba(38,91,150,.18), rgba(20,150,125,.12)); border: 1px solid rgba(120,120,120,.2);}
</style>
<div class="hero">
<p style="letter-spacing:2px">RETAIL INTELLIGENCE WORKSPACE</p>
<h1>RetailPulse</h1>
<p>Explore sales, profitability, product performance and customer behaviour.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("RetailPulse")
    uploaded = st.file_uploader("Upload your own order CSV", type=["csv"])
    st.caption("Filters")
try:
    if uploaded is not None:
        df = pd.read_csv(uploaded, parse_dates=["order_date"])
        required = {"order_id","order_date","customer_id","product_name","category","region","quantity","unit_price","unit_cost","discount_pct","order_status"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
        df["gross_sales"] = df["quantity"] * df["unit_price"]
        df["net_sales"] = df["gross_sales"] * (1 - df["discount_pct"])
        delivered = df["order_status"].eq("Delivered")
        df["revenue"] = df["net_sales"].where(delivered, 0.0)
        df["profit"] = (df["net_sales"] - df["quantity"] * df["unit_cost"]).where(delivered, 0.0)
        df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
        source = "Uploaded CSV"
    else:
        df = make_data()
        source = "3,000 generated synthetic order rows"
except Exception as exc:
    st.error(f"Could not read this dataset: {exc}")
    st.stop()

with st.sidebar:
    date_range = st.date_input("Order date range", (df.order_date.min().date(), df.order_date.max().date()))
    cats = sorted(df.category.dropna().unique())
    regs = sorted(df.region.dropna().unique())
    selected_cats = st.multiselect("Category", cats, default=cats)
    selected_regs = st.multiselect("Region", regs, default=regs)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
else:
    start = end = date_range

view = df[df.order_date.dt.date.between(start, end) & df.category.isin(selected_cats) & df.region.isin(selected_regs)].copy()
if view.empty:
    st.warning("No records match these filters.")
    st.stop()

delivered = view[view.order_status.eq("Delivered")]
revenue = delivered.revenue.sum()
profit = delivered.profit.sum()
orders = len(view)
delivered_orders = len(delivered)
customers = delivered.customer_id.nunique()
aov = revenue / delivered_orders if delivered_orders else 0
margin = profit / revenue * 100 if revenue else 0
st.caption(f"Data: {source} · Financial KPIs include Delivered orders only.")
k = st.columns(5)
k[0].metric("Total Orders", f"{orders:,}")
k[1].metric("Delivered Orders", f"{delivered_orders:,}")
k[2].metric("Recognised Revenue", f"₹{revenue:,.0f}")
k[3].metric("Gross Profit", f"₹{profit:,.0f}")
k[4].metric("Average Order Value", f"₹{aov:,.0f}")

st.subheader("Sales performance")
left, right = st.columns([1.6, 1])
monthly = delivered.groupby("month", as_index=False).agg(revenue=("revenue","sum"), profit=("profit","sum"))
with left:
    long = monthly.melt(id_vars="month", var_name="metric", value_name="amount")
    fig = px.line(long, x="month", y="amount", color="metric", markers=True, title="Monthly Revenue & Profit")
    fig.update_layout(xaxis_title="Month", yaxis_title="INR", legend_title="")
    st.plotly_chart(fig, use_container_width=True)
with right:
    status = view.order_status.value_counts().rename_axis("status").reset_index(name="orders")
    st.plotly_chart(px.pie(status, names="status", values="orders", hole=.55, title="Order Status Mix"), use_container_width=True)

st.subheader("Product and regional performance")
left, right = st.columns(2)
with left:
    by_cat = delivered.groupby("category", as_index=False).agg(revenue=("revenue","sum"), profit=("profit","sum")).sort_values("revenue", ascending=False)
    st.plotly_chart(px.bar(by_cat, x="category", y="revenue", color="profit", title="Revenue by Category"), use_container_width=True)
with right:
    by_region = delivered.groupby("region", as_index=False).revenue.sum().sort_values("revenue")
    st.plotly_chart(px.bar(by_region, x="revenue", y="region", orientation="h", title="Revenue by Region"), use_container_width=True)

left, right = st.columns(2)
with left:
    top = delivered.groupby("product_name", as_index=False).agg(revenue=("revenue","sum"), units=("quantity","sum")).nlargest(10, "revenue")
    st.plotly_chart(px.bar(top.sort_values("revenue"), x="revenue", y="product_name", orientation="h", title="Top 10 Products"), use_container_width=True)
with right:
    freq = delivered.groupby("customer_id").order_id.nunique()
    mix = pd.DataFrame({"Customer Type":["One-time","Repeat"], "Customers":[int((freq==1).sum()), int((freq>1).sum())]})
    st.plotly_chart(px.pie(mix, names="Customer Type", values="Customers", hole=.55, title="Customer Purchase Frequency"), use_container_width=True)

m1, m2, m3 = st.columns(3)
m1.metric("Profit Margin", f"{margin:.1f}%")
m2.metric("Unique Customers", f"{customers:,}")
m3.metric("Return Rate", f"{(view.order_status.eq('Returned').mean()*100):.1f}%")
with st.expander("View filtered transactions"):
    st.dataframe(view.sort_values("order_date", ascending=False), use_container_width=True, hide_index=True)
st.download_button("Download filtered CSV", view.to_csv(index=False).encode("utf-8"), "retailpulse_filtered_orders.csv", "text/csv")
st.caption("RetailPulse portfolio project · Synthetic practice data · Python · Pandas · SQL · Streamlit · Plotly")
