import pandas as pd
import os

file_path = r"c:\Users\Design - RGK\Desktop\Datapipeline\data\uploads\source_ENQUIRY - #RFQ _ LIST (1).ods"

try:
    with pd.ExcelFile(file_path, engine="calamine") as xls:
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet, header=None)
            print(f"--- Searching in sheet: {sheet} ---")
            for i in range(min(50, len(df))):
                for j in range(len(df.columns)):
                    val = str(df.iloc[i, j])
                    if "RFQ" in val.upper():
                        print(f"Found '{val}' at Row {i}, Col {j}")
                        # Print some rows below to see if it's actual RFQ numbers
                        sample = df.iloc[i+1:i+6, j].tolist()
                        print(f"  Sample data below: {sample}")
except Exception as e:
    print(f"Error: {e}")
