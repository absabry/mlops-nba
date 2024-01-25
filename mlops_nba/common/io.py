from pathlib import Path
import json
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
    """Write json file.
    Args:
        data (dict): data to write
        path (Path): path to write to
    """
    try:
        with open(path, "w") as f:
            json.dump(data, f)
            return True
    except Exception as e:
        print(e)
    return False
