import click
import pandas as pd

from mlops_nba.common.dates import get_now
from mlops_nba.common.io import create_folder, save_model, write_metadata
from mlops_nba.config import CURATED_DATA_DIR, MODEL_DIR
from mlops_nba.training_pipeline.struct import (
    LogisticRegressionModel,
    RandomForestModel,
)
from mlops_nba.training_pipeline.transformations import prepare_for_model


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
    for model_structure in models:
        model_path = MODEL_DIR / now / model_structure.name
        _ = create_folder(model_path)
        _ = save_model(model_structure.model, model_path / "model.pkl")
        _ = write_metadata(
            data=model_structure.get_metadata(), path=model_path / "metadata.json"
        )

    # extract champion model
    champion_structure = max(models, key=lambda model: model.metrics.get(metric, None))

    _ = save_model(champion_structure.model, MODEL_DIR / now / "champion.pkl")
    write_metadata(
        data={
            "execution-time": now,
            "training_file": input_path,
            **champion_structure.get_metadata(),
        },
        path=MODEL_DIR / now / "champion.json",
    )


if __name__ == "__main__":
    main()
