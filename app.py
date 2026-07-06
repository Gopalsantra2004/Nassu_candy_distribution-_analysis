import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy - Route Efficiency Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_shipments.csv", parse_dates=["Order Date", "Ship Date"])
    return df

df = load_data()

st.title("\U0001F36C Nassau Candy Distributor \u2014 Shipping Route Efficiency Dashboard")

# ----------------------------- Sidebar filters ------------------------------
st.sidebar.header("Filters")

min_date, max_date = df["Order Date"].min(), df["Order Date"].max()
date_range = st.sidebar.date_input("Order Date range", (min_date, max_date),
                                    min_value=min_date, max_value=max_date)

regions = st.sidebar.multiselect("Region", sorted(df["Region"].unique()),
                                  default=sorted(df["Region"].unique()))
states = st.sidebar.multiselect("State / Province", sorted(df["State/Province"].unique()),
                                 default=[])
ship_modes = st.sidebar.multiselect("Ship Mode", sorted(df["Ship Mode"].unique()),
                                     default=sorted(df["Ship Mode"].unique()))
lead_threshold = st.sidebar.slider(
    "Lead-time threshold (days) - flags shipments above this as delayed",
    int(df["Lead Time (days)"].min()), int(df["Lead Time (days)"].max()),
    int(df["Lead Time (days)"].quantile(0.75))
)

mask = (
    (df["Order Date"] >= pd.to_datetime(date_range[0])) &
    (df["Order Date"] <= pd.to_datetime(date_range[-1])) &
    (df["Region"].isin(regions)) &
    (df["Ship Mode"].isin(ship_modes))
)
if states:
    mask &= df["State/Province"].isin(states)

fdf = df[mask].copy()
fdf["Delayed"] = fdf["Lead Time (days)"] > lead_threshold

# --------------------------------- KPI row ----------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Shipments", f"{len(fdf):,}")
c2.metric("Avg Lead Time (days)", f"{fdf['Lead Time (days)'].mean():.1f}" if len(fdf) else "-")
c3.metric("Delay Frequency", f"{fdf['Delayed'].mean()*100:.1f}%" if len(fdf) else "-")
c4.metric("Distinct Routes", f"{fdf['Route (State)'].nunique():,}")

tab1, tab2, tab3, tab4 = st.tabs([
    "Route Efficiency Overview", "Geographic Shipping Map",
    "Ship Mode Comparison", "Route Drill-Down"
])

# ------------------------- Tab 1: Route Efficiency --------------------------
with tab1:
    st.subheader("Average Lead Time by Route")
    route_summary = (
        fdf.groupby("Route (State)")
        .agg(Total_Shipments=("Order ID", "count"),
             Avg_Lead_Time=("Lead Time (days)", "mean"),
             Delay_Frequency=("Delayed", "mean"))
        .reset_index()
    )
    route_summary = route_summary[route_summary["Total_Shipments"] >= 3]
    if len(route_summary):
        lt = route_summary["Avg_Lead_Time"]
        norm_speed = 1 - (lt - lt.min()) / (lt.max() - lt.min() + 1e-9)
        route_summary["Efficiency Score"] = (
            (0.7 * norm_speed + 0.3 * (1 - route_summary["Delay_Frequency"])) * 100
        ).round(1)
        route_summary = route_summary.sort_values("Efficiency Score", ascending=False)

        st.markdown("**Route Performance Leaderboard**")
        st.dataframe(route_summary, use_container_width=True)

        fig = px.bar(route_summary.head(15), x="Efficiency Score", y="Route (State)",
                     orientation="h", color="Efficiency Score", color_continuous_scale="Greens")
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No routes meet the minimum volume for this filter selection.")

# ------------------------- Tab 2: Geographic Map -----------------------------
with tab2:
    st.subheader("US Heatmap of Shipping Efficiency")
    us_state_abbrev = {
        'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA',
        'Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA',
        'Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
        'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA',
        'Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT',
        'Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM',
        'New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
        'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
        'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT',
        'Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY',
        'District Of Columbia':'DC',
    }
    state_perf = fdf.groupby("State/Province").agg(
        Total_Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (days)", "mean"),
    ).reset_index()
    state_perf["Abbrev"] = state_perf["State/Province"].map(us_state_abbrev)
    fig = px.choropleth(
        state_perf.dropna(subset=["Abbrev"]), locations="Abbrev", locationmode="USA-states",
        scope="usa", color="Avg_Lead_Time", color_continuous_scale="RdYlGn_r",
        hover_name="State/Province", hover_data=["Total_Shipments"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Regional Bottleneck View")
    region_perf = fdf.groupby("Region").agg(
        Total_Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (days)", "mean"),
    ).reset_index()
    fig2 = px.scatter(region_perf, x="Total_Shipments", y="Avg_Lead_Time", size="Total_Shipments",
                       color="Region", hover_name="Region", text="Region")
    st.plotly_chart(fig2, use_container_width=True)

# ------------------------- Tab 3: Ship Mode Comparison -----------------------
with tab3:
    st.subheader("Lead Time by Ship Mode")
    fig = px.box(fdf, x="Ship Mode", y="Lead Time (days)", color="Ship Mode")
    st.plotly_chart(fig, use_container_width=True)

    ship_summary = fdf.groupby("Ship Mode").agg(
        Total_Shipments=("Order ID", "count"),
        Avg_Lead_Time=("Lead Time (days)", "mean"),
        Avg_Cost=("Cost", "mean"),
        Avg_Gross_Profit=("Gross Profit", "mean"),
    ).reset_index()
    st.dataframe(ship_summary, use_container_width=True)

# ------------------------- Tab 4: Route Drill-Down ---------------------------
with tab4:
    st.subheader("State-Level Performance")
    sel_state = st.selectbox("Choose a state", sorted(fdf["State/Province"].unique()))
    state_df = fdf[fdf["State/Province"] == sel_state]

    c1, c2, c3 = st.columns(3)
    c1.metric("Shipments", len(state_df))
    c2.metric("Avg Lead Time", f"{state_df['Lead Time (days)'].mean():.1f} days" if len(state_df) else "-")
    c3.metric("Delay Rate", f"{state_df['Delayed'].mean()*100:.1f}%" if len(state_df) else "-")

    st.markdown("**Order-Level Shipment Timeline**")
    fig = px.scatter(state_df, x="Order Date", y="Lead Time (days)", color="Ship Mode",
                      hover_data=["Order ID", "Factory", "Product Name"])
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        state_df[["Order ID", "Order Date", "Ship Date", "Factory", "Product Name",
                  "Ship Mode", "Lead Time (days)", "Sales", "Gross Profit"]],
        use_container_width=True
    )
