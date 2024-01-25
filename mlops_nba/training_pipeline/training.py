import time
from abc import ABC

import click
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, save_model, write_metadata
from mlops_nba.config import CURATED_DATA_DIR, MODEL_DIR


def prepare_for_model(df):
    df = df.drop(columns=["filename", "efficency", "Rk"])
    le = preprocessing.LabelEncoder()
    for i in ["Player", "Pos", "Tm", "season", "data_period", "game_type"]:
        df.loc[:, i] = le.fit_transform(df.loc[:, i])
    return df


class Model(ABC):
    def __init__(self, dataframe: pd.DataFrame, **kwargs: dict):
        self.X = dataframe.drop("rising_stars", axis=1)
        self.y = dataframe["rising_stars"]
        self.kwargs = kwargs

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, **kwargs
        )

        self.metrics = {}
        self.hyper_parameteres = {}

    def apply(self):
        ...

    def get_metadata(self):
        return {
            **self.metrics,
            **self.kwargs,
            **self.hyper_parameteres,
            "name": self.name,
        }


class RandomForestModel(Model):
    def __init__(self, dataframe: pd.DataFrame, **kwargs: dict):
        super().__init__(dataframe, **kwargs)
        self.name = "RandomForestClassifier"

    def apply(self):
        self.hyper_parameteres = {"max_depth": 2, "min_samples_split": 4}
        rf = RandomForestClassifier(**self.hyper_parameteres)
        t0 = time.time()
        rf.fit(self.X_train, self.y_train)
        y_pred = rf.predict(self.X_test)

        self.metrics = {
            "training_time": time.time() - t0,
            "accuracy": accuracy_score(self.y_test, y_pred),
        }


class LogisticRegressionModel(Model):
    def __init__(self, dataframe: pd.DataFrame, **kwargs: dict):
        super().__init__(dataframe, **kwargs)
        self.name = "LogisticRegression"

    def apply(self):
        self.hyper_parameteres = {"C": 0.8, "dual": False}
        logistic_regression = LogisticRegression(**self.hyper_parameteres)
        t0 = time.time()
        logistic_regression.fit(self.X_train, self.y_train)
        y_pred = logistic_regression.predict(self.X_test)

        self.metrics = {
            "training_time": time.time() - t0,
            "accuracy": accuracy_score(self.y_test, y_pred),
        }


@click.command()
@click.option("--input-path", required=True, type=str)
@click.option("--metric", required=False, type=str, default="accuracy")
def main(input_path: str, metric: str):
    now = get_now(for_files=True)
    _ = create_folder(MODEL_DIR / now)

    dataframe = pd.read_parquet(CURATED_DATA_DIR / input_path)
    model_input = prepare_for_model(dataframe)
    models = [
        RandomForestModel(dataframe=model_input),
        LogisticRegressionModel(dataframe=model_input),
    ]
    _ = [model.apply() for model in models]

    # save all models with metadatas
    for model in models:
        model_path = MODEL_DIR / now / model.name
        _ = create_folder(model_path)
        _ = save_model(model, model_path / "model.pkl")
        _ = write_metadata(data=model.get_metadata(), path=model_path / "metadata.json")

    # extract champion model
    model = max(models, key=lambda model: model.metrics.get(metric, None))

    _ = save_model(model, MODEL_DIR / now / "champion.pkl")
    write_metadata(
        data={
            "execution-time": now,
            "training_file": input_path,
            **model.get_metadata(),
        },
        path=MODEL_DIR / now / "champion.json",
    )


if __name__ == "__main__":
    main()
