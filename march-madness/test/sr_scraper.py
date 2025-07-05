#!/usr/bin/env python3
# sr_scraper1.py

import requests
import pandas as pd
from bs4 import BeautifulSoup, Comment
from pathlib import Path

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def scrape_basic_school_stats(season: int) -> pd.DataFrame:
    url = f"https://www.sports-reference.com/cbb/seasons/men/{season}-school-stats.html"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")

    # 1) try to find the table outright
    table = soup.find("table", id="basic_school_stats")

    # 2) if it's hidden inside an HTML comment, pull it out of the comments
    if table is None:
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            if 'id="basic_school_stats"' in c:
                frag = BeautifulSoup(c, "lxml")
                table = frag.find("table", id="basic_school_stats")
                if table is not None:
                    break

    if table is None:
        raise RuntimeError(f"Couldn't find basic_school_stats table for {season}")

    # 3) extract the final header row
    header_rows = table.find("thead").find_all("tr")
    header = [th.get_text(strip=True) for th in header_rows[-1].find_all("th")]

    # 4) extract all body rows
    body = []
    for tr in table.find("tbody").find_all("tr"):
        if tr.get("class") and "thead" in tr["class"]:
            continue
        cols = [cell.get_text(strip=True) for cell in tr.find_all(["th", "td"])]
        body.append(cols)

    # 5) build a DataFrame
    return pd.DataFrame(body, columns=header)

if __name__ == "__main__":
    seasons = range(2011, 2026)
    out = []

    for year in seasons:
        print(f"Season {year} — ", end="", flush=True)
        try:
            df = scrape_basic_school_stats(year)
            print(f"got {len(df)} teams")

            # keep only the School column, plus the year
            df = df[["School"]].copy()
            df["Season"] = year
            out.append(df)

        except Exception as e:
            print("FAILED:", e)

    # concat all seasons and write one CSV
    if out:
        master = pd.concat(out, ignore_index=True)
        Path("data").mkdir(exist_ok=True)
        master.to_csv("data/teams_by_year.csv", index=False)
        print("\nWrote all teams to data/teams_by_year.csv")
