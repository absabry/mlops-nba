"""Utils relateed to data ingestion module
"""

from nba_api.stats.static import teams

from mlops_nba.common.dates import get_day, get_today


def get_teams():
    """Get all nba teams ids."""
    nba_teams = teams.get_teams()
    return [team["id"] for team in nba_teams]


def create_output_prefix(start_date: str, end_date: str = None) -> str:
    """Create output prefix based on start and end dates."""
    start_date_px = get_day(start_date)
    end_date_px = get_day(end_date) if end_date else get_today()
    return f"{start_date_px}_{end_date_px}"
