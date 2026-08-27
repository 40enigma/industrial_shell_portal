"""
Search API routes — Dimensional search, casting envelope calculations, filters, and CSV export.
"""
import csv
import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Shell, Document
from backend.services.matcher import search_shells

router = APIRouter(prefix="/api", tags=["search"])


def _unwrap(val, fallback=None):
    if hasattr(val, "default"):
        return val.default if val.default is not ... else fallback
    return val if val is not None else fallback


@router.get("/search")
def search(
    od: float | None = Query(None, description="Target Outer Diameter (mm)"),
    id: float | None = Query(None, alias="id", description="Target Inner Diameter (mm)"),
    length: float | None = Query(None, description="Target Length (mm)"),
    tolerance: float = Query(5.0, ge=0, le=100, description="Tolerance ±mm"),
    dimension_mode: str = Query("finish", description="Search mode: 'finish', 'casted', 'both'"),
    # Machining Envelope parameters
    machining_mode: bool = Query(False, description="Enable Machining Stock Envelope & Yield Calculator mode"),
    od_allowance: float = Query(5.0, ge=0, description="OD radial machining allowance per side (mm)"),
    id_allowance: float = Query(5.0, ge=0, description="ID radial machining allowance per side (mm)"),
    face_allowance: float = Query(10.0, ge=0, description="Facing allowance per end (mm)"),
    # Advanced filters
    wall_thickness: float | None = Query(None, description="Nominal Wall Thickness (mm)"),
    wt_tolerance: float = Query(2.0, ge=0, le=50, description="Wall thickness tolerance ±mm"),
    min_weight: float | None = Query(None, description="Minimum weight in kg"),
    max_weight: float | None = Query(None, description="Maximum weight in kg"),
    material_standard: str | None = Query(None, description="Material standard filter"),
    shell_type: str | None = Query(None, description="Shell type filter"),
    job_number: str | None = Query(None, description="Job number filter (partial)"),
    query: str | None = Query(None, description="Global keyword search (drawing, IDM, job, shell name)"),
    lot_number: int | None = Query(None, description="Lot number filter"),
    data_year: int | None = Query(None, description="Data year filter"),
    sort_by: str = Query("confidence", description="Sort by: 'confidence', 'od', 'id', 'length', 'wall_thickness', 'weight', 'yield', 'lot'"),
    sort_order: str = Query("desc", description="Sort order: 'asc', 'desc'"),
    limit: int = Query(100, ge=1, le=500, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Search shells by dimensions, casting envelope, metallurgy, weight, and keywords.
    """
    results = search_shells(
        db=db,
        od=_unwrap(od),
        id_dim=_unwrap(id),
        length=_unwrap(length),
        tolerance=float(_unwrap(tolerance, 5.0)),
        dimension_mode=str(_unwrap(dimension_mode, "finish")),
        machining_mode=bool(_unwrap(machining_mode, False)),
        od_allowance=float(_unwrap(od_allowance, 5.0)),
        id_allowance=float(_unwrap(id_allowance, 5.0)),
        face_allowance=float(_unwrap(face_allowance, 10.0)),
        wall_thickness=_unwrap(wall_thickness),
        wt_tolerance=float(_unwrap(wt_tolerance, 2.0)),
        min_weight=_unwrap(min_weight),
        max_weight=_unwrap(max_weight),
        material_standard=_unwrap(material_standard),
        shell_type=_unwrap(shell_type),
        job_number=_unwrap(job_number),
        query=_unwrap(query),
        lot_number=_unwrap(lot_number),
        data_year=_unwrap(data_year),
        sort_by=str(_unwrap(sort_by, "confidence")),
        sort_order=str(_unwrap(sort_order, "desc")),
        limit=int(_unwrap(limit, 100)),
    )

    return {
        "count": len(results),
        "tolerance_mm": tolerance,
        "dimension_mode": dimension_mode,
        "machining_mode": machining_mode,
        "query": {
            "od": od,
            "id": id,
            "length": length,
            "wall_thickness": wall_thickness,
            "min_weight": min_weight,
            "max_weight": max_weight,
            "material_standard": material_standard,
            "shell_type": shell_type,
            "job_number": job_number,
            "query": query,
            "lot_number": lot_number,
            "data_year": data_year,
            "od_allowance": od_allowance if machining_mode else None,
            "id_allowance": id_allowance if machining_mode else None,
            "face_allowance": face_allowance if machining_mode else None,
        },
        "results": results,
    }


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    """Return distinct dropdown filter options for the frontend UI."""
    materials = [
        m[0] for m in db.query(Shell.material_standard).distinct().order_by(Shell.material_standard).all()
        if m[0] and not m[0].strip().isdigit() and len(m[0].strip()) > 1
    ]

    shell_types = [
        st[0] for st in db.query(Shell.shell_type).distinct().order_by(Shell.shell_type).all()
        if st[0] and not st[0].strip().isdigit() and len(st[0].strip()) > 1
    ]

    lots = [
        lot[0] for lot in db.query(Shell.lot_number).distinct().order_by(Shell.lot_number).all()
        if lot[0] is not None
    ]

    years = [
        yr[0] for yr in db.query(Shell.data_year).distinct().order_by(Shell.data_year.desc()).all()
        if yr[0] is not None
    ]

    mold_processes = [
        mp[0] for mp in db.query(Shell.mold_process).distinct().order_by(Shell.mold_process).all()
        if mp[0]
    ]

    core_processes = [
        cp[0] for cp in db.query(Shell.core_process).distinct().order_by(Shell.core_process).all()
        if cp[0]
    ]

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    raw_months = [
        m[0] for m in db.query(Shell.month).distinct().all()
        if m[0]
    ]
    # Sort months by calendar order if possible
    months = sorted(
        raw_months,
        key=lambda m: (month_order.index(m) if m in month_order else (month_order.index(m[:3].capitalize()) if m[:3].capitalize() in month_order else 99), m)
    )

    return {
        "material_standards": materials,
        "shell_types": shell_types,
        "lots": lots,
        "years": years,
        "mold_processes": mold_processes,
        "core_processes": core_processes,
        "months": months,
    }


@router.get("/export")
def export_csv(
    od: float | None = Query(None),
    id: float | None = Query(None, alias="id"),
    length: float | None = Query(None),
    tolerance: float = Query(5.0),
    dimension_mode: str = Query("finish"),
    machining_mode: bool = Query(False),
    od_allowance: float = Query(5.0),
    id_allowance: float = Query(5.0),
    face_allowance: float = Query(10.0),
    wall_thickness: float | None = Query(None),
    wt_tolerance: float = Query(2.0),
    min_weight: float | None = Query(None),
    max_weight: float | None = Query(None),
    material_standard: str | None = Query(None),
    shell_type: str | None = Query(None),
    job_number: str | None = Query(None),
    query: str | None = Query(None),
    lot_number: int | None = Query(None),
    data_year: int | None = Query(None),
    sort_by: str = Query("confidence"),
    sort_order: str = Query("desc"),
    limit: int = Query(100000, description="Max export limit"),
    db: Session = Depends(get_db),
):
    """Export filtered search results as a comprehensive CSV with casting data."""
    results = search_shells(
        db=db,
        od=_unwrap(od),
        id_dim=_unwrap(id),
        length=_unwrap(length),
        tolerance=float(_unwrap(tolerance, 5.0)),
        dimension_mode=str(_unwrap(dimension_mode, "finish")),
        machining_mode=bool(_unwrap(machining_mode, False)),
        od_allowance=float(_unwrap(od_allowance, 5.0)),
        id_allowance=float(_unwrap(id_allowance, 5.0)),
        face_allowance=float(_unwrap(face_allowance, 10.0)),
        wall_thickness=_unwrap(wall_thickness),
        wt_tolerance=float(_unwrap(wt_tolerance, 2.0)),
        min_weight=_unwrap(min_weight),
        max_weight=_unwrap(max_weight),
        material_standard=_unwrap(material_standard),
        shell_type=_unwrap(shell_type),
        job_number=_unwrap(job_number),
        query=_unwrap(query),
        lot_number=_unwrap(lot_number),
        data_year=_unwrap(data_year),
        sort_by=str(_unwrap(sort_by, "confidence")),
        sort_order=str(_unwrap(sort_order, "desc")),
        limit=int(_unwrap(limit, 100000)),
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Job Number",
        "Piece",
        "Shell Name",
        "Finish OD (mm)",
        "Finish ID (mm)",
        "Finish Length (mm)",
        "Wall Thickness (mm)",
        "Cast OD (mm)",
        "Cast ID (mm)",
        "Cast Length (mm)",
        "Cast Wall Thickness (mm)",
        "Machining Yield (%)",
        "OD Stock Cut (mm)",
        "ID Stock Cut (mm)",
        "Face Stock Cut (mm)",
        "Actual Weight (kg)",
        "Job Card Wt (kg)",
        "Calculated Wt (kg)",
        "Weight Diff (kg)",
        "Cast / Shifting Date",
        "Month",
        "Mold Process",
        "Core Process",
        "Riser %",
        "Technology",
        "Drawing #",
        "IDM #",
        "Material Standard",
        "Hardness (BHN)",
        "Tensile (MPa)",
        "Carbon %",
        "Silicon %",
        "Manganese %",
        "Shell Type",
        "Lot #",
        "Year",
        "Confidence (%)",
        "Casting Log",
        "M&Q Linked",
        "QDAR Linked",
    ])

    for r in results:
        qdr_docs = [d["doc_number"] or d["doc_type"] for d in r["documents"] if "QDR" in d["doc_type"]]
        mq_docs = [d["sheet_name"] or "MQ" for d in r["documents"] if d["doc_type"] == "MQ"]
        cast_docs = [d["doc_number"] or "CASTING" for d in r["documents"] if d["doc_type"] == "CASTING_LOG"]

        writer.writerow([
            r.get("job_number"),
            r.get("piece_number"),
            r.get("shell_name"),
            r.get("od"),
            r.get("id_dim"),
            r.get("length"),
            r.get("wall_thickness"),
            r.get("cast_od"),
            r.get("cast_id"),
            r.get("cast_length"),
            r.get("cast_wall_thickness"),
            f"{r.get('yield_pct')}%" if r.get("yield_pct") is not None else "—",
            r.get("od_cut_per_side") if r.get("od_cut_per_side") is not None else "—",
            r.get("id_cut_per_side") if r.get("id_cut_per_side") is not None else "—",
            r.get("face_cut_per_end") if r.get("face_cut_per_end") is not None else "—",
            r.get("actual_weight"),
            r.get("job_card_weight"),
            r.get("calculated_weight"),
            r.get("weight_diff"),
            r.get("cast_date"),
            r.get("month"),
            r.get("mold_process"),
            r.get("core_process"),
            r.get("riser_pct"),
            r.get("technology"),
            r.get("drawing_number"),
            r.get("idm_number"),
            r.get("material_standard"),
            r.get("hardness_bhn"),
            r.get("tensile_strength"),
            r.get("c_pct"),
            r.get("si_pct"),
            r.get("mn_pct"),
            r.get("shell_type"),
            r.get("lot_number"),
            r.get("data_year"),
            f"{r.get('confidence')}%",
            "; ".join(cast_docs) if cast_docs else "No",
            "; ".join(mq_docs) if mq_docs else "No",
            "; ".join(qdr_docs) if qdr_docs else "No",
        ])

    output.seek(0)
    filename = f"industrial_shells_export_{dimension_mode}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    """Return summary statistics about the database."""
    from sqlalchemy import func

    shell_count = db.query(Shell).count()
    doc_count = db.query(Document).count()
    mq_count = db.query(Document).filter(Document.doc_type == "MQ").count()
    cast_count = db.query(Document).filter(Document.doc_type == "CASTING_LOG").count()
    qdr_ext = db.query(Document).filter(Document.doc_type == "QDR_EXTERNAL").count()
    qdr_int = db.query(Document).filter(Document.doc_type == "QDR_INTERNAL").count()
    available = db.query(Document).filter(Document.is_available.is_(True)).count()
    linked = db.query(Document).filter(Document.status == "LINKED").count()
    unlinked = db.query(Document).filter(Document.status == "UNLINKED").count()

    od_range = db.query(func.min(Shell.od), func.max(Shell.od)).filter(Shell.od.isnot(None), Shell.od > 0).first()
    id_range = db.query(func.min(Shell.id_dim), func.max(Shell.id_dim)).filter(Shell.id_dim.isnot(None), Shell.id_dim > 0).first()
    len_range = db.query(func.min(Shell.length), func.max(Shell.length)).filter(Shell.length.isnot(None), Shell.length > 0).first()
    wt_range = db.query(func.min(Shell.wall_thickness), func.max(Shell.wall_thickness)).filter(Shell.wall_thickness.isnot(None), Shell.wall_thickness > 0).first()
    lots = db.query(func.count(func.distinct(Shell.lot_number))).scalar()

    return {
        "shells": shell_count,
        "documents": {
            "total": doc_count,
            "mq": mq_count,
            "casting_logs": cast_count,
            "qdr_external": qdr_ext,
            "qdr_internal": qdr_int,
            "available": available,
            "linked": linked,
            "unlinked": unlinked,
        },
        "lots": lots,
        "dimension_ranges": {
            "od": {"min": od_range[0] if od_range else None, "max": od_range[1] if od_range else None},
            "id": {"min": id_range[0] if id_range else None, "max": id_range[1] if id_range else None},
            "length": {"min": len_range[0] if len_range else None, "max": len_range[1] if len_range else None},
            "wall_thickness": {"min": wt_range[0] if wt_range else None, "max": wt_range[1] if wt_range else None},
        },
    }
