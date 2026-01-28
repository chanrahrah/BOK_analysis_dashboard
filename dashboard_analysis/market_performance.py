import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys

def market_performance_tab(DATA):

    st.title("📈 Market Performance & Asset Pricing")
    # ==========================================================
    # SECTION 1: LOAD & ALIGN DATA
    # ==========================================================
    df_kospi = DATA["monthly"]["kospi"].copy()
    df_rate  = DATA["monthly"]["bok_rate"][["base_rate"]].copy()
    df_fx_monthly = DATA["monthly"]["fx"].copy()

    df_kospi = df_kospi.sort_index()
    df_rate  = df_rate.sort_index()

    # Select FX column
    FX_COL = "Won per United States Dollar (Close 15:30)"

    # ==========================================================
    # SECTION 2: EQUITY MARKET PERFORMANCE
    # ==========================================================
    # Equity markets: KOSPI vs KOSDAQ
    st.subheader("Equity Markets: KOSPI vs KOSDAQ")

    equity_cols = [
        "KOSPI_Index(End Of)",
        "KOSDAQ_Index(End of)",
    ]

    eq_df = df_kospi[equity_cols].dropna()

    eq_returns = eq_df.pct_change(3) * 100
    eq_returns.columns = ["KOSPI 3M Return (%)", "KOSDAQ 3M Return (%)"]

    fig = px.line(
        eq_df,
        title="KOSPI & KOSDAQ Index Levels"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Risk appetite signal
    eq_returns["Risk Appetite (KOSDAQ - KOSPI)"] = (
        eq_returns.iloc[:, 1] - eq_returns.iloc[:, 0]
    )

    fig = px.line(
        eq_returns,
        title="Equity Momentum & Risk Appetite (3M Returns)"
    )
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        opacity=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

    latest_eq = eq_returns.iloc[-1]

    st.caption(
        f"KOSPI 3M Return: {latest_eq['KOSPI 3M Return (%)']:.2f}%, "
        f"KOSDAQ 3M Return: {latest_eq['KOSDAQ 3M Return (%)']:.2f}%. "
        "If KOSDAQ outperforms KOSPI, it signals a risk-on market environment. " \
        "If KOSPI outperforms KOSDAQ, it signals a risk-off market environment. " \
        "While KOSDAQ is more sensitive to growth expectations, KOSPI reflects more defensive "
        "market sentiment."
    )

    if latest_eq["Risk Appetite (KOSDAQ - KOSPI)"] > 0:
        st.success(f"Risk Appetite: {latest_eq['Risk Appetite (KOSDAQ - KOSPI)']:.2f}. \
                   Risk-on regime: Growth equities (KOSDAQ) outperforming.")
    else:
        st.warning(f"Risk Appetite: {latest_eq['Risk Appetite (KOSDAQ - KOSPI)']:.2f}. \
                   Risk-off regime: Defensive equities (KOSPI) outperforming.")

    st.divider()

    # ==========================================================
    # SECTION 3: FX PERFORMANCE (KRW)
    # ==========================================================
    st.subheader("FX Market: KRW vs USD")

    fx_df = df_fx_monthly[[FX_COL]].dropna()
    fx_df.columns = ["KRW/USD"]

    fx_change = fx_df.pct_change(3) * 100

    fig = px.line(
        fx_df,
        title="KRW per USD (Higher = KRW Weakness)",
        color_discrete_sequence=["orange"]
    )

    fig.add_hline(
        y=fx_df["KRW/USD"].iloc[-1],
        annotation_text="Latest KRW/USD",
        annotation_position="top right",
        line_dash="dot",
        line_color="grey",
        opacity=0.4
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "KRW/USD captures Korea’s external balance and sensitivity to global risk conditions. "
        "Sustained KRW depreciation typically reflects USD strength, capital outflows, or "
        "constraints on domestic monetary easing. Conversely, KRW appreciation signals "
        "improving capital flow dynamics and external stability."
    )

    latest_fx = fx_change.iloc[-1, 0]

    if latest_fx > 3:
        st.error("KRW depreciation pressure: external or policy stress.")
    elif latest_fx < -3:
        st.success("KRW appreciation: improved capital flow conditions.")
    else:
        st.info("FX conditions broadly stable.")

    st.divider()

    # ==========================================================
    # SECTION 4: MONETARY CONDITIONS TRANSMISSION
    # ==========================================================
    st.subheader("Policy Rate vs Market Pricing")

    df_policy = (
        df_rate
        .join(eq_df, how="inner")
        .join(fx_df, how="inner")
        .dropna()
    )

    # Ensure numeric
    df_policy["base_rate"] = pd.to_numeric(df_policy["base_rate"], errors="coerce")
    df_policy["KOSPI_Index(End Of)"] = pd.to_numeric(
        df_policy["KOSPI_Index(End Of)"], errors="coerce"
    )

    df_plot = (
        df_policy[["base_rate", "KOSPI_Index(End Of)"]]
        .dropna()
        .reset_index()
    )

    date_col = df_plot.columns[0]

    # Policy direction for regime shading
    df_plot["rate_change"] = df_plot["base_rate"].diff()

    # Base chart: KOSPI (left)
    fig = px.line(
        df_plot,
        x=date_col,
        y="KOSPI_Index(End Of)",
        title="Policy Rate vs Market Pricing: Monetary Transmission to Equity Markets",
        labels={"KOSPI_Index(End Of)": "KOSPI Index"}
    )

    # Policy rate (right axis)
    fig.add_scatter(
        x=df_plot[date_col],
        y=df_plot["base_rate"],
        name="BOK Base Rate (%)",
        yaxis="y2",
        mode="lines+markers"
    )

    fig.update_layout(        
        yaxis=dict(title="KOSPI Index"),
        yaxis2=dict(
            title="Base Rate (%)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        margin=dict(r=120),
        legend=dict(orientation="h", y=1.15)
    )

    fig.update_traces(
        name="KOSPI Index (End-of-Period)",
        selector=dict(type="scatter")
    )

    # Shade tightening regimes
    tightening = df_plot[df_plot["rate_change"] > 0]

    for i in range(len(tightening) - 1):
        fig.add_vrect(
            x0=tightening.iloc[i][date_col],
            x1=tightening.iloc[i + 1][date_col],
            fillcolor="red",
            opacity=0.08,
            layer="below",
            line_width=0
        )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Shaded areas indicate policy tightening cycles. " \
        "During policy tightening cycles (shaded), higher policy rates coincide with shifts in equity market trends, " \
        "reflecting tighter financial conditions transmitted via higher discount rates and reduced risk appetite. " \
        "Equity pricing adjusts over time rather than instantaneously, underscoring the gradual nature of monetary transmission."
    )



