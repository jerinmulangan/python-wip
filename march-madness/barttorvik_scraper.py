#!/usr/bin/env python3
#barttorvik_scraper.py

from pathlib import Path
import re
import time
import warnings

import pandas as pd
import requests
from io import StringIO

START_YEAR, END_YEAR = 2008, 2025
OUT_DIR = Path("data"); OUT_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


TYPES  = ["R", "C", "N"]
          
VENUES = ["All", "H", "A-N", "A"]      

URL_TEMPLATE = (
    "https://barttorvik.com/trank.php"
    "?year={year}&sort=&top=0&conlimit=All"
    "&venue={venue}&type={ttype}#"
)

TEAM_RE = re.compile(r"""
    ^\s*
    (?P<name>.*?)
    \s+(?P<seed>\d+)\s*seed
    (?:,\s*(?P<res>.+))? 
    $""", re.VERBOSE | re.IGNORECASE)

def _split_team_col(df: pd.DataFrame) -> pd.DataFrame:
    def extract(cell: str):
        m = TEAM_RE.match(str(cell))
        if not m:
            return pd.Series({"team": str(cell).strip(),
                              "seed": pd.NA,
                              "tourney_res": pd.NA})
        return pd.Series({
            "team":         m.group("name").strip(),
            "seed":         int(m.group("seed")),
            "tourney_res":  (m.group("res") or "").strip() or pd.NA,
        })
    meta = df["team"].apply(extract)
    return df.drop(columns=["team"]).join(meta)

def _drop_internal_headers(df: pd.DataFrame) -> pd.DataFrame:
    mask = df["rk"].astype(str).str.fullmatch(r"\d+")
    df = df[mask].copy()
    df["rk"] = df["rk"].astype(int)
    return df

def _clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.replace(r"[%.\s]+", "_", regex=True)
                  .str.replace(r"[^\w_]", "", regex=True)
                  .str.lower()
    )
    return df

def _scrape_url(url: str) -> pd.DataFrame:
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    tables = pd.read_html(StringIO(resp.text), flavor="bs4", header=1)
    if not tables:
        raise RuntimeError(f"No table found at {url}")
    df = tables[0]
    df = _clean_cols(df)
    df = _drop_internal_headers(df)
    df = _split_team_col(df)
    return df

def main():
    all_frames = []

    for year in range(START_YEAR, END_YEAR + 1):
        for ttype in TYPES:
            for venue in VENUES:
                url = URL_TEMPLATE.format(year=year, ttype=ttype, venue=venue)
                print(f"» {year} / type={ttype} / venue={venue} … ", end="", flush=True)
                try:
                    df = _scrape_url(url)
                    print("ok")
                except Exception as e:
                    warnings.warn(f"  → failed ({e})")
                    continue

                df["year"]  = year
                df["type"]  = ttype
                df["venue"] = venue
                fname = OUT_DIR / f"trank_{year}_{ttype}_{venue.replace('-', '')}.csv"
                df.to_csv(fname, index=False)
                all_frames.append(df)

                time.sleep(.5)

    if all_frames:
        master = pd.concat(all_frames, ignore_index=True)
        master.to_csv(OUT_DIR / f"trank_{START_YEAR}_{END_YEAR}_all.csv",
                      index=False)
        print("✓ wrote master CSV for all years + filters")

if __name__ == "__main__":
    main()
