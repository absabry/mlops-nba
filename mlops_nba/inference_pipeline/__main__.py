import json

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from mlops_nba.common.io import load_model
from mlops_nba.config import INFERENCE_DIR, MODEL_DIR
from mlops_nba.data_pipeline.raw_to_curated.transformations import create_nba_features
from mlops_nba.training_pipeline.transformations import prepare_for_model

if __name__ == "__main__":
    dataframe = pd.read_csv(INFERENCE_DIR / "25_01_2024" / "input.csv")
    dataframe = create_nba_features(dataframe)
    model_path = max(MODEL_DIR.glob("*"), key=lambda x: x.name, default=None)
    print(model_path)

    model = load_model(model_path / "champion.pkl")
    metadata = json.load(open(model_path / "champion.json"))

    model_input = prepare_for_model(dataframe)
    result = model.predict(model_input)

    dataframe.to_csv(INFERENCE_DIR / "25_01_2024" / "output.csv", index=False)
