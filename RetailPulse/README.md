# RetailPulse — E-commerce Sales & Customer Analytics

RetailPulse is an interactive data analytics portfolio project built with Python, Pandas, NumPy, SQL, Streamlit and Plotly.

## Business problem
A fictional online retailer needs a single view of sales performance, profitability, product/category contribution, regional performance, order outcomes and repeat-purchase behaviour.

## Dashboard
- Total and delivered order counts
- Recognised revenue, gross profit, average order value and profit margin
- Monthly revenue and profit trends
- Order status mix and return rate
- Revenue by category and region
- Top 10 products by revenue
- One-time vs repeat customer mix
- CSV upload, filters and filtered-data export

## Data
The app generates 3,000 deterministic synthetic order records covering 2024–2025 when it starts. This is practice data, not real customer or company data. Do not describe synthetic findings as evidence about a real retailer.

Financial metrics recognise revenue and cost only for Delivered orders. Cancelled, Returned and Pending orders remain in operational counts but contribute zero recognised revenue/profit.

## Run locally
1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Run: python -m venv .venv
4. Activate the environment.
5. Run: pip install -r requirements.txt
6. Run: streamlit run app.py

## Free hosting option
The app can be hosted from a public GitHub repository using Streamlit Community Cloud. Select this project folder's app.py as the app entry point. Check the provider's current terms before publishing.

## SQL
See sql/analysis_queries.sql for example business analysis queries. All values use INR.

## KPI definitions
- Gross sales = quantity × unit price.
- Net sales = gross sales × (1 − discount fraction).
- Recognised revenue = net sales for Delivered orders only.
- Gross profit = recognised revenue − cost of goods sold for Delivered orders.
- AOV = recognised revenue ÷ delivered order count.
- Profit margin = gross profit ÷ recognised revenue × 100.
- Return rate = returned orders ÷ all filtered orders × 100.

## Limitations
This is descriptive analytics over synthetic data. Tax, shipping revenue, refunds, inventory, marketing spend and acquisition cost are not modelled. One order row represents one product line.

## Suggested resume bullet
Built RetailPulse, an interactive retail analytics dashboard using Python, Pandas, SQL, Streamlit and Plotly; analysed 3,000 synthetic order records to monitor revenue, profitability, category/region performance, fulfilment and repeat-purchase patterns.
