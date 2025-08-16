import pandas as pd

def _ensure_sorted(df: pd.DataFrame, period_col: str = "period") -> pd.DataFrame:
    return df.sort_values(period_col)

def qoq_growth(df: pd.DataFrame, group_cols: list, value_col: str = "registrations") -> pd.DataFrame:
    """
    QoQ % change within each group over time.
    """
    df = df.copy()
    df = _ensure_sorted(df)
    out = (df
           .groupby(group_cols + ["period"], as_index=False)[value_col].sum())
    out["QoQ_%"] = (out
        .groupby(group_cols)[value_col]
        .pct_change() * 100)
    return out

def yoy_growth(df: pd.DataFrame, group_cols: list, value_col: str = "registrations") -> pd.DataFrame:
    """
    YoY % change compares current period to same quarter last year.
    Works on quarterly PeriodIndex.
    """
    df = df.copy()
    df = _ensure_sorted(df)
    out = (df
           .groupby(group_cols + ["period"], as_index=False)[value_col].sum())
    # shift by 4 quarters within each group
    out["YoY_%"] = (out
        .groupby(group_cols)[value_col]
        .pct_change(4) * 100)
    return out

def filter_range(df: pd.DataFrame, start_p: pd.Period, end_p: pd.Period) -> pd.DataFrame:
    mask = (df["period"] >= start_p) & (df["period"] <= end_p)
    return df.loc[mask].copy()

def kpi_latest_delta(df: pd.DataFrame, value_col: str = "registrations"):
    """
    Returns (latest_value, delta_vs_prev, pct_change)
    for the whole (already-filtered) dataset summed over all groups.
    """
    s = (df.groupby("period")[value_col].sum().sort_index())
    if len(s) < 2:
        return (int(s.iloc[-1]) if len(s) else 0, 0, 0.0)
    latest, prev = s.iloc[-1], s.iloc[-2]
    delta = latest - prev
    pct = (delta / prev * 100) if prev != 0 else float("inf")
    return int(latest), int(delta), pct
