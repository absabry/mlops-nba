import pandas as pd


def create_nba_features(players: pd.DataFrame) -> pd.DataFrame:
    """Create features from raw data."""
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
    return players
