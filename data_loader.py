import pandas as pd

def load_data(path: str = "data/sample_data.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # Convert "date" (e.g., 2024-Q1) into a proper Period
    df["period"] = pd.PeriodIndex(df["date"], freq="Q")
    df["year"] = df["period"].map(lambda p: p.year)
    df["quarter"] = df["period"].map(lambda p: f"Q{p.quarter}")

    # Clean categories and manufacturers
    df["manufacturer"] = df["manufacturer"].fillna("Unknown").astype(str).str.title()
    df["category"] = df["category"].fillna("Other").astype(str).str.upper()

    # 👉 Add this for plotting (string version of Period)
    df["period_str"] = df["period"].astype(str)

    print("DEBUG → Columns in df:", df.columns.tolist())  # 👈 check columns in terminal

    return df
