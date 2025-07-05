#!/usr/bin/env python3
# sr_scraper2.py

import re
import time
import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup, Comment

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

def slugify(name: str) -> str:
    """Lowercase, remove trailing 'ncaa', strip punctuation, replace runs with '-'."""
    s = re.sub(r'\bncaa\b', '', name, flags=re.IGNORECASE)
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def scrape_table(session: requests.Session, url: str, table_id: str) -> pd.DataFrame:
    # retry on 429
    for attempt in range(1, 4):
        resp = session.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 429:
            wait = 10 * attempt
            print(f"  → 429, sleeping {wait}s before retry…", end="", flush=True)
            time.sleep(wait)
            continue
        resp.raise_for_status()
        break
    else:
        resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "lxml")
    table = soup.find("table", id=table_id)
    if table is None:
        # look inside HTML comments
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            if f'id="{table_id}"' in c:
                frag = BeautifulSoup(c, "lxml")
                table = frag.find("table", id=table_id)
                if table is not None:
                    break
    if table is None:
        raise RuntimeError(f"No table `{table_id}` at {url}")

    # header
    header_rows = table.thead.find_all("tr")
    cols = [th.get_text(strip=True) for th in header_rows[-1].find_all("th")]

    # body
    data = []
    for tr in table.tbody.find_all("tr"):
        if tr.get("class") and "thead" in tr["class"]:
            continue
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["th","td"])]
        data.append(cells)

    return pd.DataFrame(data, columns=cols)

def main():
    teams_csv = Path("data/teams_by_year.csv")
    if not teams_csv.exists():
        raise FileNotFoundError(f"{teams_csv} not found")

    df = pd.read_csv(teams_csv, dtype=str)
    df.columns = df.columns.str.lower().str.strip()
    if not {"season","school"}.issubset(df.columns):
        raise RuntimeError("teams_by_year.csv must have 'Season' and 'School' columns (any case)")

    out_base = Path("data/game_logs")
    reg_dir  = out_base / "regular";  reg_dir .mkdir(parents=True, exist_ok=True)
    adv_dir  = out_base / "advanced"; adv_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    for _, row in df.iterrows():
        season = row["season"].strip()
        raw    = row["school"].strip()
        slug   = slugify(raw)
        if not slug:
            print(f"❌ bad slug from '{raw}', skipping")
            continue

        for adv in (False, True):
            typ      = "advanced" if adv else "regular"
            table_id = "sgl-advanced" if adv else "sgl-basic"
            suffix   = "-advanced"    if adv else ""
            url = (
                f"https://www.sports-reference.com/cbb/schools/"
                f"{slug}/men/{season}-gamelogs{suffix}.html"
            )

            print(f"→ {typ.capitalize()} logs for {slug} ({season}) … ", end="", flush=True)
            try:
                df_logs = scrape_table(session, url, table_id)
                out_dir  = adv_dir if adv else reg_dir
                out_path = out_dir / f"{typ}_{slug}_{season}.csv"
                df_logs.to_csv(out_path, index=False)
                print(f"OK [{len(df_logs)} rows]")
            except Exception as e:
                print(f"FAILED: {e!r}")
            # polite pause between **every** request
            time.sleep(2)

if __name__ == "__main__":
    main()
