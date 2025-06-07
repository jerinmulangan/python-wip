#barttorvik_scraper.py

from pathlib import Path
import re
import time
import warnings

import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO

BASE_URL = "https://barttorvik.com/trank.php?year={year}&sort=&conlimit=#"
START_YEAR, END_YEAR = 2008, 2025          
OUT_DIR = Path("data")                     
OUT_DIR.mkdir(exist_ok=True)

HEADERS = {                                 
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/124.0.0.0 Safari/537.36")
}

def _clean_cols(df: pd.DataFrame) -> pd.DataFrame:
    # standardize column names
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.replace(r"[%.\s]+", "_", regex=True)
                  .str.replace(r"[^\w_]", "", regex=True)
                  .str.lower()
    )
    return df

# request + pandas
def scrape_year_requests(year: int) -> pd.DataFrame:
    url = BASE_URL.format(year=year)
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    tables = pd.read_html(StringIO(resp.text), flavor="bs4", header=1)
    if not tables:
        raise ValueError("request: no tables found")
    df = tables[0]
    df = _clean_cols(df)
    df["year"] = year
    return df

# selenium fallback
def scrape_year_selenium(year: int, driver_path: str = "C:/Users/jerin/Documents/chromedriver.exe") -> pd.DataFrame:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By

    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = BASE_URL.format(year=year)
        driver.get(url)
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, "lxml")
        tables = pd.read_html(StringIO(str(soup)), header=1)
        if not tables:
            raise ValueError("selenium: no tables found")
        df = tables[0]
        df = _clean_cols(df)
        df["year"] = year
        return df
    finally:
        driver.quit()

def main():
    master_frames = []

    for yr in range(START_YEAR, END_YEAR + 1):
        print(f"» scraping {yr} … ", end="", flush=True)
        try:
            df_year = scrape_year_requests(yr)
            print("requests")
        except Exception as e:
            warnings.warn(f"requests failed for {yr} ({e}); fallback: selenium")
            df_year = scrape_year_selenium(yr)
            print("selenium")

        # write out csv
        csv_year = OUT_DIR / f"trank_{yr}.csv"
        df_year.to_csv(csv_year, index=False)
        master_frames.append(df_year)

    # combine seasons
    df_all = pd.concat(master_frames, ignore_index=True)
    df_all.to_csv(OUT_DIR / "trank_2008_2025.csv", index=False)
    print(f"\nsaved {len(master_frames)} yearly files + master csv to {OUT_DIR.resolve()}")

if __name__ == "__main__":
    main()
