"""
Database Seeder — Loads M&Q workbooks, Actual Casting Log, and QDAR records into SQLite.

Features:
1. Re-creates schema with all dimensional, casting intelligence, metallurgical, and defect columns.
2. Ingests and cross-matches M&Q records with Actual Casting Log data:
   - Populates actual measured weight, job card weight, weight variance, and calculated weight.
   - Populates shifting/cast date, month, mold sand process, core process, riser %, simulation path, and tooling sizes.
   - Merges unique casting pieces into shells.
3. Inserts linked Documents for both M&Q workbooks (doc_type='MQ') and Actual Casting Log (doc_type='CASTING_LOG').
4. 3-Pass Heuristic QDAR Matcher:
   - Pass 1: Canonical 3-part base job match (e.g. SE24-BSCM-0025)
   - Pass 2: Regex & Token Substrings across complex job strings
   - Pass 3: Normalized Drawing Number fallback
   - Retains unlinked QDAR records with status='UNLINKED' and shell_id=NULL
"""
import json
import logging
import sys
from pathlib import Path
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from database.db import engine, SessionLocal, init_db
from database.models import Shell, Document, IngestionBatch
from backend.services.normalizer import (
    normalize_job_number, extract_base_job, extract_all_job_tokens,
    clean_alphanumeric, is_rollover_job
)
from etl.parse_mq_files import get_metallurgy_profile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MQ_JSON = PROCESSED_DIR / "all_lots_mq_mapping.json"
CASTING_JSON = PROCESSED_DIR / "cleaned_casting_log_2025.json"
QDAR_JSON = PROCESSED_DIR / "qdar_mapping.json"


