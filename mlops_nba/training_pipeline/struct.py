import time
from abc import ABC

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


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

        self.model = rf
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

        self.model = logistic_regression
        self.metrics = {
            "training_time": time.time() - t0,
            "accuracy": accuracy_score(self.y_test, y_pred),
        }
