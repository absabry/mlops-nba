import click
import pandas as pd


@click.command()
@click.option(
    "--input_folder",
    type=str,
    required=True,
    help="Input folder path that is already created on pre_raw folder",
)
def main(input_folder: str):
    """Create raw data from pre_raw data."""
    preraw = pd.read_csv(input_folder)


if __name__ == "__main__":
    print("hello world")
