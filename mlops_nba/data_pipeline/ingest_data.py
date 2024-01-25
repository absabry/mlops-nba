import pandas as pd
import click
from nba_api.stats.endpoints.leaguegamefinder import LeagueGameFinder
from nba_api.stats.static import teams
from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.common.dates import get_day, get_today, get_now, convert_eu_to_us
from mlops_nba.config import PRE_RAW_DATA_DIR


def create_output_prefix(start_date: str, end_date: str = None) -> str:
    """Create output prefix based on start and end dates."""
    start_date_px = get_day(start_date)
    end_date_px = get_day(end_date) if end_date else get_today()
    return f"{start_date_px}_{end_date_px}"


def get_games(start_date: str, end_date: str = None) -> pd.DataFrame:
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
    nba_teams = teams.get_teams()
    nba_ids = [team["id"] for team in nba_teams]
    nba_games_dataframe = games[games.TEAM_ID.isin(nba_ids)]

    # keep unique games only
    nba_games = nba_games_dataframe.GAME_ID.unique()

    return nba_games


@click.command()
@click.option("--start_date", required=True, help="Start date in DD/MM/YYYY format.")
@click.option("--end_date", required=False, help="End date in DD/MM/YYYY format.")
def main(start_date: str, end_date: str = None) -> pd.DataFrame:
    """Get all games between start_date and end_date."""
    folder_prefix = create_output_prefix(start_date, end_date)
    _ = create_folder(PRE_RAW_DATA_DIR / folder_prefix)

    games = get_games(start_date, end_date)
    boxscores = pd.concat(
        [BoxScoreTraditionalV2(game_id=game).get_data_frames()[0] for game in games]
    )
    boxscores.to_csv(PRE_RAW_DATA_DIR / folder_prefix / "boxscores.csv", index=False)
    write_metadata(
        data={
            "start_date": start_date,
            "end_date": end_date,
            "n_games": len(games),
            "n_boxscores": len(boxscores),
            "execution_date": get_now(),
        },
        path=PRE_RAW_DATA_DIR / folder_prefix / "metadata.json",
    )


if __name__ == "__main__":
    main()
