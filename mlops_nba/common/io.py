import chardet


def detect_encoding(folder):
    """Detect encoding of a file."""
    sample = list(folder.glob("*.csv"))[0]

    with open(sample, "rb") as rawdata:
        result = chardet.detect(rawdata.read(10000))
    return result["encoding"]
