import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import sys

def monetary_policy_tab(DATA):

    st.title("🏦 Monetary Policy — Bank of Korea")

    # ==========================================================
    # SECTION 1: MANDATE
    # ==========================================================
    st.subheader("Mandate & Policy Framework")

    st.info(
        """
        **Mandate:** Price stability  
        **Framework:** Inflation targeting  
        **Target:** **2% CPI inflation (YoY, medium-term)**
        """
    )

    # ==========================================================
    # SECTION 2: LOAD DATA
    # ==========================================================
    df_rate = DATA["monthly"]["bok_rate"][["base_rate"]]
    df_cpi  = DATA["monthly"]["cpi"][["Total item"]]
    df_exp  = DATA["monthly"]["cts"][
        ["Expectations of Interest Rates"]
    ]

    df = (
        pd.concat([df_rate, df_cpi, df_exp], axis=1, join="inner")
        .sort_index()
    )

    df["real_rate"] = df["base_rate"] - df["Total item"]
    df["d_base_rate"] = df["base_rate"].diff()

    # ==========================================================
    # SECTION 3: NOMINAL POLICY RATE VS INFLATION TARGET
    # ==========================================================
    st.subheader("Nominal Policy Rate, CPI Inflation, Inflation Target and Monetary Stance")

    st.markdown(
        """
        Red shaded regions indicate periods of **nominal policy rate hikes**, reflecting a tightening
        monetary stance. Green shaded regions indicate **policy rate cuts**, reflecting an
        accommodative stance.

        The Bank of Korea adjusts the nominal policy rate in response to deviations of inflation
        from its **2% target**.

        In the Real Policy Rate graph below, the Blue shaded region indicates neutral real rate zone (0 - 1%)
        ,neither stimulating nor restraining economic activity.

        We will explore how the BOK's policy actions have aligned with inflation dynamics
        and their implications for real monetary conditions.
        """
    )

    plot_df = df.rename(columns={
        "base_rate": "Base Rate (%)",
        "Total item": "CPI Inflation (%)"
    })

    fig = px.line(
        plot_df,
        x=plot_df.index,
        y=["Base Rate (%)", "CPI Inflation (%)"],
        labels={"value": "Percent", "index": "Date"},
        color_discrete_map={
            "CPI Inflation (%)": "#1f77b4",
            "Base Rate (%)": "pink"
        },
        title="Nominal Policy Rate vs CPI Inflation"
    )

    fig.add_hline(
        y=2,
        line_dash="dash",
        line_color="cornflowerblue",
        annotation_text="Inflation Target (2%)"
    )

    # Tightening / easing shading
    for i in range(1, len(df)):
        if df["d_base_rate"].iloc[i] > 0:
            fig.add_vrect(
                x0=df.index[i-1],
                x1=df.index[i],
                fillcolor="red",
                opacity=0.15,
                line_width=0
            )
        elif df["d_base_rate"].iloc[i] < 0:
            fig.add_vrect(
                x0=df.index[i-1],
                x1=df.index[i],
                fillcolor="green",
                opacity=0.15,
                line_width=0
            )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "When inflation rose well above the 2% target, notably during 2021–2023, "
        "the BOK responded with aggressive rate hikes (red shaded regions). "
        "As inflation pressures eased and growth concerns emerged, policy rates were lowered, "
        "as reflected in the green shaded regions from 2024 onwards."
    )

    # ==========================================================
    # SECTION 4: REAL POLICY RATE (Effective Monetary Policy)
    # ==========================================================
    fig = px.line(
        df,
        x=df.index,
        y="real_rate",
        labels={"real_rate": "Real Policy Rate (%)", "index": "Date"},
        title="Real Policy Rate and Effectiveness of Monetary Stance (Shaded)"
    )

    # Neutral real rate band (0–1%)
    fig.add_hrect(
        y0=0,
        y1=1,
        fillcolor="blue",
        opacity=0.15,
        line_width=0,
        annotation_text="Neutral Real Rate Zone (0–1%)",
        annotation_position="top left"
    )

    peak_date = df["Total item"].idxmax()

    fig.add_vline(
        x=peak_date,
        line_dash="dot",
        line_color="gray"
    )

    fig.add_annotation(
        x=peak_date,
        y=1,
        yref="paper",
        text="CPI Inflation starts easing",
        showarrow=True
    )

    # Regime shading (same logic as nominal chart)
    for i in range(1, len(df)):
        if df["d_base_rate"].iloc[i] > 0:
            fig.add_vrect(
                x0=df.index[i-1],
                x1=df.index[i],
                fillcolor="red",
                opacity=0.12,
                line_width=0
            )
        elif df["d_base_rate"].iloc[i] < 0:
            fig.add_vrect(
                x0=df.index[i-1],
                x1=df.index[i],
                fillcolor="green",
                opacity=0.12,
                line_width=0
            )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        """
        Despite sustained nominal rate hikes during the inflation surge (as indicated by the red shaded regions)
        , real rates remained **negative for an extended period**, reflecting the erosion of policy tightness by
        elevated inflation. This shows that while the BOK was tightening nominally (increase in base_rate), the real monetary conditions
        were still accommodative (negative) until inflation was brought under control (started easing).

        This highlights the distinction between **nominal tightening** and **effective real
        monetary conditions**.
        """
    )

    st.markdown(
    "While the nominal policy rate reflects the Bank of Korea’s **policy intent**, "
    "the real policy rate captures the **effective degree of monetary tightness** "
    "once inflation is taken into account."
    )

    st.divider()
    # ==========================================================
    # SECTION 7: EXPECTATIONS & CREDIBILITY
    # ==========================================================
    st.subheader("Inflation Expectations & Credibility")

    z_df = df[["Total item", "Expectations of Interest Rates"]].dropna()
    z_df = (z_df - z_df.mean()) / z_df.std()

    plot_z_df = z_df.rename(columns={
        "Total item": "CPI Inflation", "Expectations of Interest Rates": "Inflation Expectations"})

    fig = px.line(
        plot_z_df,
        x=plot_z_df.index,
        y=plot_z_df.columns,
        # Adding the requested title
        title="Inflation Expectations and BOK Credibility",
        # Relabeling variables for the Legend and Hover tooltips
        labels={
            "value": "Standardised Index (Z-Score)", 
            "index": "Date"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Inflation expectations closely track realised inflation, "
        "suggesting strong policy credibility by the Bank of Korea."
    )