def seed_shells(
    session,
    mq_records: list[dict] | None = None,
    casting_records: list[dict] | None = None,
) -> tuple[dict, dict, dict]:
    """Seed Shells merged with Casting Log data, and create lookup index dicts for heuristic linking."""
    if mq_records is None:
        if MQ_JSON.exists():
            with open(MQ_JSON, "r", encoding="utf-8") as f:
                mq_records = json.load(f)
        else:
            log.warning(f"M&Q JSON not found: {MQ_JSON}")
            mq_records = []

    if casting_records is None:
        if CASTING_JSON.exists():
            with open(CASTING_JSON, "r", encoding="utf-8") as f:
                casting_records = json.load(f)
        else:
            log.warning(f"Casting JSON not found: {CASTING_JSON}")
            casting_records = []

    log.info(f"Seeding with {len(mq_records)} M&Q records and {len(casting_records)} Casting Log records...")

    # Build multi-key index for casting records
    casting_by_lot_serial: dict[tuple, dict] = {}
    casting_by_lot_job_piece: dict[tuple, dict] = {}
    casting_by_lot_base_piece: dict[tuple, dict] = {}
    casting_by_lot_job: dict[tuple, dict] = {}

    for c in casting_records:
        lot = c.get("lot_number")
        serial = c.get("serial_number")
        c_job = clean_alphanumeric(c.get("job_number"))
        c_base = clean_alphanumeric(c.get("base_job") or extract_base_job(c.get("job_number")) or "")
        piece = str(c.get("piece_number") or "").strip()

        if lot is not None and serial is not None:
            casting_by_lot_serial[(lot, serial)] = c
        if lot is not None and c_job:
            casting_by_lot_job_piece[(lot, c_job, piece)] = c
            casting_by_lot_job[(lot, c_job)] = c
        if lot is not None and c_base:
            casting_by_lot_base_piece[(lot, c_base, piece)] = c

    job_base_to_shells: dict[str, list[int]] = {}
    token_to_shells: dict[str, list[int]] = {}
    drawing_to_shells: dict[str, list[int]] = {}

    matched_casting_ids = set()
    count = 0
    casting_linked_count = 0

    # 1. Process M&Q records and enrich with Casting Log data
    for rec in mq_records:
        lot = rec.get("lot_number")
        serial = rec.get("serial_number")
        job = rec.get("job_number") or ""
        c_job = clean_alphanumeric(job)
        c_base = clean_alphanumeric(extract_base_job(job) or "")
        piece = str(rec.get("piece_number") or "").strip()

        # Match with Casting Log
        cast_match = None
        if lot is not None and serial is not None and (lot, serial) in casting_by_lot_serial:
            cast_match = casting_by_lot_serial[(lot, serial)]
        elif lot is not None and (lot, c_job, piece) in casting_by_lot_job_piece:
            cast_match = casting_by_lot_job_piece[(lot, c_job, piece)]
        elif lot is not None and (lot, c_base, piece) in casting_by_lot_base_piece:
            cast_match = casting_by_lot_base_piece[(lot, c_base, piece)]
        elif lot is not None and (lot, c_job) in casting_by_lot_job:
            cast_match = casting_by_lot_job[(lot, c_job)]

        actual_wt = None
        job_card_wt = rec.get("weight")
        calc_wt = None
        wt_diff = None
        cast_date = None
        month = None
        mold_proc = None
        core_proc = None
        riser_pct = None
        technology = rec.get("shell_type")
        simulation_path = None
        pattern_ca = None
        core_box = None
        shaft_fit = None

        if cast_match:
            matched_casting_ids.add(id(cast_match))
            actual_wt = cast_match.get("actual_weight")
            if cast_match.get("job_card_weight") is not None:
                job_card_wt = cast_match.get("job_card_weight")
            calc_wt = cast_match.get("calculated_weight")
            wt_diff = cast_match.get("weight_diff")
            cast_date = cast_match.get("cast_date")
            month = cast_match.get("month")
            mold_proc = cast_match.get("mold_process")
            core_proc = cast_match.get("core_process")
            riser_pct = cast_match.get("riser_pct")
            technology = cast_match.get("technology") or rec.get("shell_type")
            simulation_path = cast_match.get("simulation_path")
            pattern_ca = cast_match.get("pattern_size_ca")
            core_box = cast_match.get("core_box")
            shaft_fit = cast_match.get("shaft_fitting")
            casting_linked_count += 1

        shell = Shell(
            job_number=job,
            piece_number=rec.get("piece_number"),
            shell_name=rec.get("shell_name"),
            shell_type=rec.get("shell_type"),
            material_standard=rec.get("material_standard"),
            drawing_number=rec.get("drawing_number"),
            idm_number=rec.get("idm_number"),
            lot_number=lot,
            serial_number=serial,
            data_year=rec.get("data_year", 2025),
            # Weight metrics (kg): weight represents nominal job card/drawing weight
            weight=job_card_wt or calc_wt,
            actual_weight=actual_wt,
            job_card_weight=job_card_wt,
            calculated_weight=calc_wt,
            weight_diff=wt_diff,
            # Dimensions
            od=rec.get("od"),
            id_dim=rec.get("id_dim"),
            length=rec.get("length"),
            wall_thickness=rec.get("wall_thickness"),
            cast_od=rec.get("cast_od"),
            cast_id=rec.get("cast_id"),
            cast_length=rec.get("cast_length"),
            cast_wall_thickness=rec.get("cast_wall_thickness"),
            # Casting & Foundry specs
            pattern_size_ca=pattern_ca,
            core_box=core_box,
            mold_process=mold_proc,
            core_process=core_proc,
            riser_pct=riser_pct,
            technology=technology,
            simulation_path=simulation_path,
            shaft_fitting=shaft_fit,
            month=month,
            cast_date=cast_date,
            # Metallurgy & Mechanical
            c_pct=rec.get("c_pct"),
            si_pct=rec.get("si_pct"),
            mn_pct=rec.get("mn_pct"),
            p_pct=rec.get("p_pct"),
            s_pct=rec.get("s_pct"),
            cr_pct=rec.get("cr_pct"),
            ni_pct=rec.get("ni_pct"),
            mo_pct=rec.get("mo_pct"),
            hardness_bhn=rec.get("hardness_bhn"),
            tensile_strength=rec.get("tensile_strength"),
            yield_strength=rec.get("yield_strength"),
            elongation_pct=rec.get("elongation_pct"),
            status="COMPLETE",
        )
        session.add(shell)
        session.flush()

        # Link M&Q Document
        mq_doc = Document(
            shell_id=shell.id,
            doc_type="MQ",
            doc_number=f"Lot#{rec.get('lot_number')}-M&Q",
            file_path=rec.get("mq_workbook_path"),
            sheet_name=rec.get("mq_sheet_name"),
            job_number=job,
            piece_number=rec.get("piece_number"),
            drawing_number=rec.get("drawing_number"),
            is_available=True,
            status="LINKED",
            data_year=rec.get("data_year", 2025),
        )
        session.add(mq_doc)

        # Link Casting Log Document if matched
        if cast_match:
            c_path = cast_match.get("file_path")
            cast_file_exists = Path(c_path).exists() if c_path else False
            cast_doc = Document(
                shell_id=shell.id,
                doc_type="CASTING_LOG",
                doc_number=f"Lot#{lot}-CastSr#{serial or cast_match.get('serial_number')}",
                file_path=c_path,
                sheet_name=cast_match.get("sheet_name", "2025"),
                job_number=job,
                piece_number=rec.get("piece_number"),
                drawing_number=rec.get("drawing_number") or cast_match.get("drawing_number"),
                doc_date=cast_date,
                defect_description=(
                    f"Actual Wt: {actual_wt} kg | Job Wt: {job_card_wt} kg | Diff: {wt_diff} kg | "
                    f"Mold: {mold_proc} | Core: {core_proc} | Tech: {technology}"
                ),
                detected_at=f"Foundry Shifting / Casting ({month})" if month else "Foundry Shifting",
                is_available=cast_file_exists,
                status="LINKED",
                data_year=rec.get("data_year", 2025),
            )
            session.add(cast_doc)

        # Indexing for heuristic QDAR matcher
        base_job = extract_base_job(job)
        if base_job:
            job_base_to_shells.setdefault(base_job, []).append(shell.id)

        for tok in extract_all_job_tokens(job):
            token_to_shells.setdefault(tok, []).append(shell.id)
            c_tok = clean_alphanumeric(tok)
            if c_tok:
                token_to_shells.setdefault(c_tok, []).append(shell.id)

        drawing = rec.get("drawing_number")
        if drawing:
            d_clean = clean_alphanumeric(drawing)
            if d_clean and len(d_clean) > 3:
                drawing_to_shells.setdefault(d_clean, []).append(shell.id)

        count += 1

    # 2. Ingest any remaining unmatched casting records (e.g. special castings / tooling pieces)
    unmatched_casting_added = 0
    for c in casting_records:
        if id(c) in matched_casting_ids:
            continue

        c_job = c.get("job_number") or ""
        mat_raw = c.get("material_standard")
        meta_profile = get_metallurgy_profile(mat_raw)
        c_path = c.get("file_path")
        cast_file_exists = Path(c_path).exists() if c_path else False

        actual_wt = c.get("actual_weight")
        job_card_wt = c.get("job_card_weight")
        calc_wt = c.get("calculated_weight")
        wt_diff = c.get("weight_diff")

        shell = Shell(
            job_number=c_job,
            piece_number=c.get("piece_number"),
            shell_name=c.get("shell_name"),
            shell_type=c.get("shell_type"),
            material_standard=mat_raw,
            drawing_number=c.get("drawing_number"),
            idm_number=c.get("idm_number"),
            lot_number=c.get("lot_number"),
            serial_number=c.get("serial_number"),
            data_year=c.get("data_year", 2025),
            # Weight metrics (kg): weight represents nominal allowable weight
            weight=job_card_wt or calc_wt,
            actual_weight=actual_wt,
            job_card_weight=job_card_wt,
            calculated_weight=calc_wt,
            weight_diff=wt_diff,
            # Dimensions
            od=c.get("od"),
            id_dim=c.get("id_dim"),
            length=c.get("length"),
            wall_thickness=c.get("wall_thickness"),
            cast_od=c.get("cast_od"),
            cast_id=c.get("cast_id"),
            cast_length=c.get("cast_length"),
            cast_wall_thickness=c.get("cast_wall_thickness"),
            # Casting & Foundry specs
            pattern_size_ca=c.get("pattern_size_ca"),
            core_box=c.get("core_box"),
            mold_process=c.get("mold_process"),
            core_process=c.get("core_process"),
            riser_pct=c.get("riser_pct"),
            technology=c.get("technology"),
            simulation_path=c.get("simulation_path"),
            shaft_fitting=c.get("shaft_fitting"),
            month=c.get("month"),
            cast_date=c.get("cast_date"),
            # Metallurgy from profile
            c_pct=meta_profile.get("c_pct"),
            si_pct=meta_profile.get("si_pct"),
            mn_pct=meta_profile.get("mn_pct"),
            p_pct=meta_profile.get("p_pct"),
            s_pct=meta_profile.get("s_pct"),
            cr_pct=meta_profile.get("cr_pct"),
            ni_pct=meta_profile.get("ni_pct"),
            mo_pct=meta_profile.get("mo_pct"),
            hardness_bhn=meta_profile.get("hardness_bhn"),
            tensile_strength=meta_profile.get("tensile_strength"),
            yield_strength=meta_profile.get("yield_strength"),
            elongation_pct=meta_profile.get("elongation_pct"),
            status="COMPLETE",
        )
        session.add(shell)
        session.flush()

        # Link Casting Log Document
        cast_doc = Document(
            shell_id=shell.id,
            doc_type="CASTING_LOG",
            doc_number=f"Lot#{c.get('lot_number')}-CastSr#{c.get('serial_number')}",
            file_path=c_path,
            sheet_name=c.get("sheet_name", "2025"),
            job_number=c_job,
            piece_number=c.get("piece_number"),
            drawing_number=c.get("drawing_number"),
            doc_date=c.get("cast_date"),
            defect_description=(
                f"Actual Wt: {actual_wt} kg | Job Wt: {job_card_wt} kg | Diff: {wt_diff} kg | "
                f"Mold: {c.get('mold_process')} | Core: {c.get('core_process')} | Tech: {c.get('technology')}"
            ),
            detected_at=f"Foundry Shifting / Casting ({c.get('month')})" if c.get("month") else "Foundry Shifting",
            is_available=cast_file_exists,
            status="LINKED",
            data_year=c.get("data_year", 2025),
        )
        session.add(cast_doc)

        # Indexing for heuristic QDAR matcher
        base_job = extract_base_job(c_job)
        if base_job:
            job_base_to_shells.setdefault(base_job, []).append(shell.id)

        for tok in extract_all_job_tokens(c_job):
            token_to_shells.setdefault(tok, []).append(shell.id)
            c_tok = clean_alphanumeric(tok)
            if c_tok:
                token_to_shells.setdefault(c_tok, []).append(shell.id)

        drawing = c.get("drawing_number")
        if drawing:
            d_clean = clean_alphanumeric(drawing)
            if d_clean and len(d_clean) > 3:
                drawing_to_shells.setdefault(d_clean, []).append(shell.id)

        count += 1
        unmatched_casting_added += 1

    session.commit()
    log.info(
        f"  Inserted {count} total shells (M&Q: {len(mq_records)}, Casting-only: {unmatched_casting_added}) "
        f"with {casting_linked_count + unmatched_casting_added} Casting Log links."
    )
    return job_base_to_shells, token_to_shells, drawing_to_shells


