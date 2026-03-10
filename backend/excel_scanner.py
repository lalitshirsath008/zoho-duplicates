import pandas as pd
import openpyxl
from typing import List, Dict, Any

class ExcelScanner:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.xl = pd.ExcelFile(file_path)

    def get_structure(self) -> List[Dict[str, Any]]:
        """Scans all sheets and returns metadata for each."""
        structure = []
        for sheet_name in self.xl.sheet_names:
            df = pd.read_excel(self.xl, sheet_name=sheet_name, nrows=5)
            structure.append({
                "sheet_name": sheet_name,
                "columns": df.columns.tolist(),
                "sample_rows": df.to_dict(orient="records"),
                "total_rows_estimate": self._get_row_count(sheet_name)
            })
        return structure

    def _get_row_count(self, sheet_name: str) -> int:
        """Efficiently gets row count using openpyxl for preview."""
        wb = openpyxl.load_workbook(self.file_path, read_only=True)
        return wb[sheet_name].max_row

    def get_sheet_data(self, sheet_name: str) -> pd.DataFrame:
        """Returns the full dataframe for a specific sheet."""
        return pd.read_excel(self.xl, sheet_name=sheet_name)

if __name__ == "__main__":
    # Test stub
    print("ExcelScanner module loaded.")
