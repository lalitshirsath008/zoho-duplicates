import pandas as pd
import pdfplumber
import os
from typing import List, Dict, Any, Union

class SourceLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.extension = os.path.splitext(file_path)[1].lower()

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes column names exactly as requested: lower, replace space with _, strip."""
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.strip()
        return df

    def load_data(self) -> Dict[str, Any]:
        """Loads data based on file extension and returns a dictionary of dataframes."""
        if self.extension == '.csv':
            df = pd.read_csv(self.file_path)
            return {"Default": self.normalize_columns(df)}
        
        elif self.extension in ['.xlsx', '.xls']:
            xl = pd.ExcelFile(self.file_path)
            sheets_data = {}
            for sheet in xl.sheet_names:
                df = pd.read_excel(xl, sheet_name=sheet)
                sheets_data[sheet] = self.normalize_columns(df)
            return sheets_data
            
        elif self.extension == '.pdf':
            df = self._load_pdf_as_single_df()
            return {"PDF_Extract": df} if not df.empty else {}
        
        else:
            raise ValueError(f"Unsupported file format: {self.extension}")

    def _load_pdf_as_single_df(self) -> pd.DataFrame:
        """Extracts tables from PDF as one single Master DataFrame (User's logic)."""
        rows = []
        try:
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    table = page.extract_table()
                    if table:
                        for r in table:
                            rows.append(r)
            
            if len(rows) < 2:
                return pd.DataFrame()
                
            df = pd.DataFrame(rows[1:], columns=rows[0])
            return self.normalize_columns(df)
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return pd.DataFrame()

    def get_structure(self) -> List[Dict[str, Any]]:
        """Returns metadata structure for all extracted tables/sheets."""
        data_map = self.load_data()
        structure = []
        for name, df in data_map.items():
            structure.append({
                "name": name,
                "columns": df.columns.tolist(),
                "sample_rows": df.head(3).to_dict(orient="records"),
                "total_rows": len(df)
            })
        return structure

if __name__ == "__main__":
    print("SourceLoader initialized.")
