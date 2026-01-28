import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

from data_pipeline.data_cleaning import DATA

from dashboard_analysis.summary import summary_tab
from dashboard_analysis.monetary_policy import monetary_policy_tab
from dashboard_analysis.fiscal_n_debt import fiscal_and_debt_tab
from dashboard_analysis.market_performance import market_performance_tab
from dashboard_analysis.nps_analysis import nps_analysis_tab

# Page configuration
st.set_page_config(
    page_title="South Korea Macroeconomic Dashboard",
    layout="wide"
)

st.title("🇰🇷 South Korea Macroeconomic Dashboard (2018–2025)")
st.caption("Macro transmission–based analysis")

# Load data
@st.cache_data
def load_data():
    return DATA

DATA = load_data()

# Tabs (Macro Transmission Channels)
tabs = st.tabs([
    "🟦 Monetary & Inflation",
    "🟩 Fiscal & Debt",
    "🟧 NPS Analysis",
    "🟨 Market Performance",
    
])
 
## Tab 1: Monetary & Inflation
with tabs[0]:
    monetary_policy_tab(DATA)

## Tab 2: Fiscal & Government Debt
with tabs[1]:
    fiscal_and_debt_tab(DATA)   

## Tab 3: NPS Analysis
with tabs[2]:
    nps_analysis_tab(DATA)

## Tab 4: Market Performance 
with tabs[3]:
    market_performance_tab(DATA)


