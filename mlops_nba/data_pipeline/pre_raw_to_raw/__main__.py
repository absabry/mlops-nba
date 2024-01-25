import click
import pandas as pd

from mlops_nba.common.dates import convert_duration_to_number, get_now
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.config import PRE_RAW_DATA_DIR, RAW_DATA_DIR

# 'eFG%', "Rk" --> not needed
mapping = {
    "TEAM_ABBREVIATION": "Tm",
    "PLAYER_NAME": "Player",
    "POSITION": "Pos",
    "AGE": "Age",
    "GAME_ID": "G",
    "START_POSITION": "GS",
    "mins": "MP",
    "FGM": "FG",
    "FGA": "FGA",
    "FG_PCT": "FG%",
    "FG3M": "3P",
    "FG3A": "3PA",
    "FG3_PCT": "3P%",
    "2PM": "2P",
    "2PA": "2PA",
    "2P_PCT": "2P%",
    "FTM": "FT",
    "FTA": "FTA",
    "FT_PCT": "FT%",
    "OREB": "ORB",
    "DREB": "DRB",
    "REB": "TRB",
    "AST": "AST",
    "STL": "STL",
    "BLK": "BLK",
    "TO": "TOV",
    "PF": "PF",
    "PTS": "PTS",
}


def transformation(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Transform input dataframe and add some columns.

    Args:
        dataframe (pd.DataFrame): boscores as got from raw stage

    Returns:
        pd.DataFrame: transformed dataframe
    """
    dataframe["2PM"] = dataframe["FGM"] - dataframe["FG3M"]
    dataframe["2PA"] = dataframe["FGA"] - dataframe["FG3A"]
    dataframe["2P_PCT"] = dataframe["2PM"] / dataframe["2PA"]
    dataframe["mins"] = (
        dataframe["MIN"].fillna("0:00").apply(convert_duration_to_number)
    )
    dataframe["AGE"] = dataframe["AGE"].fillna(0).astype(int)
    return dataframe


def aggregate(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Aggregate pre-raw data to have one row = one player stats of multiple games."""
    aggregation_functions = {
        "first": ["TEAM_ABBREVIATION", "PLAYER_ID", "PLAYER_NAME", "AGE", "POSITION"],
        "mean": [
            "FGM",
            "FGA",
            "FG_PCT",
            "FG3M",
            "FG3A",
            "FG3_PCT",
            "2PM",
            "2PA",
            "2P_PCT",
            "FTM",
            "FTA",
            "FT_PCT",
            "OREB",
            "DREB",
            "REB",
            "AST",
            "STL",
            "BLK",
            "TO",
            "PF",
            "PTS",
            "PLUS_MINUS",
            "mins",
        ],
        "count": ["GAME_ID", "START_POSITION"],
    }
    aggreations = {
        column: key for key, value in aggregation_functions.items() for column in value
    }
    return dataframe.groupby("PLAYER_NAME").agg(aggreations)


@click.command()
@click.option(
    "--folder-prefix",
    type=str,
    required=True,
    help="Input folder path that is already created on pre_raw folder",
)
def main(folder_prefix: str):
    """Create raw data from pre_raw data."""
    now = get_now(for_files=True)
    _ = create_folder(RAW_DATA_DIR / folder_prefix)

    boxscores = pd.read_csv(PRE_RAW_DATA_DIR / folder_prefix / "boxscores.csv")
    players = pd.read_csv(PRE_RAW_DATA_DIR / folder_prefix / "players.csv")

    # transformation and aggregations
    boxscores_with_players = boxscores.merge(players, on="PLAYER_ID", how="left")
    tr_boxscores_with_players = transformation(boxscores_with_players)
    raw_data = aggregate(tr_boxscores_with_players).rename(columns=mapping)

    # remove columns that are not needed from the api
    raw_data = raw_data.reset_index()[mapping.values()]

    # output results
    raw_data.to_parquet(RAW_DATA_DIR / folder_prefix / f"{now}-raw_data.parquet")
    write_metadata(
        {
            "from": "pre_raw",
            "to": "raw",
            "execution_date": get_now(),
            "raw_data": f"{now}-raw_data.parquet",
            "folder_prefix": folder_prefix,
            "n_data": len(raw_data),
            "n_players": len(players),
            "n_boxscores": len(boxscores),
        },
        RAW_DATA_DIR / folder_prefix / "metadata.json",
    )


if __name__ == "__main__":
    main()
