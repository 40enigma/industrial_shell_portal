"""
Multi-Year Batch Importer CLI — Ingest historical data batches (2022–2024+).

Usage:
    python -m etl.import_batch --year 2024 --mq-dir "data/raw/2024_MQ" --qdar-dir "data/raw/2024_QDAR" --casting-log "data/raw/Actual Casting Log 2024.xlsx"
    python -m etl.import_batch --year 2023 --mq-dir "d:/data/MQ_2023"
    python -m etl.import_batch --year 2025 --auto-detect

Options:
    --year         Data year for the batch (e.g. 2022, 2023, 2024, 2025). Default: 2025
    --mq-dir       Path to directory containing M&Q workbooks or Lot subdirectories
    --qdar-dir     Path to directory containing QDAR workbooks (External/Internal)
    --casting-log  Path to Actual Casting Log Excel file
    --clear        Clear existing database before importing (WARNING: wipes current data)
    --auto-detect  Ingest default 2025 dataset
"""
import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import SessionLocal, init_db
from database.models import Shell, Document
from etl.parse_mq_files import parse_all_mq_files
from etl.parse_qad_files import parse_all_qdar_files
from etl.clean_casting_log import parse_casting_log, find_casting_log_file
from etl.seed_db import seed_shells, seed_qdars, run_seed_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)


def import_batch(
    year: int,
    mq_dir: str | None = None,
    qdar_dir: str | None = None,
    casting_log: str | None = None,
    clear: bool = False,
    auto_detect: bool = False,
):
    """Ingest a historical or current batch of M&Q, Casting Log, and QDAR workbooks into SQLite."""
    log.info("=" * 65)
    log.info(f"MULTI-YEAR BATCH IMPORTER — Year: {year}")
    log.info("=" * 65)

    if auto_detect:
        log.info("Auto-detecting default dataset and running complete pipeline...")
        run_seed_pipeline(clear_existing=clear)
        return

    mq_path = Path(mq_dir) if mq_dir else None
    qdar_path = Path(qdar_dir) if qdar_dir else None
    cast_path = Path(casting_log) if casting_log else find_casting_log_file(year=year)

    if not mq_path and not qdar_path and not cast_path:
        log.error("Error: Please provide at least one of --mq-dir, --qdar-dir, --casting-log, or --auto-detect.")
        sys.exit(1)

    init_db()
    session = SessionLocal()

    try:
        if clear:
            from sqlalchemy import text
            session.execute(text("DELETE FROM documents"))
            session.execute(text("DELETE FROM shells"))
            session.commit()
            log.info("Cleared existing database records.")

        mq_records = []
        if mq_path and mq_path.exists():
            log.info(f"Parsing M&Q files from: {mq_path} (Year: {year})")
            mq_records = parse_all_mq_files(mq_dir=mq_path, year=year)
        elif mq_path:
            log.warning(f"M&Q path does not exist: {mq_path}")

        casting_records = []
        if cast_path and cast_path.exists():
            log.info(f"Parsing Casting Log from: {cast_path} (Year: {year})")
            casting_records = parse_casting_log(cast_path, year=year)

        # Insert shells and create lookup indexes
        job_base, tokens, drawings = seed_shells(
            session, mq_records=mq_records, casting_records=casting_records
        )

        qdar_records = []
        if qdar_path and qdar_path.exists():
            log.info(f"Parsing QDAR files from: {qdar_path} (Year: {year})")
            qdar_records = parse_all_qdar_files(qdar_dir=qdar_path, year=year)
        elif qdar_path:
            log.warning(f"QDAR path does not exist: {qdar_path}")

        if qdar_records:
            seed_qdars(session, job_base, tokens, drawings, qdar_records=qdar_records)

        # Batch summary
        total_shells = session.query(Shell).filter(Shell.data_year == year).count()
        total_docs = session.query(Document).filter(Document.data_year == year).count()
        cast_docs = session.query(Document).filter(Document.data_year == year, Document.doc_type == "CASTING_LOG").count()
        log.info(
            f"\nSuccessfully imported Year {year}: {total_shells} shells, "
            f"{total_docs} documents ({cast_docs} Casting Log links)."
        )

    except Exception as e:
        session.rollback()
        log.error(f"Batch import failed: {e}", exc_info=True)
        raise
    finally:
        session.close()

    log.info("MULTI-YEAR BATCH IMPORTER — Complete")


def main():
    parser = argparse.ArgumentParser(
        description="Industrial Shell Portal — Multi-Year Batch Data Importer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m etl.import_batch --year 2024 --mq-dir "D:/Data/MQ_2024" --qdar-dir "D:/Data/QDARS_2024" --casting-log "D:/Data/Casting_2024.xlsx"
  python -m etl.import_batch --year 2025 --auto-detect --clear
        """,
    )
    parser.add_argument("--year", type=int, default=2025, help="Data year for batch (e.g. 2022, 2023, 2024, 2025)")
    parser.add_argument("--mq-dir", type=str, default=None, help="Directory containing M&Q workbooks")
    parser.add_argument("--qdar-dir", type=str, default=None, help="Directory containing QDAR workbooks")
    parser.add_argument("--casting-log", type=str, default=None, help="Path to Actual Casting Log Excel workbook")
    parser.add_argument("--clear", action="store_true", help="Clear database before importing")
    parser.add_argument("--auto-detect", action="store_true", help="Auto-detect default 2025 files")

    args = parser.parse_args()
    import_batch(
        year=args.year,
        mq_dir=args.mq_dir,
        qdar_dir=args.qdar_dir,
        casting_log=args.casting_log,
        clear=args.clear,
        auto_detect=args.auto_detect,
    )


if __name__ == "__main__":
    main()
