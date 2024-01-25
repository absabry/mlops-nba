import re
from abc import ABC
from pathlib import Path

import pandas as pd

from mlops_nba.config import SEASON


class Reader(ABC):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.dataframe = self.read_dataframe()

    def read_dataframe(self):
        ...

    def additional_columns(self):
        ...

    def get_dataframe(self):
        self.additional_columns()
        return self.dataframe

    @staticmethod
    def get_file_type():
        ...


class ReadFirstDrop(Reader):
    def __init__(self, path: Path) -> None:
        super().__init__(path=path)
        self.path = path

    def read_dataframe(self):
        return pd.read_csv(self.path, sep=";", encoding="Windows-1252")

    def additional_columns(self):
        name = self.path.stem
        season = re.search(r"\d{4}-\d{4}", name).group()
        type_of_games = name.split("-").pop().strip()
        self.dataframe["season"] = season
        self.dataframe["game_type"] = type_of_games

    @staticmethod
    def get_file_type():
        return "csv"


class ReadIngested(Reader):
    def __init__(self, path: Path) -> None:
        super().__init__(path=path)

    def read_dataframe(self):
        return pd.read_parquet(self.path)

    def additional_columns(self):
        self.dataframe["season"] = SEASON
        self.dataframe["game_type"] = "Regular Season"

    @staticmethod
    def get_file_type():
        return "parquet"
