"""
Foundry Quality & Defect Intelligence Analytics API.

Provides:
1. Pareto Defect Category Analysis
2. Alloy Grade Scrap & Rework Rates
3. Lot Quality & Defect Density Heatmap
4. Key Manufacturing KPI Summary
"""
import re
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from database.models import Shell, Document

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

DEFECT_PATTERNS = {
    "Blow Holes / Gas Porosity": re.compile(r"blow\s*hole|gas|porosity|pin\s*hole", re.IGNORECASE),
    "Sand Inclusions": re.compile(r"sand|inclusion|drop|dirt", re.IGNORECASE),
    "Shrinkage Cavity / Depression": re.compile(r"shrinkage|cavity|sink|depression", re.IGNORECASE),
    "Slag Inclusions": re.compile(r"slag|dross|flux", re.IGNORECASE),
    "Dimensional Variance": re.compile(r"dimension|size|undercut|bore|over\s*size|under\s*size|thick|eccentric", re.IGNORECASE),
    "Cracks / Tear": re.compile(r"crack|tear|fracture|broken", re.IGNORECASE),
    "Machining Shift / Setup": re.compile(r"machin|step|shift|tool|chatter", re.IGNORECASE),
    "Collar / Face Defects": re.compile(r"collar|face|riser|flange", re.IGNORECASE),
}


def _unwrap(val, fallback=None):
    """Return val if not None, else fallback."""
    return val if val is not None else fallback


