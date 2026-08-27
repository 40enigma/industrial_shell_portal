"""
Dimensional Search, Proximity Matching & Casting Envelope Calculator Engine.

Features:
1. Standard Proximity Matching with Finish, Casted, and Auto dimension modes.
2. Signed dimension deltas (ΔOD, ΔID, ΔLength, ΔWT) with formatted strings.
3. Machining Stock Envelope & Yield Calculator:
   - Evaluates whether raw casting stock encompasses the target machined part
   - Computes material removal cuts (OD stock, ID stock, Facing stock)
   - Computes Machining Yield %:
     Yield % = [(Target OD² - Target ID²) * Target L] / [(Cast OD² - Cast ID²) * Cast L] * 100
   - Ranks candidates by highest volumetric yield %
4. Multi-parameter filtering, sorting, and document defect bundling.
"""
import math
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from database.models import Shell, Document


def calculate_confidence(
    target_od: float | None,
    target_id: float | None,
    target_length: float | None,
    actual_od: float | None,
    actual_id: float | None,
    actual_length: float | None,
) -> float:
    """Calculate match confidence score (0–100%) based on relative deviation."""
    deviations = []
    if target_od is not None and actual_od is not None and target_od > 0:
        deviations.append(abs(target_od - actual_od) / target_od)
    if target_id is not None and actual_id is not None and target_id > 0:
        deviations.append(abs(target_id - actual_id) / target_id)
    if target_length is not None and actual_length is not None and target_length > 0:
        deviations.append(abs(target_length - actual_length) / target_length)

    if not deviations:
        return 0.0

    total_deviation = sum(deviations)
    return round(max(0.0, 100.0 - total_deviation * 100.0), 2)


def calculate_signed_deltas(
    target_od: float | None,
    target_id: float | None,
    target_length: float | None,
    target_wt: float | None,
    actual_od: float | None,
    actual_id: float | None,
    actual_length: float | None,
    actual_wt: float | None,
) -> dict:
    """Calculate signed deltas: Delta = Actual - Target."""
    # Derive target wall thickness if not explicitly supplied
    if target_wt is None and target_od is not None and target_id is not None and target_od > target_id:
        target_wt = round((target_od - target_id) / 2.0, 2)

    def _format_delta(delta: float | None) -> str:
        if delta is None:
            return "—"
        sign = "+" if delta > 0 else ""
        return f"{sign}{delta:.1f} mm"

    delta_od = round(actual_od - target_od, 2) if (target_od is not None and actual_od is not None) else None
    delta_id = round(actual_id - target_id, 2) if (target_id is not None and actual_id is not None) else None
    delta_len = round(actual_length - target_length, 2) if (target_length is not None and actual_length is not None) else None
    delta_wt = round(actual_wt - target_wt, 2) if (target_wt is not None and actual_wt is not None) else None

    return {
        "delta_od": delta_od,
        "delta_id": delta_id,
        "delta_length": delta_len,
        "delta_wall_thickness": delta_wt,
        "delta_od_formatted": _format_delta(delta_od),
        "delta_id_formatted": _format_delta(delta_id),
        "delta_length_formatted": _format_delta(delta_len),
        "delta_wt_formatted": _format_delta(delta_wt),
    }


