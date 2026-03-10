import pandas as pd
import os

# Create data directory if not exists
os.makedirs("data", exist_ok=True)

# 1. Zoho Datasets (Split into 2 files to test merging)
zoho_data_1 = {
    "Invoice Number": ["INV-101", "INV-102"],
    "Date": ["2024-03-01", "2024-03-02"],
    "Qty": [50, 75]
}
zoho_data_2 = {
    "Invoice Number": ["INV-103", "INV-104", "INV-105"],
    "Date": ["2024-03-03", "2024-03-04", "2024-03-05"],
    "Qty": [100, 125, 140] # INV-105 mismatch (should be 150)
}

pd.DataFrame(zoho_data_1).to_csv("data/zoho_part1.csv", index=False)
pd.DataFrame(zoho_data_2).to_csv("data/zoho_part2.csv", index=False)

# 2. Source Data (Excel with normalization test)
source_data = {
    "Invoice_No": ["INV-101", "INV-102", "INV-103", "INV-104", "INV-105"],
    "Dispatch Date": ["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"],
    "Dispatch Qty": [50, 75, 100, 125, 150],
    "Status": ["Shipped", "Shipped", "Shipped", "Delivered", "Delivered"]
}

df_source = pd.DataFrame(source_data)
df_source.to_excel("data/upgraded_source.xlsx", sheet_name="Dispatch_Register", index=False)

# 3. Note on PDF: For testing PDF, the user can use any PDF with a table. 
# Since generating a PDF requires reportlab or similar, I'll stick to Excel/CSV for now 
# but the code is ready for PDF via pdfplumber.

print("Upgraded sample data (Multi-CSV and Excel) generated.")
