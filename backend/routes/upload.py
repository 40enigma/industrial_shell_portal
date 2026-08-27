"""
Web-based Full-Year Archive ZIP Ingestion & Background Processing API.

Allows users to upload .zip archives of historical foundry datasets (2022–2024+),
extracts and organizes workbooks, runs the ETL pipeline asynchronously,
and streams real-time terminal logs to the UI.
"""
import logging
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.db import get_db, SessionLocal
from database.models import IngestionBatch, Shell, Document
from etl.parse_mq_files import parse_all_mq_files
from etl.parse_qad_files import parse_all_qdar_files
from etl.seed_db import seed_shells, seed_qdars

router = APIRouter(prefix="/api/upload", tags=["upload"])
log = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_BASE_DIR = PROJECT_ROOT / "data" / "raw"



def _resolve_data_root(extract_dir: Path, year: int, max_depth: int = 4) -> Path:
    """
    Walk into nested ZIP subfolders to find the actual data directory.

    ZIPs often contain a root folder (e.g. '2023/') so the actual M&Q, QDARS,
    and Casting Log files sit one or more levels deeper than the extraction path.
    This function searches for known data markers and returns the deepest
    directory that contains them.
    """
    def _has_data_markers(d: Path) -> bool:
        """Check if a directory contains M&Q, QDARS, or Casting Log files."""
        for child in d.iterdir():
            name_lower = child.name.lower()
            if child.is_dir() and ("m&q" in name_lower or "m & q" in name_lower or "mq" in name_lower):
                return True
            if child.is_dir() and ("qdar" in name_lower or "qdars" in name_lower):
                return True
            if child.is_file() and "casting" in name_lower and name_lower.endswith((".xlsx", ".xls")):
                return True
            if child.is_dir() and "lot" in name_lower:
                return True
        return False

    # BFS: check current dir, then its subdirectories, up to max_depth levels
    candidates = [extract_dir]
    for _depth in range(max_depth):
        next_level = []
        for candidate in candidates:
            if candidate.is_dir() and _has_data_markers(candidate):
                return candidate
            if candidate.is_dir():
                next_level.extend([c for c in candidate.iterdir() if c.is_dir()])
        candidates = next_level
        if not candidates:
            break

    return extract_dir  # Fallback to original


