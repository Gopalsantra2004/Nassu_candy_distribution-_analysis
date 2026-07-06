# Nassau Candy Distributor — Shipping Route Efficiency Analysis

Factory-to-customer shipping route efficiency analysis and interactive dashboard,
built for Nassau Candy Distributor as part of the Unified Mentor program.

## Problem Statement

Nassau Candy Distributor ships products from five factories to customers across
four U.S. regions, but lacks route-level visibility into:
- Which factory-to-customer routes are consistently efficient vs. delay-prone
- How shipping performance varies by region, state, and ship mode
- Where geographic bottlenecks exist

This project turns raw order/shipment data into route-level operational
intelligence to support data-driven logistics decisions.

## Repository Contents

| File | Description |
|---|---|
| `Nassau_Candy_Route_Efficiency_Analysis.ipynb` | Full EDA notebook: cleaning, feature engineering, route benchmarking, bottleneck analysis, KPIs |
| `app.py` | Streamlit dashboard (4 modules, live filters) |
| `Nassau_Candy_Distributor.csv` | Raw source dataset |
| `cleaned_shipments.csv` | Cleaned dataset exported by the notebook |
| `executive_summary.txt` | Auto-generated stakeholder summary |
| `requirements.txt` | Python dependencies |

## Methodology

1. **Data Cleaning** — parsed dates, removed duplicates and negative lead times, standardized geographic/categorical fields
2. **Feature Engineering** — mapped each product to its source factory, built `Factory → State` / `Factory → Region` route keys, classified ship modes into Standard vs. Expedited
3. **Route Aggregation** — shipment volume, average lead time, and lead-time variability per route
4. **Efficiency Benchmarking** — ranked routes with a composite Route Efficiency Score (70% speed, 30% reliability); identified Top 10 / Bottom 10 routes
5. **Geographic Bottleneck Analysis** — flagged states with simultaneously high volume and high lead time
6. **Ship Mode Analysis** — compared lead time, cost, and profit across shipping methods

## Key Findings

- **10,194 shipments** analyzed across **196 factory-to-state routes**, 5 factories, and 4 regions
- Overall average lead time: **1,320.8 days** (median 1,274 days); overall delay frequency: **21.1%** (shipments above the 75th percentile threshold)
- **Most efficient route:** Secret Factory → Virginia (avg. 1,053 days, Efficiency Score 100)
- **Least efficient route:** Lot's O' Nuts → North Dakota (avg. 1,638 days, Efficiency Score 18)
- **Standard Class** is the fastest ship mode on average (1,314 days); **First Class** is the slowest (1,338 days) — a reminder that ship mode "class" name doesn't guarantee speed in this data
- **18 states** flagged as volume/lead-time bottlenecks, led by **California, New York, Pennsylvania, Washington, and Illinois** — all high-volume states with above-median lead times
- **Chocolate** is the dominant product division (9,844 of 10,194 shipments); **Pacific** is the highest-volume region

> **Data quality caveat:** `Order Date` values fall in 2024–2025 while `Ship Date`
> values fall in 2026–2030, producing implausibly large absolute lead times.
> This looks like a date export issue in the source file rather than genuine
> multi-year shipping delays. All findings above should be read as
> **relative/comparative** (which routes/modes/states are faster or slower
> than others) rather than literal day counts, pending validation with the
> source system.

## Dashboard

The Streamlit app provides four modules:
- **Route Efficiency Overview** — leaderboard + efficiency score chart
- **Geographic Shipping Map** — US choropleth + regional bottleneck scatter
- **Ship Mode Comparison** — lead time distribution and cost/profit by mode
- **Route Drill-Down** — state-level KPIs and order-level shipment timeline

Filters: date range, region/state, ship mode, lead-time threshold slider.

## How to Run

```bash
git clone <your-repo-url>
cd <repo-folder>
pip install -r requirements.txt

# Run the notebook first to produce cleaned_shipments.csv (or use the one included)
jupyter notebook Nassau_Candy_Route_Efficiency_Analysis.ipynb

# Then launch the dashboard
streamlit run app.py
```

## Author

Gopal Santra — Unified Mentor Project Submission
