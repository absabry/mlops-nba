import click
import pandas as pd
from nba_api.stats.endpoints.commonteamroster import CommonTeamRoster

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import write_metadata
from mlops_nba.config import PRE_RAW_DATA_DIR, SEASON
from mlops_nba.data_pipeline.ingest.utils import get_teams
from mlops_nba.monitoring.data_quality import PrerowPlayerQuality


@click.command()
@click.option(
    "--folder-prefix", required=True, help="Folder prefix created by previous steps"
)
def main(folder_prefix: str) -> None:
    """Get current active players to be merged with boxscores of the interval."""
    teams = get_teams()

    players = pd.concat(
        [
            CommonTeamRoster(team_id=team, season=SEASON).get_data_frames()[0]
            for team in teams
        ]
    )

    # data-quality checks
    players_quality = PrerowPlayerQuality(players)
    players_quality.apply()

    players.to_csv(PRE_RAW_DATA_DIR / folder_prefix / "players.csv", index=False)
    write_metadata(
        data={
            "players": {
                "n_players": len(players),
                "execution_date": get_now(),
                "folder_prefix": folder_prefix,
                "quality": players_quality.to_dict(),
            }
        },
        path=PRE_RAW_DATA_DIR / folder_prefix / "metadata.json",
    )


if __name__ == "__main__":
    main()
