import pandas as pd
from typing import Dict, Any

class ZohoLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def get_structure(self) -> Dict[str, Any]:
        """Scans the Zoho CSV and returns metadata."""
        df = pd.read_csv(self.file_path, nrows=5)
        return {
            "dataset_name": self.file_path.split("\\")[-1],
            "columns": df.columns.tolist(),
            "sample_rows": df.to_dict(orient="records")
        }

    def get_data(self) -> pd.DataFrame:
        """Returns the full dataframe for the Zoho dataset."""
        return pd.read_csv(self.file_path)

if __name__ == "__main__":
    # Test stub
    print("ZohoLoader module loaded.")
