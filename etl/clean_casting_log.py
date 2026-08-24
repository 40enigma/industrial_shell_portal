"""
Casting Log Parser — Ingestion & Cleaning of 'Actual Casting Log 2025.xlsx'.

Features:
1. High-speed streaming parser (openpyxl read_only with automatic empty-row cutoff).
2. Normalizes dates (e.g. '2025-02-12' from datetime objects or strings).
3. Extracts actual measured weight, allowable job card weight, calculated weight, and weight variance.
4. Extracts tooling, pattern, and molding process metadata:
   - Mold process (Alpha Set, etc.)
   - Core process (Alpha Set, Dolomite, etc.)
   - Riser % & Technology
   - Simulation paths & shaft fitting
   - Size with Contraction Allowance (CA) and core box sizes.
5. Normalizes job numbers, piece numbers, and dimensional parameters.

Output: data/processed/cleaned_casting_log_2025.json
"""
import datetime
import json
import logging
import re
import sys
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.normalizer import (
    normalize_job_number, normalize_piece_number, extract_base_job
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "cleaned_casting_log_2025.json"

CASTING_LOG_CANDIDATES = [
    RAW_DIR / "Actual Casting Log 2025.xlsx",
    Path(r"d:\ML\Qadri ML project\Data For Project (Mill Roller Shell Data based)") / "Actual Casting Log 2025.xlsx",
]


def safe_float(val) -> float | None:
    """Convert cell value to float or return None."""
    if val is None or val == "":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(",", "")
    if "/" in s and all(p.strip().isdigit() for p in s.split("/")):
        parts = s.split("/")
        if len(parts) == 2:
            try:
                return float(parts[0]) / float(parts[1])
            except (ValueError, ZeroDivisionError):
                pass
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


def safe_int(val) -> int | None:
    """Convert cell value to int or return None."""
    f = safe_float(val)
    return int(round(f)) if f is not None else None


def safe_str(val) -> str | None:
    """Clean string cell value."""
    if val is None or val == "" or str(val).strip() == "None":
        return None
    s = str(val).strip()
    if s.endswith(".0"):
        try:
            float(s)
            s = s[:-2]
        except ValueError:
            pass
    return s if s else None


def format_date_str(val) -> str | None:
    """Normalize date value to YYYY-MM-DD string."""
    if val is None or val == "" or str(val).strip() == "None":
        return None
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    # Check for YYYY-MM-DD pattern
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    # Check for DD-MM-YYYY pattern
    m = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return s if len(s) >= 4 else None


def normalize_month(val: str | None) -> str | None:
    """Normalize month name to standard 3-letter abbreviation."""
    if not val or str(val).strip() == "" or str(val).strip().lower() == "none":
        return None
    v = str(val).strip().lower()
    mapping = {
        "jan": "Jan", "january": "Jan",
        "feb": "Feb", "february": "Feb",
        "mar": "Mar", "march": "Mar",
        "apr": "Apr", "april": "Apr",
        "may": "May",
        "jun": "Jun", "june": "Jun",
        "jul": "Jul", "july": "Jul",
        "aug": "Aug", "august": "Aug",
        "sep": "Sep", "september": "Sep", "sept": "Sep",
        "oct": "Oct", "october": "Oct",
        "nov": "Nov", "november": "Nov",
        "dec": "Dec", "december": "Dec",
    }
    return mapping.get(v, str(val).strip().capitalize())


def normalize_process_name(val: str | None) -> str | None:
    """Standardize molding and core sand process names (e.g. 'Alpha set' -> 'Alpha Set', 'Ms Pipe' -> 'MS Pipe')."""
    if not val or str(val).strip() == "" or str(val).strip().lower() == "none":
        return None
    s = str(val).strip()
    if s.lower() == "alpha set":
        return "Alpha Set"
    if s.lower() == "co2 + chills":
        return "Co2 + Chills"
    if "ms pipe" in s.lower():
        s = re.sub(r"(?i)ms pipe", "MS Pipe", s)
    return s


def calculate_wall_thickness(od: float | None, id_dim: float | None) -> float | None:
    """Compute radial wall thickness = (OD - ID) / 2."""
    if od is not None and id_dim is not None and od > id_dim and id_dim >= 0:
        return round((od - id_dim) / 2.0, 2)
    return None


def parse_casting_log(filepath: Path | str, year: int = 2025) -> list[dict]:
    """
    Parse Actual Casting Log Excel file with streaming iterator.
    Handles the 2025 sheet and dynamic multi-sheet configurations.
    """
    path = Path(filepath)
    if not path.exists():
        log.error(f"Casting log not found: {path}")
        return []

    log.info(f"Opening Casting Log: {path.name} (Year: {year})")

    try:
        wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    except Exception as e:
        log.error(f"Failed to open workbook {path}: {e}")
        return []

    target_sheet = None
    year_str = str(year)
    for sn in wb.sheetnames:
        if year_str in sn or "casting" in sn.lower() or "log" in sn.lower():
            target_sheet = sn
            break
    if not target_sheet:
        target_sheet = wb.sheetnames[0]

    sheet = wb[target_sheet]
    log.info(f"Parsing sheet: '{target_sheet}'...")

    records = []
    consecutive_empty = 0

    for row_idx, row in enumerate(sheet.iter_rows(values_only=True)):
        # Skip header rows (rows 0 and 1)
        if row_idx < 2:
            continue

        if not any(row):
            consecutive_empty += 1
            if consecutive_empty > 20:
                # Stop parsing once we hit the end of table data
                break
            continue

        consecutive_empty = 0

        # Primary Job Number (Col 4)
        job_raw = row[4] if len(row) > 4 else None
        job_number = normalize_job_number(job_raw)
        if not job_number:
            continue

        shell_name = safe_str(row[5]) if len(row) > 5 else None
        if not shell_name:
            continue

        month = normalize_month(safe_str(row[0])) if len(row) > 0 else None
        lot_number = safe_int(row[1]) if len(row) > 1 else None
        serial_number = safe_int(row[2]) if len(row) > 2 else None
        idm_number = safe_str(row[3]) if len(row) > 3 else None
        drawing_number = safe_str(row[6]) if len(row) > 6 else None
        shell_type = safe_str(row[7]) if len(row) > 7 else None
        piece_number = normalize_piece_number(safe_str(row[8])) if len(row) > 8 else None

        # Dimensions
        finish_od = safe_float(row[9]) if len(row) > 9 else None
        finish_id = safe_float(row[10]) if len(row) > 10 else None
        finish_len = safe_float(row[11]) if len(row) > 11 else None

        cast_od = safe_float(row[12]) if len(row) > 12 else None
        cast_id = safe_float(row[13]) if len(row) > 13 else None
        cast_len = safe_float(row[14]) if len(row) > 14 else None

        wall_thickness = calculate_wall_thickness(finish_od, finish_id)
        cast_wall_thickness = calculate_wall_thickness(cast_od, cast_id)

        # Tooling & Pattern
        pattern_ca = safe_float(row[15]) if len(row) > 15 else None
        core_box = safe_float(row[20]) if len(row) > 20 else None
        riser_pct = safe_float(row[24]) if len(row) > 24 else None
        simulation_path = safe_str(row[27]) if len(row) > 27 else None

        # Weights (kg)
        calculated_weight = safe_float(row[28]) if len(row) > 28 else None
        job_card_weight = safe_float(row[34]) if len(row) > 34 else None
        weight_diff = safe_float(row[40]) if len(row) > 40 else None
        actual_weight = safe_float(row[41]) if len(row) > 41 else None

        # If weight_diff is not explicitly recorded but actual & job card are present, calculate it
        if weight_diff is None and actual_weight is not None and job_card_weight is not None:
            weight_diff = round(actual_weight - job_card_weight, 2)

        # Casting Date & Foundry Tech
        cast_date = format_date_str(row[42]) if len(row) > 42 else None
        mat_standard = safe_str(row[43]) if len(row) > 43 else None
        technology = safe_str(row[44]) if len(row) > 44 else None
        shaft_fitting = safe_str(row[45]) if len(row) > 45 else None
        core_process = normalize_process_name(safe_str(row[46])) if len(row) > 46 else None
        mold_process = normalize_process_name(safe_str(row[47])) if len(row) > 47 else None

        record = {
            "month": month,
            "lot_number": lot_number,
            "serial_number": serial_number,
            "idm_number": idm_number,
            "job_number": job_number,
            "base_job": extract_base_job(job_number),
            "shell_name": shell_name,
            "drawing_number": drawing_number,
            "shell_type": shell_type,
            "piece_number": piece_number,
            "od": finish_od,
            "id_dim": finish_id,
            "length": finish_len,
            "wall_thickness": wall_thickness,
            "cast_od": cast_od,
            "cast_id": cast_id,
            "cast_length": cast_len,
            "cast_wall_thickness": cast_wall_thickness,
            "pattern_size_ca": pattern_ca,
            "core_box": core_box,
            "riser_pct": riser_pct,
            "simulation_path": simulation_path,
            "calculated_weight": calculated_weight,
            "job_card_weight": job_card_weight,
            "actual_weight": actual_weight,
            "weight_diff": weight_diff,
            "weight": job_card_weight or calculated_weight or actual_weight,
            "cast_date": cast_date,
            "material_standard": mat_standard,
            "technology": technology,
            "shaft_fitting": shaft_fitting,
            "core_process": core_process,
            "mold_process": mold_process,
            "data_year": year,
            "file_path": str(path),
            "sheet_name": target_sheet,
        }
        records.append(record)

    log.info(f"Successfully extracted {len(records)} casting log records from {path.name}")
    return records


def find_casting_log_file(custom_path: str | Path | None = None) -> Path | None:
    """Find the casting log file from candidate locations."""
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p

    for candidate in CASTING_LOG_CANDIDATES:
        if candidate.exists():
            return candidate

    # Search in raw data dir
    if RAW_DIR.exists():
        for f in RAW_DIR.glob("*.xlsx"):
            if "casting" in f.name.lower():
                return f

    return None


def main():
    """CLI execution for Casting Log extraction."""
    log.info("=" * 60)
    log.info("ACTUAL CASTING LOG PARSER — Starting")
    log.info("=" * 60)

    casting_log_path = find_casting_log_file()

    if casting_log_path is None:
        log.warning(
            "Actual Casting Log 2025.xlsx NOT FOUND in any candidate location.\n"
            "  Checked:\n" +
            "\n".join(f"    - {p}" for p in CASTING_LOG_CANDIDATES)
        )
        records = []
    else:
        log.info(f"Found Casting Log file at: {casting_log_path}")
        records = parse_casting_log(casting_log_path, year=2025)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False, default=str)

    log.info(f"Saved {len(records)} casting records to {OUTPUT_FILE}")
    log.info("ACTUAL CASTING LOG PARSER — Complete")


if __name__ == "__main__":
    main()
