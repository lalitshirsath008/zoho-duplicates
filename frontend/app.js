const API_BASE = window.location.port === '8005' ? window.location.origin : 'http://localhost:8005';
console.log("Using API Base:", API_BASE);

let state = {
    sourceFile: null,
    zohoFiles: []
};

// UI Elements
const sourceInput = document.getElementById('excel-input');
const zohoInput = document.getElementById('zoho-input');
const sourceDrop = document.getElementById('excel-drop');
const zohoDrop = document.getElementById('zoho-drop');
const runBtn = document.getElementById('run-btn');
const resultsSection = document.getElementById('results-section');

// Event Listeners for Uploads
sourceDrop.onclick = () => sourceInput.click();
zohoDrop.onclick = () => zohoInput.click();

sourceInput.onchange = (e) => {
    if (e.target.files.length > 0) {
        state.sourceFile = e.target.files[0];
        document.getElementById('excel-info').innerText = `Source: ${state.sourceFile.name}`;
    }
};

zohoInput.onchange = (e) => {
    if (e.target.files.length > 0) {
        state.zohoFiles = Array.from(e.target.files);
        document.getElementById('zoho-info').innerText = `${state.zohoFiles.length} file(s) selected`;
    }
};

// Drag and Drop Logic
[sourceDrop, zohoDrop].forEach(dropArea => {
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.style.borderColor = 'var(--primary)';
        dropArea.style.background = 'rgba(99, 102, 241, 0.1)';
    });
    dropArea.addEventListener('dragleave', () => {
        dropArea.style.borderColor = 'var(--border)';
        dropArea.style.background = 'transparent';
    });
});

sourceDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    sourceDrop.style.borderColor = 'var(--border)';
    sourceDrop.style.background = 'transparent';
    if (e.dataTransfer.files.length > 0) {
        state.sourceFile = e.dataTransfer.files[0];
        document.getElementById('excel-info').innerText = `Source: ${state.sourceFile.name}`;
    }
});

zohoDrop.addEventListener('drop', (e) => {
    e.preventDefault();
    zohoDrop.style.borderColor = 'var(--border)';
    zohoDrop.style.background = 'transparent';
    if (e.dataTransfer.files.length > 0) {
        state.zohoFiles = Array.from(e.dataTransfer.files);
        document.getElementById('zoho-info').innerText = `${state.zohoFiles.length} file(s) dropped`;
    }
});

runBtn.onclick = async () => {
    if (!state.sourceFile || state.zohoFiles.length === 0) {
        alert("Please select both a Source file (Excel/ODS/CSV) and at least one Zoho CSV.");
        return;
    }

    runBtn.disabled = true;
    runBtn.innerHTML = '<span class="spinner"></span> Reconciling RFQs...';
    resultsSection.style.display = 'none';

    try {
        const formData = new FormData();
        formData.append('source_file', state.sourceFile);
        
        state.zohoFiles.forEach(file => {
            formData.append('zoho_files', file);
        });

        const response = await fetch(`${API_BASE}/reconcile`, {
            method: 'POST',
            body: formData
        });

        const contentType = response.headers.get("content-type");
        if (!response.ok) {
            if (contentType && contentType.includes("application/json")) {
                const err = await response.json();
                throw new Error(err.detail || "Reconciliation failed");
            } else {
                const text = await response.text();
                console.error("Server Error:", text);
                throw new Error("Internal Server Error (500). Please check if Zoho CSVs have the 'RFQ No' column.");
            }
        }

        if (!contentType || !contentType.includes("application/json")) {
            throw new Error("Invalid response from server (Not JSON)");
        }

        const data = await response.json();
        console.log("API response:", data);

        // Requirement 4 & 6: Validation checks
        if (data.status === "error") {
            alert(data.error_message);
            return; // Stop processing if source extraction failed
        }

        if (data.status === "mismatch") {
            alert(data.error_message);
        }

        displayResults(data);
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
        console.error("Fetch Error:", err);
        alert(`Error: ${err.message}`);
    } finally {
        runBtn.disabled = false;
        runBtn.innerText = "Run RFQ Reconciliation";
    }
};

function displayResults(data) {
    document.getElementById('stat-excel').innerText = (data.pdf_rfqs || 0).toLocaleString();
    document.getElementById('stat-zoho').innerText = (data.zoho_rfqs || 0).toLocaleString();
    document.getElementById('stat-matched').innerText = (data.matched || 0).toLocaleString();
    document.getElementById('stat-mismatches').innerText = (data.missing_rfqs?.length || 0).toLocaleString();
    document.getElementById('stat-duplicates').innerText = (data.duplicate_rfqs || 0).toLocaleString();

    // 1. Render Missing RFQ Report
    const reportContent = document.getElementById('report-content');
    const missing = data.missing_rfqs || [];
    
    if (missing.length === 0) {
        reportContent.innerHTML = `
            <div style="text-align: center; padding: 2rem; background: rgba(34, 197, 94, 0.05); border-radius: 12px; border: 2px dashed var(--success);">
                <p style="color: var(--success); font-weight: bold;">🎉 All RFQs Found!</p>
            </div>
        `;
    } else {
        reportContent.innerHTML = `
            <div style="overflow-x: auto;">
                <table class="data-table" style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="text-align: left;">#</th>
                            <th style="text-align: left;">Missing RFQ Number (from Source)</th>
                            <th style="text-align: right;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${missing.map((rfq, idx) => `
                            <tr>
                                <td style="color: var(--text-muted)">${idx + 1}</td>
                                <td style="font-family: monospace; font-weight: bold; color: var(--error)">${rfq}</td>
                                <td style="text-align: right;"><span style="background: rgba(239, 68, 68, 0.1); color: var(--error); padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">NOT IN ZOHO</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    // 2. Render Zoho Duplicate Report
    const duplicateContent = document.getElementById('duplicate-content');
    const zohoReport = data.zoho_report || [];

    if (zohoReport.length === 0) {
        duplicateContent.innerHTML = `<p style="text-align: center; color: var(--text-muted); padding: 1rem;">No Zoho data available.</p>`;
    } else {
        duplicateContent.innerHTML = `
            <div style="overflow-x: auto;">
                <table class="data-table" style="width: 100%;">
                    <thead>
                        <tr>
                            <th style="text-align: left;">#</th>
                            <th style="text-align: left;">Zoho RFQ Entry</th>
                            <th style="text-align: right;">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${zohoReport.map((item, idx) => `
                            <tr style="${item.status === 'DUPLICATE ENTRY' ? 'background: rgba(245, 158, 11, 0.03);' : ''}">
                                <td style="color: var(--text-muted)">${idx + 1}</td>
                                <td style="font-family: monospace; font-weight: ${item.status === 'DUPLICATE ENTRY' ? 'bold' : 'normal'}; color: ${item.status === 'DUPLICATE ENTRY' ? '#f59e0b' : 'inherit'}">${item.rfq}</td>
                                <td style="text-align: right;">
                                    <span style="background: ${item.status === 'DUPLICATE ENTRY' ? 'rgba(245, 158, 11, 0.1)' : 'rgba(34, 197, 94, 0.1)'}; 
                                                 color: ${item.status === 'DUPLICATE ENTRY' ? '#f59e0b' : 'var(--success)'}; 
                                                 padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">
                                        ${item.status}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
}
