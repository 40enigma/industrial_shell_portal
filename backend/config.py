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

# Original raw data location
ORIGINAL_DATA_DIR = Path(r"d:\ML\Qadri ML project\Data For Project (Mill Roller Shell Data based)")
RAW_MQ_DIR = ORIGINAL_DATA_DIR / "M& Q 2025 Data"
RAW_QDAR_DIR = ORIGINAL_DATA_DIR / "QDARS 2025"

# Database
DB_PATH = DATA_DIR / "industrial_shells.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Frontend
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
