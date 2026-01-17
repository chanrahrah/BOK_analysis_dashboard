import pandas as pd
import numpy as np

df_bok = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\BOK Base rate MoM.csv')
df_cpi = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Consumer Price indices MoM.csv')
df_cts = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Consumer Tendency Survey MoM.csv')
df_fx = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Exchange Rate of Won against USD, China, Japan Daily.csv')
df_npish = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Final Consumption Expenditure of NPISH by Purpose QoQ.csv')
df_fiscal_balance = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Central Governmnet Fiscal Balance MoM.csv')
df_house = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\House Price Index(KB) MoM.csv')
df_nps = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\nps_asset_allocation YoY.csv')
df_ktb = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Trade of KTB Bond MoM.csv')
df_kospi = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Transactions in KOSPI KOSDAQ Index MoM.csv')
df_debt_gdp = pd.read_csv(r'C:\Users\User\Documents\NUS\Projects\NUSSIF\data\GDP n Debt YoY.csv')
df_debt_house = pd.read_csv(r"C:\Users\User\Documents\NUS\Projects\NUSSIF\data\House Debt Ratio QoQ.csv")
df_nps_market = pd.read_csv(r"C:\Users\User\Documents\NUS\Projects\NUSSIF\data\nps market perfomance index MoM.csv")
df_debt = pd.read_csv(r"C:\Users\User\Documents\NUS\Projects\NUSSIF\data\Debt QoQ.csv")

# clean nps data to correct format
df_nps["date"] = pd.to_datetime(df_nps["date"].astype(str), format="%Y")
df_nps_percent = df_nps.pivot(index="date", columns="asset_class", values="weight_percent").sort_index()
df_nps_aum = df_nps.pivot(index="date", columns="asset_class", values="aum_billion_krw").sort_index()

# clean data type by frequency
yearly_data = [df_nps, df_debt_gdp]
quarterly_data = [df_npish, df_debt_gdp, df_debt_house, df_debt]
monthly_data = [df_bok, df_cpi, df_cts, df_house, df_ktb, df_kospi, df_fiscal_balance, df_nps_market]
daily_data = [df_fx]
full_data = yearly_data + quarterly_data + monthly_data + daily_data

# Helper cleaning function
import numpy as np

def clean_data(data: pd.DataFrame):
    # 1. Clean date column
    if "date" in data.columns:
        data["date"] = pd.to_datetime(data["date"].astype(str), format="mixed", errors="coerce")
        data.set_index("date", inplace=True)
    
    # 2. Clean numeric columns
    for col in data.columns:
        data[col] = (
            data[col].astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(" ", "", regex=False)
            .replace({"-": np.nan, ".": np.nan, "..": np.nan, "nan": np.nan})
        )
        data[col] = pd.to_numeric(data[col], errors="coerce")
    
    # 3. Clean column names
    data.columns = data.columns.str.strip()
    return data


# --------------------------------------------
# Clean data
for df in quarterly_data:
    df["date"] = (
        df["date"]
        .astype(str)
        .str.replace("/", "", regex=False)
    )
    df["date"] = pd.PeriodIndex(df["date"], freq="Q").to_timestamp()

for i in range(len(full_data)):
    full_data[i] = clean_data(full_data[i])

# clean data units
df_debt_gdp = df_debt_gdp.rename(columns={"Korea, Republic Of": "GDP"})
cols = [
    "Gross External Debt",
    "GDP"
]
df_debt_gdp[cols] = df_debt_gdp[cols] * 1452.33 / 1e6 # USD/KRW exchange rate as of Jan 2026

df_fiscal_balance = df_fiscal_balance / 1000

df_npish = df_npish / 1000

df_ktb = df_ktb / 1e12

df_nps_market["KTB Trading Value"] = df_nps_market["KTB Trading Value"] / 1e9

cols_kospi = ['KOSDAQ_Trading Value', 'KOSDAQ_Trading Value (Daily Arg.)', 
              'KOSPI_Trading Value', 'KOSPI_Trading Value (Daily Arg.)']
df_kospi[cols_kospi] = df_kospi[cols_kospi] / 1e9

# clean data into monthly frequency
# daily to monthly
df_fx_monthly    = df_fx.resample("MS").mean()
# quarterly to monthly
df_npish_monthly = df_npish.resample("MS").ffill()
df_debt_house_monthly = df_debt_house.resample("MS").ffill()
df_debt_monthly = df_debt.resample("MS").ffill()

# yearly to monthly
df_nps_percent_monthly   = df_nps_percent.resample("MS").interpolate()
df_nps_aum_monthly       = df_nps_aum.resample("MS").interpolate()
df_debt_gdp_monthly = df_debt_gdp.resample("MS").interpolate()

full_df_list = [df_bok, df_cpi, df_cts, df_fx_monthly, df_npish_monthly, df_house, 
                df_debt_house, df_debt_house_monthly,
                df_nps_percent_monthly, df_nps_aum_monthly, df_ktb, df_kospi,
                df_fiscal_balance, df_debt_gdp_monthly,
                df_npish, df_debt_gdp,df_debt,
                df_nps_percent, df_nps_aum, df_nps_market,
                df_fx]

for df in full_df_list:
    df.apply(pd.to_numeric, errors="coerce")

# --------------------------------------------
DATA = {
    "monthly": {
        "bok_rate": df_bok,
        "cpi": df_cpi,
        "cts": df_cts,
        "fx": df_fx_monthly,
        "npish": df_npish_monthly,
        "house_price": df_house,
        "nps_percent": df_nps_percent_monthly,
        "nps_aum": df_nps_aum_monthly,
        "ktb": df_ktb,
        "kospi": df_kospi,
        "fiscal_balance": df_fiscal_balance,
        "debt_gdp": df_debt_gdp_monthly,
        "debt_house": df_debt_house_monthly,
        "nps_market": df_nps_market,
        "debt": df_debt_monthly,
    },
    "quarterly": {
        "npish": df_npish,
        "debt_house": df_debt_house,
        "debt": df_debt,
    },
    "yearly": {
        "nps_percent": df_nps_percent,
        "nps_aum": df_nps_aum,
        "debt_gdp": df_debt_gdp,
    },
    "daily": {
        "fx": df_fx,
    }
}
