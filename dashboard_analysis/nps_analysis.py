import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

def nps_analysis_tab(DATA):

    st.title("📈 National Pension Service (NPS) Analysis")
    # ==========================================================
    # SECTION 1: NPS — STRUCTURAL BACKSTOP
    # ==========================================================
    st.subheader("National Pension Service (NPS) Allocation")

    df_nps_pct = DATA["yearly"]["nps_percent"].copy()
    df_nps_aum = DATA["yearly"]["nps_aum"].copy()
    df_nps_pct = df_nps_pct.sort_index()
    df_nps_aum = df_nps_aum.sort_index()
    # ---- Allocation ratios
    df_nps_pct["domestic_ratio"] = (
        df_nps_pct["domestic_equity"]
        + df_nps_pct["domestic_fixed_income"]
    )

    df_nps_pct["foreign_ratio"] = (
        df_nps_pct["global_equity"]
        + df_nps_pct["global_fixed_income"]
    )

    st.info( """ 
            The NPS allocation reveals Korea’s long-term capital anchor. 
            A stable domestic allocation supports government bonds and equities, 
            while rising foreign allocation reflects diversification and aging-population 
            dynamics. 
            """ )
    
    fig = px.area(
        df_nps_pct[["domestic_ratio", "foreign_ratio"]],
        title="NPS Domestic vs Foreign Allocation (%)",
        labels={"value": "Allocation Percentage (%)", "index": "Date"}
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The NPS has steadily increased its foreign asset allocation over the years, "
        "diversifying its portfolio beyond domestic markets. "
        "This trend reflects a strategic shift to capture global growth opportunities "
        "and mitigate domestic market risks."
    )
    st.divider()

    st.subheader("NPS Allocation vs Market Performance")

    # ==========================================================
    # LOAD & PREP DATA
    # ==========================================================
    df_market = DATA["monthly"]["nps_market"].copy()

    # --- Market performance metrics
    df_market["KOSPI_Return"] = (
        df_market["KOSPI_Index(End Of)"].pct_change() * 100
    )

    df_market["KTB_10Y_Yield_Change"] = (
        df_market["Yields of Treasury Bonds(10-year)"].diff() * 100
    )

    df_market["KTB_Trading_Value_Change"] = (
        df_market["KTB Trading Value"].pct_change() * 100
    )

    # --- NPS net flows
    df_nps_flow = df_nps_aum.diff()[
        ["domestic_equity", "domestic_fixed_income"]
    ]

    # ==========================================================
    # ALIGN DATA
    # ==========================================================
    df_plot = (
        df_market[
            [
                "KOSPI_Return",
                "KTB_10Y_Yield_Change",
                "KTB_Trading_Value_Change",
            ]
        ]
        .join(df_nps_flow, how="inner")
        .dropna()
    )

    # ==========================================================
    # A. EQUITY MARKET — REBALANCING (LAGGED RESPONSE)
    # ==========================================================
    fig_eq = go.Figure()

    fig_eq.add_trace(
        go.Bar(
            x=df_plot.index,
            y=df_plot["domestic_equity"],
            name="NPS Domestic Equity Net Flow",
            opacity=0.65,
            yaxis="y1",
        )
    )

    fig_eq.add_trace(
        go.Scatter(
            x=df_plot.index,
            y=df_plot["KOSPI_Return"],
            name="KOSPI Monthly Return (%)",
            mode="lines+markers",
            yaxis="y2",
        )
    )

    fig_eq.update_layout(
        title="KOSPI Returns -> NPS Domestic Equity Flows (NPS role as Rebalancing Channel)",
        xaxis_title="Date",
        yaxis=dict(
            title="NPS Net Buying / Selling",
            zeroline=True,
        ),
        yaxis2=dict(
            title="KOSPI Return (%)",
            overlaying="y",
            side="right",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    st.plotly_chart(fig_eq, use_container_width=True)

    st.caption(
        "NPS domestic equity flows tend to react with a lag to prior market (KOSPI) returns, which can be clearly seen in the chart above."
        "Periods of strong KOSPI returns are typically followed by net equity selling, " \
        "while market drawdowns precede renewed NPS buying—consistent with rule-based rebalancing that dampens pro-cyclical volatility rather than return-chasing behavior."
        
    )

    # ==========================================================
    # B. BOND MARKET — PRICE / YIELD CHANNEL
    # ==========================================================
    fig_bond_price = go.Figure()

    fig_bond_price.add_trace(
        go.Bar(
            x=df_plot.index,
            y=df_plot["domestic_fixed_income"],
            name="NPS Domestic Fixed-Income Net Flow",
            opacity=0.65,
            yaxis="y1",
        )
    )

    fig_bond_price.add_trace(
        go.Scatter(
            x=df_plot.index,
            y=df_plot["KTB_10Y_Yield_Change"],
            name="10Y KTB Yield Change (bp)",
            mode="lines+markers",
            yaxis="y2",
        )
    )

    fig_bond_price.update_layout(
        title="10Y KTB Yield Changes -> NPS Domestic Fixed-Income Flows (NPS role in Yield Absorption)",
        xaxis_title="Date",
        yaxis=dict(
            title="NPS Net Buying / Selling",
            zeroline=True,
        ),
        yaxis2=dict(
            title="Yield Change (bp)",
            overlaying="y",
            side="right",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    st.plotly_chart(fig_bond_price, use_container_width=True)

    st.caption(
        "Rises in long-term KTB yields tend to precede increased NPS domestic fixed-income purchases, " \
        "indicating that NPS responds to valuation and yield conditions rather than initiating yield moves. " \
        "This counter-cyclical demand helps absorb duration supply and moderates upward pressure on sovereign yields."
    )

    # ==========================================================
    # C. BOND MARKET — STRESS / LIQUIDITY CHANNEL
    # ==========================================================
    fig_bond_stress = go.Figure()

    fig_bond_stress.add_trace(
        go.Scatter(
            x=df_plot.index,
            y=df_plot["KTB_Trading_Value_Change"],
            name="KTB Trading Value Change (%)",
            mode="lines",
            yaxis="y1",
        )
    )

    fig_bond_stress.add_trace(
        go.Bar(
            x=df_plot.index,
            y=df_plot["domestic_fixed_income"],
            name="NPS Domestic FI Net Flow",
            opacity=0.6,
            yaxis="y2",
        )
    )

    fig_bond_stress.update_layout(
        title="KTB Market Stress -> NPS Domestic Fixed-Income Flows (NPS role as Liquidity Backstop)",
        xaxis_title="Date",
        yaxis=dict(
            title="KTB Trading Value Change (%)",
            zeroline=True,
        ),
        yaxis2=dict(
            title="NPS Net Buying / Selling",
            overlaying="y",
            side="right",
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    st.plotly_chart(fig_bond_stress, use_container_width=True)

    st.caption(
        "Periods of elevated KTB trading activity—an indicator of market stress and liquidity demand—are followed by stronger NPS bond absorption. " \
        "This pattern suggests NPS acts as a structural liquidity backstop, supplying balance-sheet capacity when private market liquidity deteriorates."
    )

    st.success(
        """
        Across asset classes, NPS investment flows systematically respond to market conditions rather than leading them. Equity flows reflect rebalancing to prior returns, 
        while fixed-income allocations rise in response to higher yields and market stress. This behavior positions NPS as a counter-cyclical stabilizer in Korea’s capital markets.
        """
    )
    st.divider()
