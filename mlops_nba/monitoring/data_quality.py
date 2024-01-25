import great_expectations as ge
import pandas as pd


class QualityChecker:
    def __init__(self, data: pd.DataFrame):
        self.df = ge.from_pandas(data)
        self.errors = {}

    def apply(self):
        """Define the logic for each class"""

    def get_status(self):
        """
        Return the status of the quality check
        """
        if self.errors:
            return "Failed"
        return "Success"

    def to_dict(self):
        """
        Return the status of the quality check
        """
        return {"status": self.get_status(), "errors": self.errors}


class PrerowBoxScoreQuality(QualityChecker):
    def apply(self):
        """apply all the checks"""
        checks = [
            self.df.expect_column_unique_value_count_to_be_between(
                column="TEAM_ID", min_value=20, max_value=30
            ),
            self.df.expect_compound_columns_to_be_unique(
                column_list=["PLAYER_ID", "GAME_ID"]
            ),
        ]
        for check in checks:
            if not check["success"]:
                key = check["expectation_config"]["kwargs"]
                key = key.get("column") if "column" in key else key.get("column_list")
                self.errors[key] = check["result"]


class PrerowPlayerQuality(QualityChecker):
    def apply(self):
        """apply all the checks"""
        checks = [
            self.df.expect_column_values_to_be_between(
                column="AGE", min_value=18, max_value=45
            ),
            self.df.expect_compound_columns_to_be_unique(column_list=["PLAYER"]),
        ]
        for check in checks:
            if not check["success"]:
                key = check["expectation_config"]["kwargs"]
                key = key.get("column") if "column" in key else key.get("column_list")
                self.errors[key] = check["result"]


class RowQuality(QualityChecker):
    def apply(self):
        """apply all the checks"""
        checks = [{"success": True}]
        for check in checks:
            if not check["success"]:
                self.errors[check["expectation_config"]["kwargs"]["column"]] = check[
                    "result"
                ]
