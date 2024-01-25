import time

import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, save_model, write_metadata
from mlops_nba.config import CURATED_DATA_DIR, MODEL_DIR

INPUT_PATH = (
    CURATED_DATA_DIR / "first-drop" / "curated_players-20240125__201445.parquet"
)


def prepare_for_model(df):
    df = df.drop(columns=["filename", "efficency", "Rk"])
    le = preprocessing.LabelEncoder()
    for i in ["Player", "Pos", "Tm", "season", "data_period", "game_type"]:
        df.loc[:, i] = le.fit_transform(df.loc[:, i])
    return df


def classification_model(df):

    X = df.drop("rising_stars", axis=1)
    y = df["rising_stars"]

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    rf = RandomForestClassifier()
    t0 = time.time()
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    training_time = time.time() - t0
    accuracy = accuracy_score(y_test, y_pred)

    return rf, {"accuracy": accuracy, "latency": training_time}



if __name__ == "__main__":
    now = get_now(for_files=True)
    _ = create_folder(MODEL_DIR / now)

    dataframe = pd.read_parquet(INPUT_PATH)
    model_input = prepare_for_model(dataframe)
    model, metadata = classification_model(model_input)

    _ = save_model(model, MODEL_DIR / now / "random-forest.pkl")
    write_metadata(
        data={
            "model_name": "random-forest",
            "training_date": now,
            **metadata,
            "training_file": str(INPUT_PATH),
        },
        path=MODEL_DIR / now / "metadata.json",
    )
