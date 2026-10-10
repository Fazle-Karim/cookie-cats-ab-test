"""Load the raw CSV into a local SQLite database (data/cookie_cats.db)."""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "raw" / "cookie_cats.csv"
DB = ROOT / "data" / "cookie_cats.db"
EXPECTED = ["userid", "version", "sum_gamerounds", "retention_1", "retention_7"]


def main():
    if not CSV.exists():
        sys.exit(f"Missing file: {CSV}\nDownload cookie_cats.csv from Kaggle first.")
    df = pd.read_csv(CSV)
    if list(df.columns) != EXPECTED:
        sys.exit(f"Unexpected columns: {list(df.columns)}\nExpected: {EXPECTED}")

    # SQLite has no boolean type, so store the retention flags as 0/1.
    for col in ("retention_1", "retention_7"):
        df[col] = df[col].astype(int)

    with sqlite3.connect(DB) as con:
        df.to_sql("players", con, if_exists="replace", index=False)
        # This fails loudly if any userid is duplicated.
        con.execute("CREATE UNIQUE INDEX ix_players_userid ON players(userid)")
        rows = con.execute("SELECT COUNT(*) FROM players").fetchone()[0]
    print(f"Loaded {rows:,} rows into {DB}")


if __name__ == "__main__":
    main()
