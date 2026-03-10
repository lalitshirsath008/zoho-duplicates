import pandas as pd
import os

# Create data directory if not exists
os.makedirs("data", exist_ok=True)

# 1. Excel Data (Source)
excel_data = {
    "Invoice_No": ["INV-001", "INV-002", "INV-003", "INV-004", "INV-005"],
    "Dispatch_Date": ["2024-03-01", "2024-03-02", "2024-03-03", "2024-03-04", "2024-03-05"],
    "Dispatch_Qty": [100, 250, 400, 150, 300],
    "Customer": ["Alpha Corp", "Beta Inc", "Gamma Ltd", "Delta Co", "Epsilon Org"]
}

df_excel = pd.DataFrame(excel_data)

# Create a multi-sheet Excel
with pd.ExcelWriter("data/sample_dispatch.xlsx") as writer:
    df_excel.to_excel(writer, sheet_name="Dispatch_Register", index=False)
    # Add dummy sheets to test AI mapping
    pd.DataFrame({"ID": [1,2], "Val": ["A", "B"]}).to_excel(writer, sheet_name="Staff_Logs", index=False)
    pd.DataFrame({"Date": ["2024-01-01"], "Exp": [500]}).to_excel(writer, sheet_name="Expenses", index=False)

# 2. Zoho Data (Target - with discrepancies)
# - Missing INV-003
# - INV-005 has different Qty (290 instead of 300)
# - Added INV-006 (Extra record)
zoho_data = {
    "InvoiceNumber": ["INV-001", "INV-002", "INV-004", "INV-005", "INV-006"],
    "Date": ["2024-03-01", "2024-03-02", "2024-03-04", "2024-03-05", "2024-03-06"],
    "Quantity": [100, 250, 150, 290, 500],
    "ClientName": ["Alpha Corp", "Beta Inc", "Delta Co", "Epsilon Org", "Zeta Ltd"]
}

df_zoho = pd.DataFrame(zoho_data)
df_zoho.to_csv("data/zoho_export.csv", index=False)

print("Sample data generated in 'data/' directory.")