@router.get("/summary")
def get_analytics_summary(
    year: int | None = Query(None, description="Optional manufacturing year filter (e.g. 2023, 2024, 2025, 2026)"),
    db: Session = Depends(get_db),
):
    """Generate comprehensive quality and defect intelligence analytics, optionally filtered by year."""
    target_year = _unwrap(year)

    shell_base = db.query(Shell)
    doc_base = db.query(Document)

    if target_year is not None:
        shell_base = shell_base.filter(Shell.data_year == target_year)
        doc_base = doc_base.filter(Document.data_year == target_year)

    total_shells = shell_base.count()
    total_docs = doc_base.count()
    qdr_docs = doc_base.filter(Document.doc_type.in_(["QDR_EXTERNAL", "QDR_INTERNAL"])).all()
    qdr_count = len(qdr_docs)

    # 1. Defect Category Pareto Breakdown
    category_counts = {k: 0 for k in DEFECT_PATTERNS.keys()}
    category_counts["Other / General"] = 0
    judgment_counts = {"Reject": 0, "Rework able": 0, "Concession": 0, "Other": 0}

    for doc in qdr_docs:
        desc = doc.defect_description or ""
        matched = False
        for cat, pattern in DEFECT_PATTERNS.items():
            if pattern.search(desc):
                category_counts[cat] += 1
                matched = True
        if not matched:
            category_counts["Other / General"] += 1

        judgment = (doc.defect_judgment or "").strip().lower()
        if "reject" in judgment:
            judgment_counts["Reject"] += 1
        elif "rework" in judgment:
            judgment_counts["Rework able"] += 1
        elif "concession" in judgment or "accept" in judgment:
            judgment_counts["Concession"] += 1
        else:
            judgment_counts["Other"] += 1

    # Format Pareto list sorted descending based on total categorized defect occurrences
    total_defect_occurrences = sum(v for v in category_counts.values())
    pareto_list = [
        {
            "category": k,
            "count": v,
            "pct": round((v / total_defect_occurrences * 100.0) if total_defect_occurrences > 0 else 0, 1),
        }
        for k, v in category_counts.items() if v > 0
    ]
    pareto_list.sort(key=lambda x: x["count"], reverse=True)

    # Cumulative %
    cum = 0.0
    for idx, item in enumerate(pareto_list):
        cum += item["pct"]
        if idx == len(pareto_list) - 1:
            item["cumulative_pct"] = 100.0
        else:
            item["cumulative_pct"] = round(min(100.0, cum), 1)

    # 2. Alloy Rejection & Rework Rates and 3. Lot Heatmap (Optimized SQL Aggregation)
    alloy_query = db.query(Shell.material_standard, func.count(Shell.id)).filter(Shell.material_standard.isnot(None))
    lot_query = db.query(Shell.lot_number, func.count(Shell.id)).filter(Shell.lot_number.isnot(None))
    if target_year is not None:
        alloy_query = alloy_query.filter(Shell.data_year == target_year)
        lot_query = lot_query.filter(Shell.data_year == target_year)

    alloy_total_map = {
        mat: count for mat, count in alloy_query.group_by(Shell.material_standard).all()
        if mat and not mat.isdigit()
    }

    lot_total_map = {
        lot: count for lot, count in lot_query.group_by(Shell.lot_number).all()
        if lot is not None
    }

    # Fetch all linked QDR defect documents with shell attributes in a single fast JOIN query
    qdr_links_query = db.query(
        Document.shell_id,
        Document.defect_judgment,
        Shell.material_standard,
        Shell.lot_number
    ).join(Shell, Document.shell_id == Shell.id).filter(
        Document.doc_type.in_(["QDR_EXTERNAL", "QDR_INTERNAL"])
    )
    if target_year is not None:
        qdr_links_query = qdr_links_query.filter(Shell.data_year == target_year)
    qdr_links = qdr_links_query.all()

    # Aggregate by alloy
    alloy_data = {mat: {"qdr_count": 0, "reject_count": 0, "rework_count": 0, "shell_ids": set()} for mat in alloy_total_map}
    lot_data = {lot: {"qdr_count": 0, "shell_ids": set()} for lot in lot_total_map}

    for shell_id, judgment_raw, mat, lot in qdr_links:
        judgment = (judgment_raw or "").lower()
        if mat in alloy_data:
            alloy_data[mat]["qdr_count"] += 1
            if shell_id:
                alloy_data[mat]["shell_ids"].add(shell_id)
            if "reject" in judgment:
                alloy_data[mat]["reject_count"] += 1
            elif "rework" in judgment:
                alloy_data[mat]["rework_count"] += 1

        if lot in lot_data:
            lot_data[lot]["qdr_count"] += 1
            if shell_id:
                lot_data[lot]["shell_ids"].add(shell_id)

    # Format alloy statistics
    alloy_stats = []
    for mat, total_count in alloy_total_map.items():
        data = alloy_data.get(mat, {"qdr_count": 0, "reject_count": 0, "rework_count": 0, "shell_ids": set()})
        total_defect_shells = len(data["shell_ids"])
        defect_rate = round((total_defect_shells / total_count * 100.0) if total_count > 0 else 0.0, 1)
        rejection_rate = round((data["reject_count"] / total_count * 100.0) if total_count > 0 else 0.0, 1)

        alloy_stats.append({
            "alloy": mat,
            "total_cast": total_count,
            "defect_count": data["qdr_count"],
            "defect_shells": total_defect_shells,
            "reject_count": data["reject_count"],
            "rework_count": data["rework_count"],
            "defect_rate_pct": defect_rate,
            "rejection_rate_pct": rejection_rate,
        })
    alloy_stats.sort(key=lambda x: x["total_cast"], reverse=True)

    # Format lot heatmap
    lot_heatmap = []
    for lot_num in sorted(lot_total_map.keys()):
        total_count = lot_total_map[lot_num]
        qdr_lot_count = lot_data[lot_num]["qdr_count"]
        defect_density = round((qdr_lot_count / total_count * 100.0) if total_count > 0 else 0, 1)

        if defect_density == 0:
            severity = "clean"
        elif defect_density <= 25:
            severity = "low"
        elif defect_density <= 50:
            severity = "medium"
        else:
            severity = "high"

        lot_heatmap.append({
            "lot_number": lot_num,
            "total_shells": total_count,
            "defect_count": qdr_lot_count,
            "defect_density_pct": defect_density,
            "severity": severity,
        })

    # Overall Quality Metrics (unique shells with ≥1 QDAR, not total QDAR count)
    unique_defect_shell_ids = set()
    for shell_id, _, _, _ in qdr_links:
        if shell_id is not None:
            unique_defect_shell_ids.add(shell_id)
    overall_defect_rate = round((len(unique_defect_shell_ids) / total_shells * 100.0) if total_shells > 0 else 0, 1)

    # 4. Casting Intelligence & Weight Variance Analytics
    shells_with_act_wt_q = db.query(Shell).filter(Shell.actual_weight.isnot(None), Shell.actual_weight > 0)
    if target_year is not None:
        shells_with_act_wt_q = shells_with_act_wt_q.filter(Shell.data_year == target_year)
    shells_with_act_wt = shells_with_act_wt_q.all()
    total_act_wt_kg = sum(s.actual_weight for s in shells_with_act_wt)
    
    # Calculate job allowable weight for shells that have target weights
    shells_with_job_wt = [s for s in shells_with_act_wt if (s.job_card_weight or s.weight)]
    total_job_wt_kg = sum((s.job_card_weight or s.weight or 0) for s in shells_with_job_wt)
    
    # Weight variance computed on shells with known actual and allowable weights
    shells_with_diff = [
        s for s in shells_with_act_wt 
        if s.weight_diff is not None or (s.actual_weight is not None and (s.job_card_weight or s.weight) is not None)
    ]
    
    def _calc_diff(s):
        if s.weight_diff is not None:
            return s.weight_diff
        allowable = s.job_card_weight or s.weight
        return (s.actual_weight - allowable) if (s.actual_weight and allowable) else 0.0

    total_wt_diff_kg = round(sum(_calc_diff(s) for s in shells_with_diff), 1)
    overweight_count = sum(1 for s in shells_with_diff if _calc_diff(s) > 0)
    underweight_count = sum(1 for s in shells_with_diff if _calc_diff(s) < 0)
    avg_diff_kg = round(total_wt_diff_kg / len(shells_with_diff), 1) if shells_with_diff else 0.0

    # Monthly Casting Throughput
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_aliases = {
        "june": "Jun", "july": "Jul", "sept": "Sep", "september": "Sep",
        "january": "Jan", "february": "Feb", "march": "Mar", "april": "Apr",
        "august": "Aug", "october": "Oct", "november": "Nov", "december": "Dec",
        "1": "Jan", "01": "Jan", "2": "Feb", "02": "Feb", "3": "Mar", "03": "Mar",
        "4": "Apr", "04": "Apr", "5": "May", "05": "May", "6": "Jun", "06": "Jun",
        "7": "Jul", "07": "Jul", "8": "Aug", "08": "Aug", "9": "Sep", "09": "Sep",
        "10": "Oct", "11": "Nov", "12": "Dec",
    }
    monthly_raw_q = db.query(
        Shell.month,
        func.count(Shell.id),
        func.sum(Shell.actual_weight)
    ).filter(Shell.month.isnot(None))
    if target_year is not None:
        monthly_raw_q = monthly_raw_q.filter(Shell.data_year == target_year)
    monthly_raw = monthly_raw_q.group_by(Shell.month).all()

    monthly_map = {}
    for m in monthly_raw:
        if not m[0]:
            continue
        m_name = str(m[0]).strip()
        canonical_m = month_aliases.get(m_name.lower(), month_aliases.get(m_name, m_name.capitalize()))
        if canonical_m in monthly_map:
            monthly_map[canonical_m]["count"] += m[1]
            monthly_map[canonical_m]["tonnage"] = round(monthly_map[canonical_m]["tonnage"] + ((m[2] or 0) / 1000.0), 2)
        else:
            monthly_map[canonical_m] = {"month": canonical_m, "count": m[1], "tonnage": round((m[2] or 0) / 1000.0, 2)}

    monthly_stats = []
    for mo in month_order:
        if mo in monthly_map:
            monthly_stats.append(monthly_map[mo])
    for mo, item in monthly_map.items():
        if mo not in month_order:
            monthly_stats.append(item)

    # Molding & Core Process Breakdown
    mold_raw_q = db.query(Shell.mold_process, func.count(Shell.id)).filter(Shell.mold_process.isnot(None))
    core_raw_q = db.query(Shell.core_process, func.count(Shell.id)).filter(Shell.core_process.isnot(None))
    if target_year is not None:
        mold_raw_q = mold_raw_q.filter(Shell.data_year == target_year)
        core_raw_q = core_raw_q.filter(Shell.data_year == target_year)
    mold_raw = mold_raw_q.group_by(Shell.mold_process).all()
    core_raw = core_raw_q.group_by(Shell.core_process).all()
    mold_breakdown = [{"process": m[0], "count": m[1]} for m in mold_raw if m[0]]
    core_breakdown = [{"process": c[0], "count": c[1]} for c in core_raw if c[0]]

    tech_raw_q = db.query(Shell.technology, func.count(Shell.id)).filter(Shell.technology.isnot(None))
    if target_year is not None:
        tech_raw_q = tech_raw_q.filter(Shell.data_year == target_year)
    technology_raw = tech_raw_q.group_by(Shell.technology).all()
    tech_breakdown = [{"technology": t[0], "count": t[1]} for t in technology_raw if t[0]]
    tech_breakdown.sort(key=lambda x: x["count"], reverse=True)

    return {
        "kpi": {
            "total_shells": total_shells,
            "total_documents": total_docs,
            "total_qdars": qdr_count,
            "defect_rate_pct": overall_defect_rate,
            "judgments": judgment_counts,
            # Casting KPIs
            "total_actual_tonnage": round(total_act_wt_kg / 1000.0, 2),
            "total_job_tonnage": round(total_job_wt_kg / 1000.0, 2),
            "net_weight_variance_kg": total_wt_diff_kg,
            "avg_weight_diff_kg": avg_diff_kg,
            "overweight_shells": overweight_count,
            "underweight_shells": underweight_count,
            "total_cast_logged": len(shells_with_act_wt),
        },
        "pareto_distribution": pareto_list,
        "alloy_quality": alloy_stats,
        "lot_heatmap": lot_heatmap,
        "casting_analytics": {
            "monthly_throughput": monthly_stats,
            "mold_processes": mold_breakdown,
            "core_processes": core_breakdown,
            "technologies": tech_breakdown[:8],
        },
    }
