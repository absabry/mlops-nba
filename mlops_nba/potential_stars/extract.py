import re
from pathlib import Path

import pandas as pd

from mlops_nba.common.io import detect_encoding
from mlops_nba.config import CURATED_DATA_DIR, RAW_DATA_DIR

OUTPUT_FILENAME = "potential-stars.parquet"
# can be automated in next versions
AGE_THRESHOLD = 23
POINTS_THRESHOLD = 10
EFFICENCY_THRESHOLD = 12


def get_file(filename: str):
    """Load intermediate data from curated data directory."""
    df = pd.read_csv(filename, sep=";", encoding="Windows-1252")
    name = filename.stem
    season = re.search(r"\d{4}-\d{4}", name).group()
    type_of_matches = name.split("-").pop().strip()

    df["filename"] = name
    df["season"] = season
    df["period"] = type_of_matches
    return df


def get_raw_data(path: Path):
    """Load intermediate data from curated data directory."""
    files = path.glob("*.csv")
    players = pd.concat(
        [get_file(filename=stat_player) for stat_player in files],
        ignore_index=True,
    )
    return players


if __name__ == "__main__":
    players = get_raw_data(path=RAW_DATA_DIR)
    players["efficency"] = (
        players.PTS
        + players.TRB
        + players.AST
        + players.STL
        + players.BLK
        - (players.FGA - players.FG)
        - (players.FTA - players.FT)
        - players.TOV
    )
    rising_stars = (
        players.query(
            f"(efficency >= {EFFICENCY_THRESHOLD}) & (PTS >= {POINTS_THRESHOLD}) & (Age <= {AGE_THRESHOLD})"
        )
        .sort_values("efficency", ascending=False)
        .sort_values(["efficency", "Age"], ascending=True)
    )
    players.to_parquet(CURATED_DATA_DIR / OUTPUT_FILENAME, compression="snappy")
