import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

def monetary_policy_tab(df: pd.DataFrame):

    st.title("Monetary Policy (Bank of Korea)")

    df = df.copy()
    df = df.sort_index()

    # ==========================================================
    # SECTION 1: MONETARY POLICY & INFLATION TARGETING
    # ==========================================================
    st.subheader("Monetary Policy & Inflation Targeting")

    st.markdown("""
    **BOK Mandate:** Price stability through inflation targeting.  
    **Target:** 2% CPI inflation (YoY, medium-term).

    The Base Rate is adjusted to anchor inflation expectations and stabilise growth.
    """)

    # --- Base Rate & CPI
    def plot_base_rate_cpi(df):
        plot_ddf = df[["base_rate", "Total item"]].rename(columns={"base_rate": "Base Rate (%)", 
                                                                   "Total item": "CPI Inflation (YoY %)"})
        fig = px.line(plot_ddf, x=plot_ddf.index, y=["Base Rate (%)", "CPI Inflation (YoY %)"],
                    title="Base Rate vs CPI Inflation",
                    labels={"index": "Date", "value": "Value", "variable": "Legend"})
        fig.add_hline(
            y=2.0, 
            line_dash="dash", 
            line_color="red", 
            annotation_text="BOK Inflation Target (2%)", 
            annotation_position="bottom right"
        )

        st.plotly_chart(fig, use_container_width=True)
    
    plot_base_rate_cpi(df)

    # base rate vs cpi vs real rate metrics
    df = df.copy()
    df = df.sort_index()

    # Levels
    df["real_rate"] = df["base_rate"] - df["Total item"]

    # Changes (MoM)
    df["d_base_rate"] = df["base_rate"].diff()
    df["d_cpi"] = df["Total item"].diff()
    df["d_real_rate"] = df["real_rate"].diff()

    def classify_policy(d_real):
        if d_real > 0.10:
            return "🟥 Hawkish ↑"
        elif d_real < -0.10:
            return "🟩 Dovish ↓"
        else:
            return "⚪ Neutral →"

    df["policy_stance"] = df["d_real_rate"].apply(classify_policy)

    # policy decision table
    policy_moves = df[df["d_base_rate"] != 0][
        [
            "base_rate", "Total item", "real_rate",
            "d_base_rate", "d_cpi", "d_real_rate",
            "policy_stance"
        ]
    ]

    if not policy_moves.empty:
        st.subheader("📌 Monetary Policy Actions & Real Stance")

        display_df = policy_moves.rename(columns={
            "base_rate": "Base Rate (%)",
            "Total item": "CPI (YoY, %)",
            "real_rate": "Real Rate (%)",
            "d_base_rate": "Δ Base Rate",
            "d_cpi": "Δ CPI",
            "d_real_rate": "Δ Real Rate",
            "policy_stance": "Policy Classification"
        })

        st.dataframe(display_df, use_container_width=True)

    # policy metrics (current)
    latest = df.iloc[-1]

    stance = classify_policy(latest["d_real_rate"])

    arrow = "🔺" if latest["d_real_rate"] > 0.10 else "🔻" if latest["d_real_rate"] < -0.10 else "➡️"

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "As of Date",
        latest.name.strftime("%B %Y")
    )

    c2.metric(
        "BOK Base Rate",
        f"{latest['base_rate']:.2f}%",
        f"{latest['d_base_rate']:+.2f} MoM"
    )

    c3.metric(
        "CPI Inflation (YoY)",
        f"{latest['Total item']:.2f}%",
        f"{latest['d_cpi']:+.2f} MoM"
    )

    c4.metric(
        "Real Policy Rate",
        f"{latest['real_rate']:.2f}%",
        f"{latest['d_real_rate']:+.2f} MoM {arrow}"
    )

    c5.metric(
        "Policy Stance",
        stance
    )

    # interpretation
    st.subheader("Policy Interpretation")
    if latest["d_real_rate"] > 0.10:
        st.error("Policy is actively tightening financial conditions to combat inflation.")
    elif latest["d_real_rate"] < -0.10:
        st.success("Policy is easing in real terms, supporting growth and liquidity.")
    else:
        st.info("Policy stance is broadly neutral; inflation dynamics are offsetting rate moves.")

    st.divider()

    # ==========================================================
    # SECTION 2: INFLATION EXPECTATIONS & CREDIBILITY
    # ==========================================================
    st.subheader("Inflation Expectations vs Actual Inflation")

    cols = [
        "Total item",
        "Expectations of Interest Rates",
        "Composite Consumer Sentiment Index",
    ]

    z_df = df[cols].dropna().copy()
    z_df = (z_df - z_df.mean()) / z_df.std()

    st.subheader("Standardised Macro Signals (Z-Score)")
    st.line_chart(z_df)

    st.caption(
        "Policy credibility improves when inflation expectations stabilise despite elevated CPI."
    )

    st.divider()

    # ==========================================================
    # SECTION 3: INFLATION FUNDAMENTALS (CPI TABLE)
    # ==========================================================
    st.subheader("Inflation Breakdown (Latest YoY %)")

    cpi_components = [
        'Alcoholic beverages and tobacco',
        'Clothing and footwear',
        'Communication',
        'Education',
        'Food and non-alcoholic beverages',
        'Furnishings, household equipment and routine household maintenance',
        'Health',
        'Housing, water, electricity and other fuels',
        'Miscellaneous goods and services',
        'Recreation and culture',
        'Restaurants and hotels',
        'Transport'
    ]

    cpi_table = (
        df[cpi_components]
        .iloc[-1]
        .to_frame(name="Inflation (%)")
        .sort_values("Inflation (%)", ascending=False)
    )

    st.dataframe(cpi_table, use_container_width=True)

    st.divider()

    # ==========================================================
    # SECTION 4: GROWTH FUNDAMENTALS (GDP BY SECTOR)
    # ==========================================================
    st.subheader("Growth by Sector (3-Month % Change)")

    gdp_sectors = ['Accommodation and food services', 'Arts, sports and recreation', 
                   'Basic metals', 'Building repair', 'Business support services', 
                   'Chemicals and chemical products', 'Coke and refined petroleum products', 
                   'Communication', 'Computer, electronic and optical products', 'Electrical equipment',
                   'Fabricated metal products', 'Food, beverages products', 'Machinery and equipment', 
                   'Non-metallic mineral products', 'Non-residential building construction', 
                   'Other manufacturing, repair and installation of machinery and equipment', 
                   'Professional, scientific and technical services', 'Publishing, broadcasting, motion picture, video and television programme production, and information service', 
                   'Residential building construction', 'Textile and leather products', 'Transportation equipment', 'Wholesale and retail trade', 
                   'Wood and paper products, printing and reproduction of recorded media', 'Building construction and repair', 'Business activities', 
                   'Civil engineering', 'Cultural and other services', 'Education', 'Electricity', 'Finance and insurance', 'Gas, steam and air conditioning supply', 
                   'Human health and social work', 'Information and communication', 'Manufacturing', 'Public administration, defence and social security', 'Real estate', 
                   'Transportation and storage', 'Water supply, sewerage, waste management and remediation activities', 'Wholesale and retail trade, accommodation and food services', 
                   'Agriculture, forestry and fishing', 'Construction', 'Electricity, gas and water supply', 'Gross domestic product at market prices(GDP)', 'Gross national income(GNI)', 
                   'Mining, quarrying and Manufacturing', 'Net factor income from the rest of the world'
    ]

    gdp_growth = df[gdp_sectors].pct_change(periods=3) * 100

    gdp_growth_table = (
        gdp_growth
        .iloc[-1]
        .to_frame(name="3-Month Growth (%)")
        .sort_values("3-Month Growth (%)", ascending=False)
    )

    st.dataframe(gdp_growth_table, use_container_width=True)

    # ==========================================================
    # SECTION 5: MACRO REGIME SUMMARY
    # ==========================================================
    st.subheader("Macro–Policy Regime Summary")

    latest_gdp_growth = (
        df["Gross domestic product at market prices(GDP)"]
        .pct_change(periods=3)
        .iloc[-1] * 100
    )

    if latest["Total item"] > 3 and latest_gdp_growth < 1:
        st.error("Stagflation risk: Inflation remains high while growth weakens.")
    elif latest["Total item"] < 2 and latest_gdp_growth > 2:
        st.success("Soft landing: Inflation easing with resilient growth.")
    else:
        st.info("Mixed macro signals: Policy trade-offs remain.")

