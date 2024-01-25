import re
from pathlib import Path

import pandas as pd

from mlops_nba.common.dates import get_now
from mlops_nba.config import CURATED_DATA_DIR, RAW_DATA_DIR

OUTPUT_PRE_ROW = ""
OUTPUT_ROW = ""
OUTPUT_CURATED = ""
OUTPUT_PREPROCESSED = ""

data_prerow = pd.read_csv(OUTPUT_PRE_ROW)
data_row = pd.read_csv(OUTPUT_ROW)
data_curated = pd.read_csv(OUTPUT_CURATED)
data_preprocessed = pd.read_csv(OUTPUT_PREPROCESSED)


class prerow_quality:
    def __init__(self, data_prerow):
        self.df = ge.from_pandas(data)
        self.uniquness = self.Uniquness_PlayerTeamPosition()
        self.max_games = self.Max_NbGames()
        self.positions = self.Check_Existing_Positions()

    def Uniquness_PlayerTeamPosition(
        self,
    ):
        return self.df.expect_compound_columns_to_be_unique(
            column_list=["Player", "Pos", "Tm"]
        )["success"]

    def Max_NbGames(self):
        return self.df.expect_column_values_to_be_between(
            column="Age", min_value=1, max_value=70
        )["success"]

    def Check_Existing_Positions(self):
        return df.expect_column_values_to_be_in_set(
            column="Pos", value_set=["SG", "SF", "PF", "C", "PG"]
        )


class row_quality:
    def __init__(self, data_row):
        self.df = ge.from_pandas(data)
        self.uniquness = self.Uniquness_PlayerTeamPosition()
        self.max_games = self.Max_NbGames()
        self.positions = self.Check_Existing_Positions()

    def Uniquness_PlayerTeamPosition(self):
        return self.df.expect_compound_columns_to_be_unique(
            column_list=["Player", "Pos", "Tm"]
        )["success"]

    def Max_NbGames(self):
        return self.df.expect_column_values_to_be_between(
            column="Age", min_value=1, max_value=70
        )["success"]

    def Check_Existing_Positions(self):
        return df.expect_column_values_to_be_in_set(
            column="Pos", value_set=["SG", "SF", "PF", "C", "PG"]
        )


class curated:
    def __init__(self, data_curated):
        self.df = ge.from_pandas(data)
        self.uniquness = self.Uniquness_PlayerTeamPosition()
        self.max_games = self.Max_NbGames()
        self.positions = self.Check_Existing_Positions()

    def Uniquness_PlayerTeamPosition(self):
        return self.df.expect_compound_columns_to_be_unique(
            column_list=["Player", "Pos", "Tm"]
        )["success"]

    def Max_NbGames(self):
        return self.df.expect_column_values_to_be_between(
            column="Age", min_value=1, max_value=70
        )["success"]

    def Check_Existing_Positions(self):
        return df.expect_column_values_to_be_in_set(
            column="Pos", value_set=["SG", "SF", "PF", "C", "PG"]
        )


class preprocessed_quality:
    def __init__(self, data):
        self.df = ge.from_pandas(data_preprocessed)
        self.uniquness = self.Uniquness_PlayerTeamPosition()
        self.max_games = self.Max_NbGames()
        self.positions = self.Check_Existing_Positions()

    def Uniquness_PlayerTeamPosition(self):
        return self.df.expect_compound_columns_to_be_unique(column_list=["Player"])[
            "success"
        ]

    def Max_NbGames(self):
        return self.df.expect_column_values_to_be_between(
            column="Age", min_value=1, max_value=70
        )["success"]

    def Check_Existing_Positions(self):
        return df.expect_column_values_to_be_in_set(
            column="Pos", value_set=["SG", "SF", "PF", "C", "PG"]
        )
