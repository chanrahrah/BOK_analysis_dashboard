import streamlit as st
import pandas as pd
import sys

def summary_tab(DATA):
    st.header("🇰🇷 Korea Macro Summary")

    # ---------------------------
    # 1. Pull required series
    # ---------------------------
    df_rate = DATA["monthly"]["bok_rate"]
    df_cpi  = DATA["monthly"]["cpi"]
    df_cts  = DATA["monthly"]["cts"]
    df_fisc = DATA["monthly"]["fiscal_balance"]

    # Required columns
    RATE_COL = "base_rate"
    CPI_COL  = "Total item"
    SENT_COL = "Composite Consumer Sentiment Index"
    FISC_COL = "Balance"

    # ---------------------------
    # 2. Guard clauses
    # ---------------------------
    for name, df, col in [
        ("Base rate", df_rate, RATE_COL),
        ("CPI", df_cpi, CPI_COL),
        ("Consumer sentiment", df_cts, SENT_COL),
        ("Fiscal balance", df_fisc, FISC_COL),
    ]:
        if col not in df.columns:
            st.error(f"Missing column '{col}' in {name} dataset.")
            return

    # ---------------------------
    # 3. Latest values & changes
    # ---------------------------
    def merge_df(df1, df2, on="date"):
        return pd.merge(
            df1.reset_index(),
            df2.reset_index(),
            on=on,
            how="inner"
        ).set_index(on)
    
    # merge base rate, cpi, consumer sentiment, fiscal balance dfs
    merged_df = merge_df(
        merge_df(df_rate[[RATE_COL]], df_cpi[[CPI_COL]]),
        merge_df(df_cts[[SENT_COL]], df_fisc[[FISC_COL]])
    )

    def latest_and_change(series, periods=1):
        series = series.dropna()
        return (
            series.iloc[-1],
            series.iloc[-1] - series.iloc[-1 - periods]
        )

    rate_now, rate_change = latest_and_change(merged_df[RATE_COL])
    cpi_now, cpi_change   = latest_and_change(merged_df[CPI_COL])
    sent_now, sent_change = latest_and_change(merged_df[SENT_COL])
    fisc_now, fisc_change = latest_and_change(merged_df[FISC_COL])

    curr_date = merged_df.index[-1].strftime("%B %Y")

    # ---------------------------
    # 4. KPI row
    # ---------------------------
    st.markdown(f"#### 📅 As of {curr_date}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "BOK Base Rate (%)",
        f"{rate_now:.2f}",
        f"{rate_change:+.2f} MoM"
    )

    col2.metric(
        "CPI Inflation (YoY %)",
        f"{cpi_now:.2f}",
        f"{cpi_change:+.2f} MoM"
    )

    col3.metric(
        "Consumer Sentiment",
        f"{sent_now:.1f}",
        f"{sent_change:+.1f} MoM"
    )

    col4.metric(
        "Fiscal Balance",
        f"{fisc_now:,.0f}",
        f"{fisc_change:+,.0f} MoM"
    )

    st.divider()

    # ---------------------------
    # 5. Macro regime logic
    # ---------------------------
    real_rate = rate_now - cpi_now

    stance = (
        "Restrictive" if real_rate > 0
        else "Accommodative" if real_rate < 0
        else "Neutral"
    )

    inflation_trend = "Cooling" if cpi_change < 0 else "Re-accelerating"

    # ---------------------------
    # 6. Narrative summary
    # ---------------------------
    st.subheader("📌 Key Takeaways")

    st.markdown(
        f"""
        - **Real Policy Rate:** {real_rate:.2f}%  
        - **Monetary Policy Stance:** {stance}  
        - **Inflation Trend:** {inflation_trend}  
        - **Consumer Confidence:** {"Improving" if sent_change > 0 else "Weakening"}
        """
    )

    st.info(
        f"""
        Korea’s macro environment remains **{stance.lower()}**, with the
        policy rate exceeding inflation by **{real_rate:.2f}%**.
        Inflation pressures are **{inflation_trend.lower()}**, while
        household sentiment is **{"recovering" if sent_change > 0 else "softening"}**.
        """
    )

