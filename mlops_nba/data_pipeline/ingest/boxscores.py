import click
import pandas as pd
from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder

from mlops_nba.common.dates import convert_eu_to_us, get_now
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.config import PRE_RAW_DATA_DIR
from mlops_nba.data_pipeline.ingest.utils import create_output_prefix, get_teams
from mlops_nba.monitoring.data_quality import PrerowBoxScoreQuality


def get_games(start_date: str, end_date: str = None) -> None:
    """Get all nba games between start_date and end_date.

    If end_date is None, we get data until today.
    """
    start_date = convert_eu_to_us(date_str=start_date)
    end_date = convert_eu_to_us(date_str=end_date)

    gamefinder = LeagueGameFinder(
        date_from_nullable=start_date, date_to_nullable=end_date
    )
    games = gamefinder.get_data_frames()[0]

    # filter on nba_teams only, as the leaguegamefinder does not filter
    # on nba teams only correctly.
    nba_ids = get_teams()
    nba_games_dataframe = games[games.TEAM_ID.isin(nba_ids)]

    # keep unique games only
    nba_games = nba_games_dataframe.GAME_ID.unique()

    return nba_games


def get_boxscores(game: str) -> pd.DataFrame:
    """Get boxscores for a list of games."""
    try:
        return BoxScoreTraditionalV2(game_id=game, timeout=60).get_data_frames()[0]
    except Exception as e:
        print(f"game: {game}", e)
        return pd.DataFrame()


@click.command()
@click.option("--start_date", required=True, help="Start date in DD/MM/YYYY format.")
@click.option("--end_date", required=False, help="End date in DD/MM/YYYY format.")
def main(start_date: str, end_date: str = None) -> pd.DataFrame:
    """Get all games between start_date and end_date."""
    folder_prefix = create_output_prefix(start_date, end_date)
    _ = create_folder(PRE_RAW_DATA_DIR / folder_prefix)

    games = get_games(start_date, end_date)
    boxscores = pd.concat([get_boxscores(game) for game in games])
    boxscores.to_csv(PRE_RAW_DATA_DIR / folder_prefix / "boxscores.csv", index=False)

    # data-quality checks
    boxscores_quality = PrerowBoxScoreQuality(boxscores)
    boxscores_quality.apply()

    write_metadata(
        data={
            "boxscores": {
                "start_date": start_date,
                "end_date": end_date,
                "n_games": len(games),
                "n_boxscores": len(boxscores),
                "execution_date": get_now(),
                "quality_checks": boxscores_quality.to_dict(),
            }
        },
        path=PRE_RAW_DATA_DIR / folder_prefix / "metadata.json",
    )


if __name__ == "__main__":
    main()
