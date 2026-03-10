# AI Data Reconciliation Tool

This tool automates the process of matching Excel sheets to Zoho Analytics datasets using Gemini AI and performing a detailed reconciliation.

## Features
- **AI-Powered Mapping**: Automatically detects which sheet matches a Zoho CSV export.
- **Smart Column Mapping**: Maps columns even if they have slightly different names.
- **Detailed Reconciliation**: Identifies missing records, extra records, and value mismatches.
- **Modern UI**: Clean, responsive dashboard for easy operation.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   Create a `.env` file in the root directory and add your Google Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Generate Sample Data** (Optional but recommended for testing):
   ```bash
   python generate_sample_data.py
   ```

4. **Run the Backend**:
   ```bash
   python main.py
   ```
   The API will start at `http://localhost:8000`.

5. **Open the Frontend**:
   Simply open `frontend/index.html` in your web browser (or serve it using a local server).

## Usage
1. Upload `data/sample_dispatch.xlsx` in the Excel section.
2. Upload `data/zoho_export.csv` in the Zoho section.
3. Click **Run AI Reconciliation**.
4. View the AI mapping insights and the detailed reconciliation report.
