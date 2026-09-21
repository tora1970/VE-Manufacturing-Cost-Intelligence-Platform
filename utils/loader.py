from pathlib import Path
import pandas as pd


class MasterDataLoader:

    def __init__(
        self,
        masterdata_path="data/masterdata"
    ):
        self.masterdata_path = Path(
            masterdata_path
        )

    def load_all(self):

        data = {}

        for file in self.masterdata_path.glob(
            "*.xlsx"
        ):

            key = file.stem.lower()

            data[key] = pd.read_excel(
                file
            )

        return data
