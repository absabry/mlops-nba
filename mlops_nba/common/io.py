import json
import pickle
from pathlib import Path

import chardet


def detect_encoding(folder):
    """Detect encoding of a file."""
    sample = list(folder.glob("*.csv"))[0]

    with open(sample, "rb") as rawdata:
        result = chardet.detect(rawdata.read(10000))
    return result["encoding"]


def create_folder(path: Path) -> bool:
    """Create output folder if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True)
        return True
    return False


def write_metadata(data: dict, path: Path) -> bool:
    """Write the metadata file. If it already exists, append
    new info on the json file and write it again
    Args:
        data (dict): data to write
        path (Path): path to write to
    """
    metadata = json.load(open(path, "r")) if path.exists() else {}
    try:
        with open(path, "w") as f:
            metadata.update(data)
            json.dump(metadata, f)
            return True
    except Exception as e:
        print(e)
    return False


def save_model(model, path: Path) -> bool:
    """Save the model to a pickle file.
    Args:
        model (sklearn model): model to save
        path (Path): path to save the model to
    """
    try:
        with open(path, "wb") as f:
            pickle.dump(model, f)
            return True
    except Exception as e:
        print(e)
    return False
