import pandas as pd

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.config import CURATED_DATA_DIR, PREPROCESSED_DATA_DIR


def read_data() -> pd.DataFrame:
    """Read folders one by one. In each folder, we should only keep the most recent dataset (parquet file)
    and ignore others.

    Returns:
        (pd.DataFrame, metadata):
            - the latest data got from currated dataset, per each folder (which is each interval of time)
            - metadata about the process of reading
    """
    folders = list(CURATED_DATA_DIR.glob("*"))
    latest_files = [
        max(folder.rglob("*.parquet"), key=lambda x: x.name, default=None)
        for folder in folders
    ]
    latest_files = list(map(str, filter(None, latest_files)))

    dataframes = [pd.read_parquet(filename) for filename in latest_files]
    return pd.concat(dataframes, ignore_index=True), {
        "folders": list(map(str, folders)),
        "files": latest_files,
        "n_files": len(latest_files),
        "n_rows_per_df": [len(df) for df in dataframes],
    }


def merge_data(currated_data: pd.DataFrame) -> pd.DataFrame:
    """Merge data from different currated runs into a single dataframe ready for training pipeline.

    Args:
        data (pd.DataFrame): data from different sources

    Returns:
        pd.DataFrame: merged data
    """
    mean_columns = [
        "MP",
        "FG",
        "FGA",
        "FG%",
        "FG3",
        "FG3A",
        "FG3%",
        "2P",
        "2PA",
        "2P%",
        "FT",
        "FTA",
        "FT%",
        "ORB",
        "DRB",
        "TRB",
        "AST",
        "STL",
        "BLK",
        "TOV",
        "PF",
        "PTS",
    ]
    aggregation_functions = {
        "first": ["Age", "Pos"],
        "sum": ["G", "GS"],
    }
    aggreations = {
        column: key for key, value in aggregation_functions.items() for column in value
    }
    return currated_data.groupby(["Player", "season", "game_type", "Tm"]).agg(
        aggreations
    )


def main():
    now = get_now()
    _ = create_folder(PREPROCESSED_DATA_DIR)
    curated_data, metadata = read_data()

    final_data = curated_data.copy()
    final_data.to_parquet(PREPROCESSED_DATA_DIR / f"preprocessed_data-{now}.parquet")
    write_metadata(
        data={
            "execution_date": get_now(),
            "from": "curated",
            "to": "preprocessed",
            **metadata,
            "potential_files": [
                str(file) for file in CURATED_DATA_DIR.rglob("*.parquet")
            ],
            "n_rows_input": len(curated_data),
            "n_rows_output": len(final_data),
            "n_columns": len(final_data.columns),
            "columns": list(final_data.columns),
            "filename": f"preprocessed_data-{now}.parquet",
        },
        path=PREPROCESSED_DATA_DIR / f"preprocessed_data-{now}.json",
    )


if __name__ == "__main__":
    main()