def seed_qdars(
    session,
    job_base_to_shells: dict,
    token_to_shells: dict,
    drawing_to_shells: dict,
    qdar_records: list[dict] | None = None,
):
    """Seed QDAR records with 3-pass heuristic linking."""
    if qdar_records is None:
        if not QDAR_JSON.exists():
            log.warning(f"QDAR JSON not found: {QDAR_JSON}")
            return
        with open(QDAR_JSON, "r", encoding="utf-8") as f:
            qdar_records = json.load(f)

    log.info(f"Linking and seeding {len(qdar_records)} QDAR reports...")

    pass1_count = 0
    pass2_count = 0
    pass3_count = 0
    unlinked_count = 0

    for rec in qdar_records:
        job = rec.get("job_number")
        file_path = rec.get("file_path")
        file_name = rec.get("file_name") or (Path(file_path).name if file_path else "")
        drawing = rec.get("drawing_number")
        file_exists = Path(file_path).exists() if file_path else False
        is_rollover = is_rollover_job(job, file_name)

        matched_shell_ids = set()

        # Pass 1: Canonical Base Job Match
        base_job = extract_base_job(job)
        if base_job and base_job in job_base_to_shells:
            matched_shell_ids.update(job_base_to_shells[base_job])
            pass1_count += 1

        # Pass 2: Regex Token Extraction
        if not matched_shell_ids:
            for tok in extract_all_job_tokens(job, file_name):
                if tok in token_to_shells:
                    matched_shell_ids.update(token_to_shells[tok])
                c_tok = clean_alphanumeric(tok)
                if c_tok in token_to_shells:
                    matched_shell_ids.update(token_to_shells[c_tok])
            if matched_shell_ids:
                pass2_count += 1

        # Pass 3: Drawing Fallback
        if not matched_shell_ids and drawing:
            d_clean = clean_alphanumeric(drawing)
            if d_clean and d_clean in drawing_to_shells:
                matched_shell_ids.update(drawing_to_shells[d_clean])
                pass3_count += 1

        doc_type_val = rec.get("doc_type", "QDR_EXTERNAL")

        if matched_shell_ids:
            doc_status = "LINKED"
            unavail_reason = None if file_exists else (
                "Missing / Incomplete (2024 Rollover)" if is_rollover else "File not found on disk"
            )
            for sid in matched_shell_ids:
                doc = Document(
                    shell_id=sid,
                    doc_type=doc_type_val,
                    doc_number=rec.get("qdar_number"),
                    file_path=file_path,
                    job_number=job,
                    piece_number=rec.get("piece_number"),
                    customer_name=rec.get("customer_name"),
                    part_name=rec.get("part_name"),
                    drawing_number=drawing,
                    doc_date=rec.get("doc_date"),
                    defect_description=rec.get("defect_description"),
                    defect_judgment=rec.get("defect_judgment"),
                    detected_at=rec.get("detected_at"),
                    detected_by=rec.get("detected_by"),
                    responsibility=rec.get("responsibility"),
                    is_available=file_exists,
                    unavailable_reason=unavail_reason,
                    status=doc_status,
                    data_year=rec.get("data_year", 2025),
                )
                session.add(doc)
        else:
            unlinked_count += 1
            doc_status = "UNLINKED"
            unavail_reason = "Missing / Incomplete (2024 Rollover)" if is_rollover else "Unlinked QDAR Archive"
            doc = Document(
                shell_id=None,
                doc_type=doc_type_val,
                doc_number=rec.get("qdar_number"),
                file_path=file_path,
                job_number=job,
                piece_number=rec.get("piece_number"),
                customer_name=rec.get("customer_name"),
                part_name=rec.get("part_name"),
                drawing_number=drawing,
                doc_date=rec.get("doc_date"),
                defect_description=rec.get("defect_description"),
                defect_judgment=rec.get("defect_judgment"),
                detected_at=rec.get("detected_at"),
                detected_by=rec.get("detected_by"),
                responsibility=rec.get("responsibility"),
                is_available=file_exists,
                unavailable_reason=unavail_reason,
                status=doc_status,
                data_year=rec.get("data_year", 2025),
            )
            session.add(doc)

    session.commit()
    log.info(f"  QDAR Linked: Pass1={pass1_count}, Pass2={pass2_count}, Pass3={pass3_count} | Unlinked={unlinked_count}")


