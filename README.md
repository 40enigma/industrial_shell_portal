# QADRI GROUP — Industrial Shell Data Retrieval, Casting Envelope & Quality Intelligence Portal

<div align="center">
  <img src="frontend/qadri_logo.svg" alt="Qadri Group Logo" width="120" />
  <h3>QADRI GROUP</h3>
  <p><strong>Foundry Shell & Casting Quality Intelligence Platform</strong></p>
</div>

---

## 🌟 Overview & Core Capabilities

The **Qadri Group Industrial Shell Portal** is a production foundry engineering platform built for dimensional casting stock evaluation, machining envelope yield optimization, quality defect Pareto analytics, multi-year historical dataset ingestion, and selective technical document retrieval.

### 1. 🔍 Dimensional Search & Machining Stock Envelope Calculator
- **Multi-Mode Dimensional Search**:
  - **Finish Size Mode**: Match against target finished (machined) blueprint dimensions ($\text{OD}$, $\text{ID}$, $\text{Length}$, $\text{Wall Thickness}$) with customizable tolerance margins ($\pm 0\text{--}50\,\text{mm}$).
  - **Casted Size Mode**: Match against raw as-cast stock dimensions.
  - **Auto Match Mode**: Concurrently evaluates both finished targets and raw stock.
  - **Machining Stock Envelope & Yield Calculator**: Determines whether a raw casting stock size encompasses the required finish geometry given specified radial $\text{OD}$/$\text{ID}$ allowances and end-facing cuts. Computes volumetric material utilization yield ($\%$):
    $$\text{Yield } (\%) = \frac{(\text{Target OD}^2 - \text{Target ID}^2) \times \text{Target Length}}{(\text{Cast OD}^2 - \text{Cast ID}^2) \times \text{Cast Length}} \times 100$$
- **Signed Delta Badges**: Real-time indicators showing exact dimension differences (e.g. $\Delta +2.0\,\text{mm}$, $\Delta -1.5\,\text{mm}$).
- **Real-Time 2D SVG Cross-Section Visualizer**: Interactive concentric blueprint rendering depicting as-cast raw stock, finished machined boundaries, and inner bore voids.

---

### 2. 📦 Job Dossier Center & Selective File Download (Single / ZIP)
- **Direct Job Lookup**: Search any Job Number (e.g. `SE24-BSCM-0025`, `SE23-`), Drawing Number, or IDM code.
- **Selective File Checklists**: Every matched shell displays all linked source files:
  - 📊 **M&Q Technical Workbooks** (`.xls` / `.xlsx` with per-shell metallurgy sub-sheets)
  - 🔥 **Actual Casting Log Records** (shifter weights, date, mold/core sand processes)
  - 🛡️ **External QDAR Defect Reports** (QA inspector tickets, customer names, detection stages)
  - ⚙️ **Internal QDAR Defect Reports** (shop floor inspection and rework tracking)
  - 📄 **Auto-Generated Technical Dossier Summary** (`.txt`)
- **Flexible Downloads**:
  - Download individual files directly with the highlighted Job Number prefix.
  - Select any combination of checkboxes and download as a clean, standardized ZIP bundle (e.g. `[JOB_SE24-BSCM-0025]_Selected_Files.zip`).

---

