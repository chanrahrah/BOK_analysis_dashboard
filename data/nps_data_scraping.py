import requests
import pandas as pd
import json

BASE_URL = "https://fund.nps.or.kr/eng/orinsm/ptflobrkdwn"

# Map each asset class to endpoint + label
ENDPOINTS = {
    "domestic_equity": "chartOHFD0003P0.do",
    "domestic_fixed_income": "chartOHFD0004P0.do",
    "global_equity": "chartOHFD0005P0.do",
    "global_fixed_income": "chartOHFD0006P0.do"
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
}

payload = {"searchGbu": ""}

def fetch_asset_class(name, endpoint):
    """Fetch and process one asset-class chart."""
    url = f"{BASE_URL}/{endpoint}"
    r = r = requests.post(url, json=payload, headers=headers)
    r.raise_for_status()
    data = r.json()

    rows = data.get("resultDtlList", [])[0:]  # skip index 0 (non-data entry)

    records = []
    for row in rows:
        records.append({
            "asset_class": name,
            "date": int(row["crtrYrNm"]),
            "aum_billion_krw": float(row["artclAmtNm"]),
            "weight_percent": float(row["wholAstCtstRtNm"])
        })

    return pd.DataFrame(records)

# Collect all datasets
all_frames = []

for name, endpoint in ENDPOINTS.items():
    print(f"Fetching {name} ...")
    df = fetch_asset_class(name, endpoint)
    all_frames.append(df)

# Combine
final_df = pd.concat(all_frames, ignore_index=True)
final_df = final_df.sort_values(["asset_class", "date"])

# Save CSV
final_df.to_csv("nps_asset_allocation.csv", index=False)

print("Done! Saved as nps_asset_allocation YoY.csv")
final_df.head()
