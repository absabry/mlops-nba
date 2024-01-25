from pathlib import Path

import click
import pandas as pd

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.config import CURATED_DATA_DIR, RAW_DATA_DIR
from mlops_nba.data_pipeline.raw_to_curated.struct import (
    Reader,
    ReadFirstDrop,
    ReadIngested,
)
from mlops_nba.data_pipeline.raw_to_curated.transformations import create_nba_features

# can be automated in next versions
AGE_THRESHOLD = 23
POINTS_THRESHOLD = 10
EFFICENCY_THRESHOLD = 12


def create_reader(folder: Path):
    """Read csv file. First-drop are the dataset given at the beginning of the project.
    Others are created in data-ingestion mode, so will be read differnetly, even if the data
    is the same.
    """
    parent = folder.name
    if parent == "first-drop":
        return ReadFirstDrop
    return ReadIngested


def get_file(filename: Path, reader: Reader):
    """Load intermediate data from curated data directory."""
    dataframe = reader(path=filename).get_dataframe()
    dataframe["data_period"] = filename.parent.stem
    dataframe["filename"] = filename.stem
    return dataframe


def get_raw_data(path: Path):
    """Load intermediate data from curated data directory."""
    reader = create_reader(folder=path)
    files = path.rglob(f"*.{reader.get_file_type()}")
    players = pd.concat(
        [get_file(filename=stat_player, reader=reader) for stat_player in files],
        ignore_index=True,
    )
    return players


def stars_definition(row):
    """Define rising stars."""
    return (
        row["efficency"] >= EFFICENCY_THRESHOLD
        and row["PTS"] >= POINTS_THRESHOLD
        and row["Age"] <= AGE_THRESHOLD
    )


@click.command()
@click.option(
    "--folder-prefix",
    type=str,
    required=True,
    help="Input folder path that is already created on pre_raw folder",
)
def main(folder_prefix: str):
    """Create curated data from raw data."""
    now = get_now(for_files=True)
    _ = create_folder(CURATED_DATA_DIR / folder_prefix)

    players = get_raw_data(path=RAW_DATA_DIR / folder_prefix)
    players = create_nba_features(players=players)
    players["rising_stars"] = players.apply(stars_definition, axis=1)

    players.to_parquet(
        CURATED_DATA_DIR / folder_prefix / f"curated_players-{now}.parquet",
        compression="snappy",
    )
    write_metadata(
        data={
            "execution_date": get_now(),
            "from": "raw",
            "to": "curated",
            "folder_prefix": folder_prefix,
            "n_transformation": 2,
            "new_columns": ["efficency", "rising_stars"],
            "n_players": len(players),
            "n_stars": len(players[players["rising_stars"] == True]),
        },
        path=CURATED_DATA_DIR / folder_prefix / f"curated_players-{now}.json",
    )


if __name__ == "__main__":
    main()