### 3. 📊 Quality Intelligence & Defect Analytics
- **Pareto Defect Distribution**: Visualizes defect frequency and cumulative impact $\%$ based on the $80/20$ Pareto principle.
- **Monthly Casting Volume & Tonnage**: Tracks manufactured shell counts and shifting tonnage across monthly production cycles.
- **Alloy Grade Scrap & Rework Matrix**: Evaluates rejection and rework rates categorized by metallurgical alloy specification (e.g., `QAST-ALLOY 2.0`, `QAST-ALLOY 2.1`, `C.I Mill Roller 2017`).
- **Foundry Lot Quality Heatmap**: Color-coded density matrix across manufacturing lots (Lot #1 through Lot #28+).
- **Molding & Core Process Distribution**: Process breakdown for Alpha Set, Dolomite, and custom riser setups.

---

### 4. 🗄️ Multi-Year Ingestion Manager & Terminal Worker
- **Web-Based ZIP Upload**: Drag-and-drop full-year archives (`2022.zip`, `2023.zip`, `2024.zip`).
- **Auto-Discovery ETL Pipeline**: Automatically resolves nested directory structures (`M&Q Data`, `QDARS`, `Actual Casting Log`), cleans and normalizes records, and executes heuristic 3-pass linking.
- **Live Terminal Console**: Real-time streamed progress, record counts, and error tracking.

---

## 🚀 How to Run the Portal & Make It Accessible

### 1. Prerequisites
- Python 3.10+ (Python 3.11 / 3.12 / 3.14 tested)
- Virtual environment with required dependencies

### 2. Activate Virtual Environment & Install Dependencies
Open **PowerShell** or **Command Prompt** in the project directory:

```powershell
# Navigate to the portal directory
cd "d:\ML\Qadri ML project\industrial_shell_portal"

# Activate the virtual environment
..\venv\Scripts\Activate.ps1

# Install requirements (if needed)
pip install -r requirements.txt
```

---

### 3. Launching the Local Server

#### Option A: Run on Localhost (Only accessible on your computer)
```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and visit: **`http://localhost:8000`**

#### Option B: Make Accessible Across Local Network (Wi-Fi / LAN / Foundry Devices)
To access the portal from other computers, laptops, tablets, or mobile phones on the same Wi-Fi / office network:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

1. Find your machine's Local IP Address:
   ```powershell
   ipconfig
   # Look for "IPv4 Address", e.g. 192.168.1.50 or 10.0.0.15
   ```
2. Open any browser on any device connected to the same network and navigate to:
   **`http://YOUR_LOCAL_IP:8000`** (e.g. `http://192.168.1.50:8000`)

---

## 🌐 Web Application Pages & Routes

The portal is organized into dedicated multi-page views accessible from the top navigation bar:

| Route / URL | Page Description |
| :--- | :--- |
| **`/`** or **`/search`** | **Shell Search & Machining Stock Envelope Calculator** (2D SVG cross-section, dimensional search, tolerance slider, selective download modal) |
| **`/job-lookup`** or **`/dossier`** | **Job Dossier & Document Download Center** (direct Job Number lookup, full specs, file checklist, 1-click single/ZIP download) |
| **`/quality`** or **`/analytics`** | **Foundry Quality & Defect Intelligence** (Pareto chart, monthly tonnage, alloy scrap rates, lot quality heatmap) |
| **`/ingestion`** or **`/upload-manager`** | **Archive Ingestion & Year Manager** (archive drag-and-drop upload, live terminal streamer, past batch history) |

---

## 🛠️ CLI Batch Ingestion Commands

If you prefer to run data ingestion from the command line:

```powershell
# Ingest full dataset
python -m etl.seed_db

# Ingest specific year with custom directories
python -m etl.import_batch --year 2023 --mq-dir "data/raw/2023/M&Q 2023 Data" --qdar-dir "data/raw/2023/QDARS 2023"
```

---

## 📂 Project Architecture

```
industrial_shell_portal/
│
├── backend/
│   ├── main.py                  # FastAPI app entry point & multi-page routers
│   ├── config.py                # Central path and database configuration
│   ├── routes/
│   │   ├── search.py            # Dimensional search & CSV export API
│   │   ├── documents.py         # File inspection, selective ZIP & download API
│   │   ├── analytics.py         # Pareto, alloy scrap, and lot heatmap API
│   │   └── upload.py            # Archive ZIP upload & background ETL worker
│   └── services/
│       ├── matcher.py           # Proximity search, deltas & stock envelope engine
│       └── normalizer.py        # Job numbers, tokenizers & alphanumeric cleaners
│
├── database/
│   ├── db.py                    # SQLAlchemy SQLite engine & session setup
│   └── models.py                # Shell, Document, and IngestionBatch ORM models
│
├── etl/
│   ├── parse_mq_files.py        # M&Q workbook & metallurgy parser (with auto-directory discovery)
│   ├── clean_casting_log.py     # Actual Casting Log parser & weight tracker
│   ├── parse_qad_files.py       # QDAR defect ticket parser (External & Internal)
│   ├── seed_db.py               # 3-Pass heuristic matcher & database seeder
│   └── import_batch.py          # Standalone CLI batch importer
│
├── frontend/
│   ├── index.html               # Main Shell Search & Stock Calculator page
│   ├── quality.html             # Quality Intelligence & Defect Analytics page
│   ├── ingestion.html           # Archive Ingestion & Live Terminal page
│   ├── job_lookup.html          # Job Dossier & Document Download Center page
│   ├── qadri_logo.svg           # Official Qadri Group vector emblem
│   ├── style.css                # Qadri Group executive corporate theme (Dark/Light)
│   └── app.js                   # Application state, 2D SVG canvas & download modal logic
│
├── data/
│   ├── industrial_shells.db     # SQLite database (1,460+ shells, 2,380+ linked documents)
│   ├── raw/                     # Uploaded and extracted archives partitioned by year
│   └── processed/               # Intermediate ETL JSON mappings
│
├── .gitignore                   # Complete GitHub ignore rules (binaries, databases, venv)
└── requirements.txt             # Project dependencies
```

---

## 🧪 Testing & Validation

To verify all system endpoints and API responses:

```powershell
python -c "from fastapi.testclient import TestClient; from backend.main import app; c = TestClient(app); print('Status:', c.get('/health').json())"
```
