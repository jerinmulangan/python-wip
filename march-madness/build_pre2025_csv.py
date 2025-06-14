#!/usr/bin/env python3

from pathlib import Path
import re

import pandas as pd
import requests

YEAR    = 2025
URL     = (
    "https://barttorvik.com/trank.php"
    "?year=2025&sort=&hteam=&t2value=&conlimit=All&state=All"
    "&begin=20241101&end=20250316&top=0&revquad=0&quad=5"
    "&venue=All&type=All&mingames=0#"
)
OUT     = Path("data/pre2025.csv")
OUT.parent.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def fetch_raw():
    r = requests.get(URL, headers=HEADERS, timeout=30)
    r.raise_for_status()
    tables = pd.read_html(r.text, flavor="bs4", header=1)
    if not tables:
        raise RuntimeError("No tables found at that URL")
    return tables[0]

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df[df["Rk"].astype(str).str.fullmatch(r"\d+")].copy()

    df.columns = (
        df.columns
          .str.strip()
          .str.replace(r"[%.\s]+", "_", regex=True)
          .str.replace(r"[^\w_]", "", regex=True)
          .str.lower()
    )

    TEAM_RE = re.compile(
        r"^\s*(?P<name>.*?)\s+(?P<seed>\d+)\s*seed(?:,\s*(?P<res>.+))?$",
        re.IGNORECASE,
    )
    def split_team(cell):
        m = TEAM_RE.match(str(cell))
        if not m:
            return pd.Series({"team": str(cell).strip(),
                              "seed": pd.NA,
                              "tourney_res": pd.NA})
        return pd.Series({
            "team":        m.group("name").strip(),
            "seed":        int(m.group("seed")),
            "tourney_res": (m.group("res") or "").strip() or pd.NA,
        })

    df = df.drop(columns=["team"]).join(df["team"].apply(split_team))

    df["year"] = YEAR
    return df

def main():
    print(f"Fetching pre-tournament {YEAR} data…")
    raw = fetch_raw()
    print(f" raw rows: {len(raw)}")
    df = clean(raw)
    print(f" clean rows: {len(df)}")
    df.to_csv(OUT, index=False)
    print(f"✓ wrote {OUT} ({len(df):,} rows)")

if __name__ == "__main__":
    main()
