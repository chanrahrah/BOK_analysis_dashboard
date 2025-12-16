import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

from summary import summary_tab
from monetary_policy import monetary_policy_tab
from fiscal_n_debt import render_debt_stability_tab
# ----------------------------------
# Page configuration
# ----------------------------------
st.set_page_config(
    page_title="South Korea Macroeconomic Dashboard",
    layout="wide"
)

st.title("🇰🇷 South Korea Macroeconomic Dashboard (2018–2025)")
st.caption("Macro transmission–based analysis")

# ----------------------------------
# Load data
# ----------------------------------
@st.cache_data
def load_data():
    relative_path = os.path.join(os.pardir, 'data', 'cleaned_full_data.csv')
    file_path = os.path.abspath(relative_path)
    if not os.path.exists(file_path):
        st.error(f"Error: Dataset not found at path: {file_path}")
        st.stop() # Stops the script execution gracefully
    df = pd.read_csv(
        file_path,
        parse_dates=["date"],  
        index_col="date"      
    )
    df = df.set_index("date").sort_index()
    return df

df = load_data()

# ----------------------------------
# Sidebar – global controls
# ----------------------------------
st.sidebar.header("Global Controls")

start_date, end_date = st.sidebar.date_input(
    "Date range",
    [df.index.min(), df.index.max()]
)

df = df.loc[start_date:end_date]

transform = st.sidebar.selectbox(
    "Transformation",
    ["Level", "MoM %", "YoY %"]
)

rolling_window = st.sidebar.slider(
    "Rolling correlation window (months)",
    3, 24, 12
)

# ----------------------------------
# Helper functions
# ----------------------------------
def transform_series(s, method):
    if method == "MoM %":
        return s.pct_change() * 100
    elif method == "YoY %":
        return s.pct_change(12) * 100
    return s

def plot_pair(df, x_col, y_col, title):
    s1 = transform_series(df[x_col], transform)
    s2 = transform_series(df[y_col], transform)

    plot_df = pd.concat([s1, s2], axis=1).dropna()
    plot_df.columns = [x_col, y_col]

    col1, col2 = st.columns(2)

    with col1:
        fig_ts = px.line(
            plot_df,
            x=plot_df.index,
            y=plot_df.columns,
            title=title
        )
        st.plotly_chart(fig_ts, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            trendline="ols",
            title="Cross-Indicator Relationship"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    rolling_corr = plot_df[x_col].rolling(rolling_window).corr(plot_df[y_col])

    fig_corr = px.line(
        rolling_corr,
        title=f"{rolling_window}-Month Rolling Correlation"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

# ----------------------------------
# Tabs (Macro Transmission Channels)
# ----------------------------------
tabs = st.tabs([
    "Summary",
    "🟦 Monetary & Inflation",
    "🟩 Fiscal & Debt",
    "🟨 Growth Cycle",
    "🟥 Asset Markets",
    "🟪 External Sector"
])

# ==================================
# Tab 0: Summary
# ==================================
with tabs[0]:
    summary_tab(df)
    
# ==================================
# 🟦 Tab 1: Monetary & Inflation
# ==================================
with tabs[1]:
    monetary_policy_tab(df)

# ==================================
# 🟩 Tab 2: Fiscal & Government Debt
# ==================================
with tabs[2]:
    render_debt_stability_tab(df)   

# # ==================================
# # 🟨 Tab 3: Growth & Business Cycle
# # ==================================
# with tabs[3:
#     st.subheader("Growth & Business Cycle")

#     growth = st.selectbox(
#         "Growth Indicator",
#         [
#             "Gross domestic product at market prices(GDP)",
#             "Gross national income(GNI)"
#         ]
#     )

#     sentiment = st.selectbox(
#         "Sentiment Indicator",
#         ["Composite Consumer Sentiment Index"]
#     )

#     plot_pair(
#         df,
#         growth,
#         sentiment,
#         "Growth vs Consumer Sentiment"
#     )

# # ==================================
# # 🟥 Tab 4: Asset Markets
# # ==================================
# with tabs[4]
#   st.subheader("Asset Markets & Financial Conditions")

#     asset = st.selectbox(
#         "Asset Market Indicator",
#         [
#             "KOSPI_Index(End Of)",
#             "KOSDAQ_Index(End of)",
#             "All Groups",
#             "Apartment"
#         ]
#     )

#     policy = st.selectbox(
#         "Policy / Rate Indicator",
#         ["base_rate"]
#     )

#     plot_pair(
#         df,
#         asset,
#         policy,
#         "Asset Prices vs Monetary Policy"
#     )

# # ==================================
# # 🟪 Tab 5: External Sector
# # ==================================
# with tabs[5]:
#     st.subheader("External Sector & Capital Flows")

#     fx = st.selectbox(
#         "Exchange Rate",
#         ["Won per United States Dollar (Close 15:30)"]
#     )

#     capital = st.selectbox(
#         "Capital Flow / Allocation",
#         ["global_equity", "govt_debt_foreign"]
#     )

#     plot_pair(
#         df,
#         fx,
#         capital,
#         "Exchange Rate & Capital Flows"
#     )
