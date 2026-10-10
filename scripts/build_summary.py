"""Build the small summary files the Streamlit app reads (no raw data needed)."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "cookie_cats.csv"
OUT = ROOT / "data" / "processed"


def main():
    df = pd.read_csv(RAW)
    df["retention_1"] = df["retention_1"].astype(int)
    df["retention_7"] = df["retention_7"].astype(int)
    OUT.mkdir(parents=True, exist_ok=True)

    rows = []
    for version, g in df.groupby("version"):
        rounds = g["sum_gamerounds"]
        cutoff = rounds.quantile(0.999)          # drop the top 0.1% for a robust view
        trimmed = rounds[rounds <= cutoff]
        rows.append({
            "version": version,
            "players": len(g),
            "retained_day1": int(g["retention_1"].sum()),
            "retained_day7": int(g["retention_7"].sum()),
            "median_rounds": float(rounds.median()),
            "max_rounds": int(rounds.max()),
            "zero_round_players": int((rounds == 0).sum()),
            "trim_n": len(trimmed),
            "trim_mean_rounds": float(trimmed.mean()),
            "trim_std_rounds": float(trimmed.std()),
        })
    pd.DataFrame(rows).to_csv(OUT / "summary.csv", index=False)

    # Histogram of rounds in bins of 10; everything of 205 or more goes into "200+".
    edges = np.arange(0, 220, 10)
    hist_rows = []
    for version, g in df.groupby("version"):
        clipped = g["sum_gamerounds"].clip(upper=205)
        counts, _ = np.histogram(clipped, bins=edges)
        for start, count in zip(edges[:-1], counts):
            hist_rows.append({"version": version, "bin_start": int(start),
                              "players": int(count)})
    pd.DataFrame(hist_rows).to_csv(OUT / "rounds_hist.csv", index=False)
    print("Wrote summary.csv and rounds_hist.csv to", OUT)


if __name__ == "__main__":
    main()