def calculate_machining_envelope(
    target_od: float | None,
    target_id: float | None,
    target_length: float | None,
    cast_od: float | None,
    cast_id: float | None,
    cast_length: float | None,
    od_allowance: float = 5.0,
    id_allowance: float = 5.0,
    face_allowance: float = 10.0,
) -> dict:
    """
    Evaluate if raw casting stock encloses target finish dimensions with allowances.
    Calculates stock removal cuts and volumetric Machining Yield %.
    """
    if not target_od or not target_id or not target_length or target_od <= 0 or target_id <= 0 or target_length <= 0:
        return {
            "is_valid_envelope": False,
            "yield_pct": 0.0,
            "od_cut_per_side": None,
            "id_cut_per_side": None,
            "face_cut_per_end": None,
            "envelope_status": "NOT_SPECIFIED",
            "envelope_notes": "Target finish dimensions not specified",
        }

    if not cast_od or not cast_id or not cast_length or cast_od <= 0 or cast_id <= 0 or cast_length <= 0:
        return {
            "is_valid_envelope": False,
            "yield_pct": 0.0,
            "od_cut_per_side": None,
            "id_cut_per_side": None,
            "face_cut_per_end": None,
            "envelope_status": "MISSING_CAST_DIMS",
            "envelope_notes": "Missing as-cast dimensions",
        }

    min_required_od = target_od + 2.0 * od_allowance
    max_allowable_id = target_id - 2.0 * id_allowance
    min_required_length = target_length + 2.0 * face_allowance

    od_valid = cast_od >= min_required_od
    id_valid = cast_id <= max_allowable_id
    length_valid = cast_length >= min_required_length

    is_valid = od_valid and id_valid and length_valid

    # Stock removal per side
    od_cut_per_side = round((cast_od - target_od) / 2.0, 2)
    id_cut_per_side = round((target_id - cast_id) / 2.0, 2)
    face_cut_per_end = round((cast_length - target_length) / 2.0, 2)

    # Volumetric Yield %
    target_vol = (target_od**2 - target_id**2) * target_length
    cast_vol = (cast_od**2 - cast_id**2) * cast_length

    yield_pct = 0.0
    if cast_vol > 0 and target_vol > 0:
        yield_pct = round(min(100.0, (target_vol / cast_vol) * 100.0), 2)

    reasons = []
    if not od_valid: reasons.append(f"Cast OD ({cast_od}mm) < Req ({min_required_od}mm)")
    if not id_valid: reasons.append(f"Cast ID ({cast_id}mm) > Max ({max_allowable_id}mm)")
    if not length_valid: reasons.append(f"Cast L ({cast_length}mm) < Req ({min_required_length}mm)")

    return {
        "is_valid_envelope": is_valid,
        "yield_pct": yield_pct,
        "od_cut_per_side": od_cut_per_side,
        "id_cut_per_side": id_cut_per_side,
        "face_cut_per_end": face_cut_per_end,
        "envelope_status": "VALID_STOCK" if is_valid else "UNDERSIZE",
        "envelope_notes": "; ".join(reasons) if reasons else "Sufficient machining allowance",
    }


