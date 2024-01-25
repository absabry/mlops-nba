import click
import pandas as pd
from nba_api.stats.endpoints.commonteamroster import CommonTeamRoster
from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, write_metadata
from mlops_nba.config import PRE_RAW_DATA_DIR, SEASON
from mlops_nba.data_pipeline.ingest.utils import create_output_prefix, get_teams


@click.command()
@click.option("--start_date", required=True, help="Start date in DD/MM/YYYY format.")
@click.option("--end_date", required=False, help="End date in DD/MM/YYYY format.")
def main(start_date: str, end_date: str = None) -> None:
    """Get current active players to be merged with boxscores of the interval."""
    folder_prefix = create_output_prefix(start_date, end_date)
    _ = create_folder(PRE_RAW_DATA_DIR / folder_prefix)

    teams = get_teams()

    players = pd.concat(
        [
            CommonTeamRoster(team_id=team, season=SEASON).get_data_frames()[0]
            for team in teams
        ]
    )

    players.to_csv(PRE_RAW_DATA_DIR / folder_prefix / "players.csv", index=False)
    write_metadata(
        data={
            "players": {
                "start_date": start_date,
                "end_date": end_date,
                "n_players": len(players),
                "execution_date": get_now(),
            }
        },
        path=PRE_RAW_DATA_DIR / folder_prefix / "metadata.json",
    )


if __name__ == "__main__":
    main()