def run_seed_pipeline(clear_existing: bool = True):
    """Run full schema recreation and database population with M&Q, Casting Log, and QDARS."""
    # Ensure processed files are up to date
    if not MQ_JSON.exists():
        from etl.parse_mq_files import main as run_mq_etl
        run_mq_etl()
    if not CASTING_JSON.exists():
        from etl.clean_casting_log import main as run_casting_etl
        run_casting_etl()
    if not QDAR_JSON.exists():
        from etl.parse_qad_files import main as run_qdar_etl
        run_qdar_etl()

    init_db(drop_first=False)
    session = SessionLocal()

    try:
        if clear_existing:
            session.execute(text("DELETE FROM documents"))
            session.execute(text("DELETE FROM shells"))
            session.commit()
            log.info("Cleared database records for clean seeding (retained ingestion history)")

        job_base, tokens, drawings = seed_shells(session)
        seed_qdars(session, job_base, tokens, drawings)

        # Log initial batch record
        shell_count = session.query(Shell).count()
        doc_count = session.query(Document).count()
        cast_doc_count = session.query(Document).filter(Document.doc_type == "CASTING_LOG").count()
        mq_doc_count = session.query(Document).filter(Document.doc_type == "MQ").count()
        qdr_doc_count = session.query(Document).filter(Document.doc_type.in_(["QDR_EXTERNAL", "QDR_INTERNAL"])).count()

        batch = IngestionBatch(
            year=2025,
            filename="Initial 2025 Complete Dataset (M&Q, Actual Casting Log, QDARS)",
            total_shells=shell_count,
            total_documents=doc_count,
            status="COMPLETED",
            log_output=(
                f"Successfully initialized 2025 dataset with {shell_count} shells and {doc_count} documents "
                f"(M&Q: {mq_doc_count}, Casting Logs: {cast_doc_count}, QDARS: {qdr_doc_count})."
            ),
        )
        session.add(batch)
        session.commit()

        log.info(f"\n{'='*55}")
        log.info("  DATABASE INITIALIZATION COMPLETE")
        log.info(f"{'='*55}")
        log.info(f"  Shell Records:          {shell_count}")
        log.info(f"  Total Document Records: {doc_count}")
        log.info(f"    - M&Q Plans:          {mq_doc_count}")
        log.info(f"    - Casting Logs:       {cast_doc_count}")
        log.info(f"    - QDAR Reports:       {qdr_doc_count}")
        log.info(f"{'='*55}")

    except Exception as e:
        session.rollback()
        log.error(f"Seeding failed: {e}", exc_info=True)
        raise
    finally:
        session.close()


def main():
    run_seed_pipeline(clear_existing=True)


if __name__ == "__main__":
    main()
