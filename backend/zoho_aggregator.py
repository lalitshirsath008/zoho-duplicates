import pandas as pd
import os
from typing import List, Dict, Any

class ZohoAggregator:
    def __init__(self, file_paths: List[str]):
        self.file_paths = file_paths

    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardizes column names exactly as requested: lower, replace space with _, strip."""
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.strip()
        return df

    def get_merged_data(self) -> pd.DataFrame:
        """Reads and merges all CSV files into a single master DataFrame."""
        dfs = []
        for path in self.file_paths:
            try:
                df = pd.read_csv(path)
                df = self.normalize_columns(df)
                dfs.append(df)
            except Exception as e:
                print(f"Error loading {path}: {e}")
        
        if not dfs:
            return pd.DataFrame()
            
        merged_df = pd.concat(dfs, ignore_index=True)
        # Remove perfect duplicates
        merged_df = merged_df.drop_duplicates()
        return merged_df

    def get_structure(self) -> Dict[str, Any]:
        """Returns metadata structure for the aggregated Zoho dataset."""
        df = self.get_merged_data()
        if df.empty:
            return {"dataset_name": "Merged_Zoho", "columns": [], "sample_rows": [], "total_rows": 0}
            
        return {
            "dataset_name": "Merged_Zoho",
            "columns": df.columns.tolist(),
            "sample_rows": df.head(5).to_dict(orient="records"),
            "total_rows": len(df)
        }

if __name__ == "__main__":
    print("ZohoAggregator initialized.")