def run_background_ingestion(batch_id: int, year: int, extract_dir: Path):
    """Background worker that executes extraction, parsing, and seeding."""
    db: Session = SessionLocal()
    batch = db.query(IngestionBatch).filter(IngestionBatch.id == batch_id).first()
    if not batch:
        db.close()
        return

    logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Started ingestion for Year {year}..."]
    try:
        # Auto-detect the real data root inside the extracted archive
        data_root = _resolve_data_root(extract_dir, year)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Resolved data root: {data_root}")
        
        # Clean up any existing records for this specific year to ensure idempotent re-ingestion
        db.query(Document).filter(Document.data_year == year).delete()
        db.query(Shell).filter(Shell.data_year == year).delete()
        db.commit()
        
        # Check for M&Q workbooks
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning for M&Q workbooks...")
        mq_records = parse_all_mq_files(mq_dir=data_root, year=year)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Extracted {len(mq_records)} valid M&Q shell records with metallurgy.")
        batch.total_shells = len(mq_records)
        batch.log_output = "\n".join(logs)
        db.commit()

        # Check for Casting Log workbooks
        casting_records = []
        cast_candidates = (
            list(data_root.glob(f"*Casting*{year}*.xls*")) +
            list(data_root.glob(f"*casting*{year}*.xls*")) +
            list(data_root.glob(f"*Log*{year}*.xls*")) +
            list(data_root.glob("*Casting*.xls*")) +
            list(data_root.glob("*casting*.xls*")) +
            list(data_root.glob("*Log*.xls*")) +
            list(data_root.rglob(f"*Casting*{year}*.xls*")) +
            list(data_root.rglob(f"*casting*{year}*.xls*")) +
            list(data_root.rglob(f"*Log*{year}*.xls*")) +
            list(data_root.rglob("*Casting*.xls*")) +
            list(data_root.rglob("*casting*.xls*")) +
            list(data_root.rglob("*Log*.xls*"))
        )
        seen_paths = set()
        for cast_candidate in cast_candidates:
            if cast_candidate.exists() and not cast_candidate.name.startswith("~$") and cast_candidate not in seen_paths:
                seen_paths.add(cast_candidate)
                from etl.clean_casting_log import parse_casting_log
                records = parse_casting_log(cast_candidate, year=year)
                if records:
                    casting_records = records
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Extracted {len(casting_records)} actual casting log records from {cast_candidate.name}.")
                    break

        # Seed shells (merged with casting data)
        job_base, tokens, drawings = seed_shells(db, mq_records=mq_records, casting_records=casting_records)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Seeded Shell records (with Casting Intelligence) into SQLite database.")

        # Check for QDAR workbooks
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Scanning for QDAR quality records...")
        qdar_records = parse_all_qdar_files(qdar_dir=data_root, year=year)
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Extracted {len(qdar_records)} QDAR quality records.")

        if qdar_records:
            seed_qdars(db, job_base, tokens, drawings, qdar_records=qdar_records)
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Linked QDAR defect reports to shells using heuristic matching.")

        doc_count = db.query(Document).filter(Document.data_year == year).count()
        batch.total_documents = doc_count
        batch.total_shells = db.query(Shell).filter(Shell.data_year == year).count()
        batch.status = "COMPLETED"
        cast_doc_count = db.query(Document).filter(Document.data_year == year, Document.doc_type == "CASTING_LOG").count()
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Ingestion completed successfully! {batch.total_shells} shells, {batch.total_documents} documents ({cast_doc_count} Casting Logs).")
        batch.log_output = "\n".join(logs)
        db.commit()

    except Exception as e:
        log.error(f"Ingestion batch {batch_id} failed: {e}", exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass
        batch = db.query(IngestionBatch).filter(IngestionBatch.id == batch_id).first()
        if batch:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {str(e)}")
            batch.status = "FAILED"
            batch.log_output = "\n".join(logs)
            try:
                db.commit()
            except Exception:
                pass
    finally:
        db.close()


@router.post("/year-data")
async def upload_year_data(
    background_tasks: BackgroundTasks,
    year: int = Form(..., description="Target manufacturing year (e.g. 2024, 2023)"),
    file: UploadFile = File(..., description="ZIP archive containing M&Q and QDAR workbooks"),
    db: Session = Depends(get_db),
):
    """Upload full-year ZIP archive and launch background ingestion worker."""
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip archive files are supported.")

    year_target_dir = RAW_BASE_DIR / str(year)
    year_target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_save_path = year_target_dir / f"upload_{timestamp}_{file.filename}"

    # Save uploaded ZIP
    try:
        with open(zip_save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Safely extract ZIP (Zip Slip protection)
    extract_dir = year_target_dir / f"extracted_{timestamp}"
    extract_dir.mkdir(parents=True, exist_ok=True)
    resolved_base = extract_dir.resolve()
    try:
        with zipfile.ZipFile(zip_save_path, "r") as z:
            for member in z.infolist():
                member_path = (extract_dir / member.filename).resolve()
                if not str(member_path).startswith(str(resolved_base)):
                    raise ValueError(f"Illegal path traversal attempt in archive: {member.filename}")
            z.extractall(extract_dir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to unzip archive safely: {e}")

    # Create IngestionBatch record
    batch = IngestionBatch(
        year=year,
        filename=file.filename,
        total_shells=0,
        total_documents=0,
        status="PROCESSING",
        log_output=f"[{datetime.now().strftime('%H:%M:%S')}] Upload received. Starting background extraction...",
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Queue background task
    background_tasks.add_task(run_background_ingestion, batch.id, year, extract_dir)

    return {
        "batch_id": batch.id,
        "year": year,
        "filename": file.filename,
        "status": "PROCESSING",
        "message": f"Archive received. Ingestion worker started for Year {year}.",
    }


@router.get("/status/{batch_id}")
def get_batch_status(batch_id: int, db: Session = Depends(get_db)):
    """Check live status and terminal logs for a running or past ingestion batch."""
    batch = db.query(IngestionBatch).filter(IngestionBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Ingestion batch not found.")

    return {
        "batch_id": batch.id,
        "year": batch.year,
        "filename": batch.filename,
        "uploaded_at": batch.uploaded_at.isoformat() if batch.uploaded_at else None,
        "total_shells": batch.total_shells,
        "total_documents": batch.total_documents,
        "status": batch.status,
        "log_output": batch.log_output,
    }


@router.get("/history")
def get_batch_history(db: Session = Depends(get_db)):
    """Get history of all uploaded batches and system ingestions."""
    batches = db.query(IngestionBatch).order_by(IngestionBatch.id.desc()).all()
    return [
        {
            "id": b.id,
            "year": b.year,
            "filename": b.filename,
            "uploaded_at": b.uploaded_at.strftime("%Y-%m-%d %H:%M:%S") if b.uploaded_at else "—",
            "total_shells": b.total_shells,
            "total_documents": b.total_documents,
            "status": b.status,
        }
        for b in batches
    ]
