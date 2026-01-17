import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

def fiscal_and_debt_tab(DATA):

    st.title("🏛️ Fiscal Policy & Debt Sustainability")

    # ==========================================================
    # SECTION 1: LOAD DATA
    # ==========================================================
    df_fisc = DATA["monthly"]["fiscal_balance"].copy()
    df_house = DATA["monthly"]["cts"].copy()
    df_debt_gdp_monthly = DATA["monthly"]["debt_gdp"].copy()

    df_nps_pct = DATA["yearly"]["nps_percent"].copy()
    df_nps_aum = DATA["yearly"]["nps_aum"].copy()
    df_debt_gdp_year = DATA["yearly"]["debt_gdp"].copy()

    df_debt_house = DATA["quarterly"]["debt_house"].copy()
    df_debt = DATA["quarterly"]["debt"].copy()

    df_fisc = df_fisc.sort_index()
    df_house = df_house.sort_index()
    df_debt_gdp_monthly = df_debt_gdp_monthly.sort_index()
    df_debt_gdp_year = df_debt_gdp_year.sort_index()
    df_debt_house = df_debt_house.sort_index()
    df_nps_pct = df_nps_pct.sort_index()
    df_nps_aum = df_nps_aum.sort_index()

    # ==========================================================
    # SECTION 2: FEATURE ENGINEERING — FISCAL STANCE
    # ==========================================================
    df_fisc["fiscal_impulse"] = (
        df_fisc["Current Expenditure"].diff(12)
        + df_fisc["Capital Expenditure"].diff(12)
        - df_fisc["Total Revenues"].diff(12)
    )

    df_fisc["primary_balance"] = (
        df_fisc["Balance"] + df_fisc["Interest Payments"]
    )

    df_fisc["interest_burden"] = (
        df_fisc["Interest Payments"] / df_fisc["Total Revenues"]
    )

    # ==========================================================
    # SECTION 3: FISCAL STANCE
    # ==========================================================
    st.subheader("Fiscal Stance: Balance vs Impulse")

    st.info(
        "Negative Fiscal Balance indicates a Deficit, Positive Fiscal Balance indicates a Surplus." \
        "Increasing / Positive Fiscal Impulse indicates Expansionary Stance, Decreasing / NegativeFiscal Impulse indicates Contractionary Stance."
    )

    plot_df = df_fisc.rename(columns={
        "Balance": "Fiscal Balance",
        "fiscal_impulse": "Fiscal Impulse"})
    fig = px.line(
        plot_df[["Fiscal Balance", "Fiscal Impulse"]],
        title="Fiscal Balance & Fiscal Impulse (YoY)",
        labels={"value": "KRW Trillion", "index": "Date"}
    )
    
    fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="red",
        )
    
    fig.add_vrect(
        x0="2020-01-01", 
        x1="2022-03-01", 
        fillcolor="gray", 
        opacity=0.1, 
        layer="below", 
        annotation_text="COVID-19 Pandemic", 
        annotation_position="top left"
    )

    st.plotly_chart(fig, use_container_width=True)

    
    latest = df_fisc.iloc[-1]

    stance = (
        "Expansionary" if latest["fiscal_impulse"] > 0
        else "Contractionary"
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Fiscal Balance (KRW Trillion)", f"{latest['Balance']:+,.0f}",
              delta=f"{latest['Balance']:+,.0f}")
    c2.metric("Fiscal Impulse (YoY) (KRW Trillion)", f"{latest['fiscal_impulse']:+,.0f}",
              delta=f"{latest['fiscal_impulse']:+,.0f}")
    c3.metric("Fiscal Stance", stance)

    st.caption(
        """
        Fiscal policy has shifted through clear regimes: neutral fine-tuning pre-2020,
        emergency stimulus during COVID, a short-lived consolidation attempt in 2022,
        followed by stop-go re-expansion from 2023 onward.    

        The latest reading shows Korea is running a persistent fiscal deficit while re-accelerating fiscal support at the margin.
        This reflects a stabilization-oriented but reactive fiscal framework, relying on domestic balance-sheet capacity rather than consolidation.
        The stance supports near-term growth but raises medium-term debt sustainability concerns.
        """
    )

    st.divider()

    # ==========================================================
    # SECTION 2: DEBT SUSTAINABILITY
    # ==========================================================
    st.subheader("Korea Debt Sustainability")

    # Debt
    fig = px.line(
        df_debt,
        title="Net Borrowing / Lending by Sector (Trillion Won) — Quarterly",
        labels={"value": "Trillion Won", "date": "Date"},
        color_discrete_map={
            "Rest of the world": "lightblue"
        }
    )

    fig.update_traces(
        line=dict(dash="dot"),
        selector=dict(name="Rest of the world"),
        showlegend=False
    )

    last_date = df_debt.index[-1]
    last_value = df_debt["Rest of the world"].iloc[-1]

    fig.add_annotation(
        x=last_date,
        y=last_value,
        text="Rest of the world",
        showarrow=False,
        xanchor="left",
        xshift=10,        # Slightly offset text to the right so it doesn't touch the line
        font=dict(color="lightblue")
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="grey",
        annotation_text="Net borrowing (+) vs Net lending (–)"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        """Negative values for the Rest of the World reflect Korea’s net lending position vs foreign economies. 
        As domestic sectors—particularly households and government—absorb financing, excess savings are channeled abroad, 
        resulting in persistent net capital outflows and a structurally negative RoW balance.”"""
    )

    # Debt-to-GDP (yearly)
    df_debt_gdp_year["debt_to_gdp"] = (
        df_debt_gdp_year["Gross External Debt"]
        / df_debt_gdp_year["GDP"]
    ) * 100

    covid_start_val_debt_gdp_y = df_debt_gdp_year.loc["2020-01-01", "debt_to_gdp"]

    col1, col2 = st.columns(2)
    with col1: 
        fig = px.line(
            df_debt_gdp_year["debt_to_gdp"],
            title="Debt(External) -to-GDP Ratio (%) — Yearly",
            labels={"value": "Percent", "date": "Date"},
            color_discrete_sequence=["pink"] 
        )
        fig.add_vrect(
            x0="2020-01-01", 
            x1="2022-03-01", 
            fillcolor="gray", 
            opacity=0.1, 
            layer="below", 
            annotation_text="COVID-19 Pandemic", 
            annotation_position="top left"
        )

        fig.add_hline(
            y=covid_start_val_debt_gdp_y, 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"Pre-COVID Level ({covid_start_val_debt_gdp_y:.1f}%)",
            annotation_position="bottom right"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2: 
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # 1. Add the Household Debt/Income Ratio (Primary Y-axis)
        fig.add_trace(
            go.Scatter(
                x=df_debt_house.index, 
                y=df_debt_house["Household and NPISHs Credit to GDP ratio(Core debt)"], 
                name="Debt-to-GDP Ratio (%)",
                line_color='blue'
            ),
            secondary_y=False,
        )
        
        # 2. Add the Household Debt (Trillion Won) (Secondary Y-axis)
        fig.add_trace(
            go.Scatter(
                x=df_debt_house.index, 
                y=df_debt_house["Households and NPISHs"], 
                name="Household Debt (Trn KRW)",
                line_color='orange',
                 line=dict(width=1.5, dash="dot"),
            ),
            secondary_y=True,
        )
        
        # Add figure title and adjust layout
        fig.update_layout(
            title_text="Dual Axis: Household Debt / Income (%) vs. Total Household Debt (Trillion Won) (Quarterly)",
            margin=dict(t=100, l=40, r=40, b=30), 
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        fig.add_vrect(
            x0="2020-01-01", 
            x1="2022-03-01", 
            fillcolor="gray", 
            opacity=0.1, 
            layer="below", 
            annotation_text="COVID-19 Pandemic", 
            annotation_position="top left"
        )
        
        # Set y-axes titles
        fig.update_yaxes(title_text="Debt-to-GDP Ratio (%)", secondary_y=False)
        fig.update_yaxes(title_text="Total Household Debt (Trn KRW)", secondary_y=True)
        
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        """
        **Debt-to-GDP** measures long-term solvency, the ability to meet its long-term financial obligations.
        A rising ratio indicates increasing leverage and potential vulnerability to shocks.
        """
    )
    st.caption(
        """
    External debt-to-GDP rose sharply during COVID-19 as emergency fiscal support, global liquidity easing,
    and weaker nominal GDP increased reliance on external financing. Since 2022, the ratio has gradually
    declined, reflecting post-pandemic normalization, tighter financial conditions, and improved growth,
    though leverage remains above pre-COVID levels.

    Household debt-to-income surged during the pandemic amid ultra-low interest rates and strong credit
    growth, particularly in housing. In the post-COVID period, monetary tightening and macroprudential
    measures have started to reduce household leverage, but elevated debt levels continue to pose
    downside risks to consumption during economic slowdowns.
        """
    )

    st.divider()


