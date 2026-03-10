import pandas as pd
from typing import Dict, Any, List
from fuzzywuzzy import fuzz

class Reconciler:
    def __init__(self, source_df: pd.DataFrame, zoho_df: pd.DataFrame, column_mapping: Dict[str, str], fuzzy_threshold: int = 90):
        """
        :param source_df: Normalized DataFrame from Source (PDF/Excel/CSV).
        :param zoho_df: Normalized and Merged DataFrame from Zoho.
        :param column_mapping: Map of Source_Col -> Zoho_Col
        :param fuzzy_threshold: Score (0-100) above which strings are considered "matched".
        """
        self.source_df = source_df.reset_index(drop=True)
        self.zoho_df = zoho_df.reset_index(drop=True)
        self.mapping = column_mapping
        self.fuzzy_threshold = fuzzy_threshold
        
        # Select and rename columns in source to match Zoho names
        # Filter mapping to only include columns present in source_df
        self.active_mapping = {k: v for k, v in column_mapping.items() if k in self.source_df.columns}
        self.mapped_source = self.source_df[list(self.active_mapping.keys())].rename(columns=self.active_mapping)

    def reconcile(self) -> Dict[str, Any]:
        """Performs row count check, missing/extra records, and value mismatches."""
        
        source_count = len(self.mapped_source)
        zoho_count = len(self.zoho_df)
        
        # Determine Primary Key (AI suggested or first mapped column)
        key_col = list(self.active_mapping.values())[0] if self.active_mapping else None
        
        if not key_col:
            return {"error": "No valid column mapping provided or columns missing in source."}

        # Sets of keys for comparison (ensure strings for consistency)
        source_keys = set(self.mapped_source[key_col].dropna().astype(str))
        zoho_keys = set(self.zoho_df[key_col].dropna().astype(str))
        
        missing_in_zoho = list(source_keys - zoho_keys)
        extra_in_zoho = list(zoho_keys - source_keys)
        
        # Value Mismatches (Only for matched keys)
        common_keys = source_keys.intersection(zoho_keys)
        mismatches = []
        
        # Iterate through common records to check values
        for key in list(common_keys)[:200]: # Performance cap for prototype
            source_row = self.mapped_source[self.mapped_source[key_col].astype(str) == str(key)].iloc[0]
            zoho_row = self.zoho_df[self.zoho_df[key_col].astype(str) == str(key)].iloc[0]
            
            row_mismatches = {}
            for col in self.active_mapping.values():
                val_src = source_row[col]
                val_zoho = zoho_row[col]
                
                # Check mismatch with fuzzy logic for strings
                if not self._is_match(val_src, val_zoho):
                    row_mismatches[col] = {"source": str(val_src), "zoho": str(val_zoho)}
            
            if row_mismatches:
                mismatches.append({"key": key, "mismatches": row_mismatches})

        return {
            "summary": {
                "source_total": source_count,
                "zoho_total": zoho_count,
                "matched_records": len(common_keys),
                "missing_in_zoho_count": len(missing_in_zoho),
                "extra_in_zoho_count": len(extra_in_zoho),
                "mismatch_count": len(mismatches)
            },
            "missing_in_zoho_samples": missing_in_zoho[:15],
            "extra_in_zoho_samples": extra_in_zoho[:15],
            "mismatch_samples": mismatches[:15]
        }

    def _is_match(self, v1: Any, v2: Any) -> bool:
        """Compares values, using fuzzy matching for strings."""
        if pd.isna(v1) and pd.isna(v2):
            return True
        if pd.isna(v1) or pd.isna(v2):
            return False
            
        s1, s2 = str(v1).strip(), str(v2).strip()
        
        if s1 == s2:
            return True
            
        # Try numeric comparison if both are digits
        try:
            if float(v1) == float(v2):
                return True
        except:
            pass
            
        # Fuzzy string match
        if len(s1) > 2 and len(s2) > 2:
            score = fuzz.ratio(s1.lower(), s2.lower())
            if score >= self.fuzzy_threshold:
                return True
                
        return False

if __name__ == "__main__":
    print("Upgraded Reconciler loaded.")
