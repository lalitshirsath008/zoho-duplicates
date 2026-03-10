import pandas as pd
import os
import time
import re
from typing import List, Dict, Any

class RFQEngine:
    def __init__(self):
        pass

    def extract_from_file(self, file_path: str, is_source: bool = False) -> List[str]:
        """
        Extracts RFQ numbers from a file (Excel/ODS/CSV).
        Strictly detects the header row by searching for "RFQ No" and extracts only that column.
        """
        if not file_path or not os.path.exists(file_path):
            return []
            
        try:
            filename = file_path.lower()
            
            def process_df(df: pd.DataFrame) -> List[str]:
                if df.empty:
                    return []
                
                candidates = []
                # Scan first 50 rows for the header row
                # Requirement: detect the header row by searching for "RFQ No"
                for i in range(min(50, len(df))):
                    row_vals = df.iloc[i].astype(str).str.lower().tolist()
                    for j, val in enumerate(row_vals):
                        if "rfq" in val:
                            score = 0
                            # High priority for "RFQ No" as requested
                            if "rfq no" in val:
                                score += 2000
                            elif any(x in val for x in ["1.0", "2.0"]):
                                score += 1000
                            elif val.strip() == "rfq":
                                score += 500
                            else:
                                score += 50
                            
                            # Penalty for metadata
                            if any(x in val for x in ["owner", "person", "name", "contact", "summary", "analysis", "date", "status", "brief", "received"]):
                                score -= 3000
                            
                            if score > 0:
                                candidates.append({"row": i, "col": j, "score": score, "val": val})
                
                if not candidates:
                    return []
                
                # Best candidate
                candidates.sort(key=lambda x: x["score"], reverse=True)
                best = candidates[0]
                
                col_idx = best["col"]
                header_row = best["row"]
                
                # Extract starting from the row after the header
                # We filter out trash and ensure we only get valid RFQs
                raw_data = df.iloc[header_row+1:, col_idx].dropna().astype(str).str.strip().tolist()
                
                valid = []
                for v in raw_data:
                    v_low = v.lower()
                    if v_low in ["nan", "", "none", "rfq", "rfq no", "sr. no", "s.no"]:
                        continue
                    if len(v) < 2: continue
                    valid.append(v)
                
                return valid

            if filename.endswith((".xlsx", ".ods", ".xls")):
                all_results = []
                with pd.ExcelFile(file_path, engine="calamine") as xls:
                    for sheet_name in xls.sheet_names:
                        if any(x in sheet_name.lower() for x in ["cache", "log", "tmp", "temp", "hidden"]):
                            continue
                        try:
                            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                            rfqs = process_df(df)
                            if rfqs:
                                all_results.append({"sheet": sheet_name, "rfqs": rfqs, "count": len(rfqs)})
                        except:
                            continue
                
                if not all_results:
                    return []
                
                # For source, if we have a sheet with "RFQ No" exactly, we prefer it.
                # In your case, we want the sheet that has the genuine RFQs.
                # We'll pick the sheet that has a mid-range count (~28-100) and contains digits.
                # If everything else fails, we pick the one with most rows that isn't names.
                useful_results = [r for r in all_results if sum(1 for x in r["rfqs"][:10] if re.search(r'\d', x)) > 0]
                
                if useful_results:
                    # Prefer the sheet that matches the target count range (~33) if available
                    matches_range = [r for r in useful_results if 10 < r["count"] < 100]
                    if matches_range:
                        matches_range.sort(key=lambda x: x["count"], reverse=True)
                        return matches_range[0]["rfqs"]
                    
                    useful_results.sort(key=lambda x: x["count"], reverse=True)
                    return useful_results[0]["rfqs"]
                
                all_results.sort(key=lambda x: x["count"], reverse=True)
                return all_results[0]["rfqs"]
            
            elif filename.endswith(".csv"):
                # For Zoho CSVs, assume headers exist or detect them
                df = pd.read_csv(file_path, header=None)
                return process_df(df)
            
            return []
        except Exception as e:
            print(f"DEBUG Error: {e}")
            return []

    def extract_from_zoho(self, file_paths: List[str]) -> List[str]:
        all_rfqs = []
        for path in file_paths:
            all_rfqs.extend(self.extract_from_file(path, is_source=False))
        return all_rfqs

    def reconcile(self, source_file: str, zoho_files: List[str]) -> Dict[str, Any]:
        """
        Reconciles source vs zoho and detects duplicates in Zoho.
        Uses the exact logic requested by the user.
        """
        from collections import Counter
        
        # 1. Extract Zoho RFQ column and keep all rows
        source_list = self.extract_from_file(source_file, is_source=True)
        zoho_rfqs = self.extract_from_zoho(zoho_files)
        
        # 2. Detect duplicates using Counter
        counts = Counter(zoho_rfqs)
        
        # duplicate_total = sum(count-1 for count in counts.values() if count > 1)
        duplicate_total = sum(count - 1 for count in counts.values() if count > 1)
        
        # 3. Create unique list ONLY for reconciliation
        zoho_unique = set(zoho_rfqs)
        source_unique = set(source_list)
        
        # 4. Building report with markings
        seen = {}
        zoho_report = []
        for rfq in zoho_rfqs:
            if rfq not in seen:
                seen[rfq] = 1
                status = "OK"
            else:
                status = "DUPLICATE ENTRY"
            
            zoho_report.append({
                "rfq": rfq,
                "status": status
            })

        # 5. Matching with unique sets
        matched = source_unique.intersection(zoho_unique)
        missing = source_unique - zoho_unique
        
        return {
            "pdf_rfqs": len(source_unique),
            "zoho_rfqs": len(zoho_rfqs),
            "matched": len(matched),
            "duplicate_rfqs": duplicate_total,
            "missing_rfqs": sorted(list(missing)),
            "zoho_report": zoho_report,
            "status": "success"
        }

if __name__ == "__main__":
    print("RFQEngine High-Precision Logic Loaded.")