def search_shells(
    db: Session,
    od: float | None = None,
    id_dim: float | None = None,
    length: float | None = None,
    tolerance: float = 5.0,
    dimension_mode: str = "finish",  # "finish", "casted", "both"
    # Machining Envelope parameters
    machining_mode: bool = False,
    od_allowance: float = 5.0,
    id_allowance: float = 5.0,
    face_allowance: float = 10.0,
    # Advanced filters
    wall_thickness: float | None = None,
    wt_tolerance: float = 2.0,
    min_weight: float | None = None,
    max_weight: float | None = None,
    material_standard: str | None = None,
    shell_type: str | None = None,
    job_number: str | None = None,
    query: str | None = None,
    lot_number: int | None = None,
    data_year: int | None = None,
    sort_by: str = "confidence",
    sort_order: str = "desc",
    limit: int = 100,
) -> list[dict]:
    """Search shells by dimensional criteria, casting envelope, metallurgy, or keywords."""
    db_query = db.query(Shell).options(joinedload(Shell.documents))
    mode = str(dimension_mode).lower() if isinstance(dimension_mode, str) else "finish"
    sort_by_str = str(sort_by).lower() if isinstance(sort_by, str) else "confidence"
    sort_order_str = str(sort_order).lower() if isinstance(sort_order, str) else "desc"
    filters = []

    if machining_mode and od and id_dim and length:
        # In Machining Envelope Mode: target dimensions define minimum raw casting stock
        min_cast_od = od + 2.0 * od_allowance
        max_cast_id = id_dim - 2.0 * id_allowance
        min_cast_len = length + 2.0 * face_allowance

        filters.append(and_(
            Shell.cast_od.isnot(None),
            Shell.cast_od >= min_cast_od,
            Shell.cast_id.isnot(None),
            Shell.cast_id <= max_cast_id,
            Shell.cast_length.isnot(None),
            Shell.cast_length >= min_cast_len,
        ))

    elif mode == "casted":
        if od is not None:
            filters.append(and_(Shell.cast_od.isnot(None), Shell.cast_od >= od - tolerance, Shell.cast_od <= od + tolerance))
        if id_dim is not None:
            filters.append(and_(Shell.cast_id.isnot(None), Shell.cast_id >= id_dim - tolerance, Shell.cast_id <= id_dim + tolerance))
        if length is not None:
            filters.append(and_(Shell.cast_length.isnot(None), Shell.cast_length >= length - tolerance, Shell.cast_length <= length + tolerance))
        if wall_thickness is not None:
            filters.append(and_(Shell.cast_wall_thickness.isnot(None), Shell.cast_wall_thickness >= wall_thickness - wt_tolerance, Shell.cast_wall_thickness <= wall_thickness + wt_tolerance))

    elif mode == "both":
        dim_clauses = []
        if od is not None:
            dim_clauses.append(or_(
                and_(Shell.od.isnot(None), Shell.od >= od - tolerance, Shell.od <= od + tolerance),
                and_(Shell.cast_od.isnot(None), Shell.cast_od >= od - tolerance, Shell.cast_od <= od + tolerance)
            ))
        if id_dim is not None:
            dim_clauses.append(or_(
                and_(Shell.id_dim.isnot(None), Shell.id_dim >= id_dim - tolerance, Shell.id_dim <= id_dim + tolerance),
                and_(Shell.cast_id.isnot(None), Shell.cast_id >= id_dim - tolerance, Shell.cast_id <= id_dim + tolerance)
            ))
        if length is not None:
            dim_clauses.append(or_(
                and_(Shell.length.isnot(None), Shell.length >= length - tolerance, Shell.length <= length + tolerance),
                and_(Shell.cast_length.isnot(None), Shell.cast_length >= length - tolerance, Shell.cast_length <= length + tolerance)
            ))
        if wall_thickness is not None:
            dim_clauses.append(or_(
                and_(Shell.wall_thickness.isnot(None), Shell.wall_thickness >= wall_thickness - wt_tolerance, Shell.wall_thickness <= wall_thickness + wt_tolerance),
                and_(Shell.cast_wall_thickness.isnot(None), Shell.cast_wall_thickness >= wall_thickness - wt_tolerance, Shell.cast_wall_thickness <= wall_thickness + wt_tolerance)
            ))
        if dim_clauses:
            filters.append(and_(*dim_clauses))

    else:
        # Finish dimensions mode
        if od is not None:
            filters.append(and_(Shell.od.isnot(None), Shell.od >= od - tolerance, Shell.od <= od + tolerance))
        if id_dim is not None:
            filters.append(and_(Shell.id_dim.isnot(None), Shell.id_dim >= id_dim - tolerance, Shell.id_dim <= id_dim + tolerance))
        if length is not None:
            filters.append(and_(Shell.length.isnot(None), Shell.length >= length - tolerance, Shell.length <= length + tolerance))
        if wall_thickness is not None:
            filters.append(and_(Shell.wall_thickness.isnot(None), Shell.wall_thickness >= wall_thickness - wt_tolerance, Shell.wall_thickness <= wall_thickness + wt_tolerance))

    # Advanced Filters
    if min_weight is not None:
        filters.append(and_(Shell.weight.isnot(None), Shell.weight >= min_weight))
    if max_weight is not None:
        filters.append(and_(Shell.weight.isnot(None), Shell.weight <= max_weight))
    if material_standard:
        filters.append(Shell.material_standard.ilike(f"%{material_standard.strip()}%"))
    if shell_type:
        filters.append(Shell.shell_type.ilike(f"%{shell_type.strip()}%"))
    if lot_number is not None:
        filters.append(Shell.lot_number == lot_number)
    if data_year is not None:
        filters.append(Shell.data_year == data_year)
    if job_number:
        filters.append(Shell.job_number.ilike(f"%{job_number.strip()}%"))

    # Global Keyword Query
    if query:
        q = f"%{query.strip()}%"
        filters.append(or_(
            Shell.job_number.ilike(q),
            Shell.drawing_number.ilike(q),
            Shell.idm_number.ilike(q),
            Shell.shell_name.ilike(q),
            Shell.material_standard.ilike(q),
            Shell.piece_number.ilike(q),
        ))

    if filters:
        db_query = db_query.filter(and_(*filters))

    shells = db_query.all()

    results = []
    has_target_dims = (od is not None or id_dim is not None or length is not None)

    for shell in shells:
        matched_mode_used = "finish"

        if machining_mode and od and id_dim and length:
            envelope = calculate_machining_envelope(
                target_od=od, target_id=id_dim, target_length=length,
                cast_od=shell.cast_od, cast_id=shell.cast_id, cast_length=shell.cast_length,
                od_allowance=od_allowance, id_allowance=id_allowance, face_allowance=face_allowance
            )
            conf = envelope["yield_pct"]
            deltas = calculate_signed_deltas(od, id_dim, length, wall_thickness, shell.cast_od, shell.cast_id, shell.cast_length, shell.cast_wall_thickness)
            matched_mode_used = "machining_stock"
        elif mode == "casted":
            conf = calculate_confidence(od, id_dim, length, shell.cast_od, shell.cast_id, shell.cast_length)
            deltas = calculate_signed_deltas(od, id_dim, length, wall_thickness, shell.cast_od, shell.cast_id, shell.cast_length, shell.cast_wall_thickness)
            envelope = calculate_machining_envelope(
                target_od=shell.od or (od or 0), target_id=shell.id_dim or (id_dim or 0), target_length=shell.length or (length or 0),
                cast_od=shell.cast_od, cast_id=shell.cast_id, cast_length=shell.cast_length,
            )
            matched_mode_used = "casted"
        elif mode == "both":
            conf_finish = calculate_confidence(od, id_dim, length, shell.od, shell.id_dim, shell.length)
            conf_cast = calculate_confidence(od, id_dim, length, shell.cast_od, shell.cast_id, shell.cast_length)
            if conf_cast > conf_finish:
                conf = conf_cast
                deltas = calculate_signed_deltas(od, id_dim, length, wall_thickness, shell.cast_od, shell.cast_id, shell.cast_length, shell.cast_wall_thickness)
                matched_mode_used = "casted"
            else:
                conf = conf_finish
                deltas = calculate_signed_deltas(od, id_dim, length, wall_thickness, shell.od, shell.id_dim, shell.length, shell.wall_thickness)
                matched_mode_used = "finish"
            envelope = calculate_machining_envelope(
                target_od=shell.od or (od or 0), target_id=shell.id_dim or (id_dim or 0), target_length=shell.length or (length or 0),
                cast_od=shell.cast_od, cast_id=shell.cast_id, cast_length=shell.cast_length,
            )
        else:
            conf = calculate_confidence(od, id_dim, length, shell.od, shell.id_dim, shell.length)
            deltas = calculate_signed_deltas(od, id_dim, length, wall_thickness, shell.od, shell.id_dim, shell.length, shell.wall_thickness)
            envelope = calculate_machining_envelope(
                target_od=shell.od or (od or 0), target_id=shell.id_dim or (id_dim or 0), target_length=shell.length or (length or 0),
                cast_od=shell.cast_od, cast_id=shell.cast_id, cast_length=shell.cast_length,
            )
            matched_mode_used = "finish"

        if not has_target_dims and not machining_mode:
            conf = 100.0

        docs = []
        for doc in shell.documents:
            docs.append({
                "id": doc.id,
                "doc_type": doc.doc_type,
                "doc_number": doc.doc_number,
                "file_path": doc.file_path,
                "sheet_name": doc.sheet_name,
                "is_available": doc.is_available,
                "unavailable_reason": doc.unavailable_reason,
                "customer_name": doc.customer_name,
                "part_name": doc.part_name,
                "drawing_number": doc.drawing_number,
                "doc_date": doc.doc_date,
                "defect_description": doc.defect_description,
                "defect_judgment": doc.defect_judgment,
                "detected_at": doc.detected_at,
                "responsibility": doc.responsibility,
                "status": doc.status,
            })

        results.append({
            "id": shell.id,
            "data_year": shell.data_year,
            "job_number": shell.job_number,
            "piece_number": shell.piece_number,
            "shell_name": shell.shell_name,
            "shell_type": shell.shell_type,
            "material_standard": shell.material_standard,
            "drawing_number": shell.drawing_number,
            "idm_number": shell.idm_number,
            "lot_number": shell.lot_number,
            "serial_number": shell.serial_number,
            "weight": shell.weight,
            "actual_weight": shell.actual_weight,
            "job_card_weight": shell.job_card_weight,
            "calculated_weight": shell.calculated_weight,
            "weight_diff": shell.weight_diff,
            "cast_date": shell.cast_date,
            "month": shell.month,
            "mold_process": shell.mold_process,
            "core_process": shell.core_process,
            "riser_pct": shell.riser_pct,
            "technology": shell.technology,
            "simulation_path": shell.simulation_path,
            "pattern_size_ca": shell.pattern_size_ca,
            "core_box": shell.core_box,
            "shaft_fitting": shell.shaft_fitting,
            "od": shell.od,
            "id_dim": shell.id_dim,
            "length": shell.length,
            "wall_thickness": shell.wall_thickness,
            "cast_od": shell.cast_od,
            "cast_id": shell.cast_id,
            "cast_length": shell.cast_length,
            "cast_wall_thickness": shell.cast_wall_thickness,
            # Metallurgy & Mechanical Tests
            "c_pct": shell.c_pct,
            "si_pct": shell.si_pct,
            "mn_pct": shell.mn_pct,
            "p_pct": shell.p_pct,
            "s_pct": shell.s_pct,
            "cr_pct": shell.cr_pct,
            "ni_pct": shell.ni_pct,
            "mo_pct": shell.mo_pct,
            "hardness_bhn": shell.hardness_bhn,
            "tensile_strength": shell.tensile_strength,
            "yield_strength": shell.yield_strength,
            "elongation_pct": shell.elongation_pct,
            # Scores & Variances
            "confidence": conf,
            "matched_mode": matched_mode_used,
            **deltas,
            **envelope,
            "documents": docs,
        })

    # Sort results with nulls sorted last in both ascending and descending directions
    reverse_sort = (sort_order_str == "desc")
    sort_key = sort_by_str

    def _sort_val(r, key, fallback=0.0):
        v = r.get(key)
        if v is None:
            return float("-inf") if reverse_sort else float("inf")
        return v

    if machining_mode or sort_key == "yield":
        results.sort(key=lambda r: (_sort_val(r, "yield_pct"), _sort_val(r, "confidence")), reverse=reverse_sort)
    elif sort_key == "od":
        results.sort(key=lambda r: _sort_val(r, "od"), reverse=reverse_sort)
    elif sort_key == "id":
        results.sort(key=lambda r: _sort_val(r, "id_dim"), reverse=reverse_sort)
    elif sort_key == "length":
        results.sort(key=lambda r: _sort_val(r, "length"), reverse=reverse_sort)
    elif sort_key == "wall_thickness":
        results.sort(key=lambda r: _sort_val(r, "wall_thickness"), reverse=reverse_sort)
    elif sort_key == "weight":
        results.sort(key=lambda r: _sort_val(r, "weight"), reverse=reverse_sort)
    elif sort_key == "lot":
        results.sort(key=lambda r: _sort_val(r, "lot_number"), reverse=reverse_sort)
    else:
        results.sort(key=lambda r: (_sort_val(r, "confidence"), _sort_val(r, "lot_number")), reverse=reverse_sort)

    return results[:limit]
