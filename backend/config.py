"""
Configuration module — Central path settings for the Industrial Shell Portal.
All paths are resolved from the project root directory.
"""
from pathlib import Path

# Project root (industrial_shell_portal/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Original raw data location (dynamically resolved with fallback)
_workspace_root = PROJECT_ROOT.parent
_candidate_data_dirs = [
    _workspace_root / "Data For Project (Mill Roller Shell Data based)",
    PROJECT_ROOT / "data" / "raw",
]
ORIGINAL_DATA_DIR = next((p for p in _candidate_data_dirs if p.exists()), _candidate_data_dirs[0])

# Dynamic resolution for 2025 raw folders (handles both 'M& Q 2025 Data' and 'M&Q 2025 Data')
def _find_dir_by_pattern(parent: Path, patterns: list[str]) -> Path:
    if parent.exists():
        for pat in patterns:
            matches = list(parent.glob(pat))
            if matches:
                return matches[0]
            # Also check subfolder for year (e.g. 2025/)
            year_matches = list(parent.glob(f"*/{pat}"))
            if year_matches:
                return year_matches[0]
    return parent / patterns[0].replace("*", "")

RAW_MQ_DIR = _find_dir_by_pattern(ORIGINAL_DATA_DIR, ["*M*Q*2025*Data*", "*MQ*2025*"])
RAW_QDAR_DIR = _find_dir_by_pattern(ORIGINAL_DATA_DIR, ["*QDAR*2025*", "*QDR*2025*"])

# Database
DB_PATH = DATA_DIR / "industrial_shells.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Frontend
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
