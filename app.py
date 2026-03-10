import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any

app = FastAPI(title="RFQ Reconciliation API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

from backend.rfq_engine import RFQEngine

@app.post("/reconcile")
async def run_rfq_reconciliation(
    source_file: UploadFile = File(...),
    zoho_files: List[UploadFile] = File(...)
):
    # Requirement 5: JSON response schema
    error_response = {
        "pdf_rfqs": 0,
        "zoho_rfqs": 0,
        "matched": 0,
        "missing_rfqs": []
    }

    # 1. Save Source PDF
    source_path = os.path.join(UPLOAD_DIR, f"source_{source_file.filename}")
    with open(source_path, "wb") as buffer:
        shutil.copyfileobj(source_file.file, buffer)
    
    # 2. Save and collect Zoho Files
    zoho_paths = []
    for zf in zoho_files:
        z_path = os.path.join(UPLOAD_DIR, f"zoho_{zf.filename}")
        with open(z_path, "wb") as buffer:
            shutil.copyfileobj(zf.file, buffer)
        zoho_paths.append(z_path)

    try:
        # 3. Execute RFQ Engine
        engine = RFQEngine()
        result = engine.reconcile(source_path, zoho_paths)
        
        # Requirement 4 trace
        print(f"DEBUG: RFQ Reconciliation complete. Missing: {len(result['missing_rfqs'])}")
        
        return result

    except Exception as e:
        import traceback
        print("DEBUG: RFQ Reconcile Exception:")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error_message": f"Unexpected error: {str(e)}",
            "pdf_rfqs": 0,
            "zoho_rfqs": 0,
            "matched": 0,
            "missing_rfqs": []
        }

# Serving Frontend
@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse("frontend/index.html")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    # Use 8005 as established in previous fixes
    uvicorn.run(app, host="0.0.0.0", port=8005)
