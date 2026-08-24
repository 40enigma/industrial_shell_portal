"""
Document routes — File serving, real downloads, local launches, and defect metadata.
"""
import io
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Shell, Document

router = APIRouter(prefix="/api/documents", tags=["documents"])


class DownloadSelectionRequest(BaseModel):
    """Request body for selective file download."""
    doc_ids: List[int]
    job_number: str | None = None
    include_dossier: bool = False


def _format_file_size(size_bytes: int) -> str:
    """Format bytes into readable KB/MB string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def _build_doc_file_info(d: Document) -> dict:
    """Extract full file metadata including existence, sizes, and defect reports."""
    file_path_obj = Path(d.file_path) if d.file_path else None
    file_exists = file_path_obj.exists() if file_path_obj else False
    size_bytes = file_path_obj.stat().st_size if file_exists else 0

    return {
        "id": d.id,
        "doc_type": d.doc_type,
        "doc_number": d.doc_number,
        "file_name": file_path_obj.name if file_path_obj else None,
        "file_path": str(file_path_obj) if file_path_obj else None,
        "file_size_bytes": size_bytes,
        "file_size_formatted": _format_file_size(size_bytes) if file_exists else "—",
        "sheet_name": d.sheet_name,
        "job_number": d.job_number,
        "piece_number": d.piece_number,
        "drawing_number": d.drawing_number,
        "customer_name": d.customer_name,
        "defect_judgment": d.defect_judgment,
        "defect_description": d.defect_description,
        "status": d.status,
        "data_year": d.data_year,
        "is_available": file_exists,
        "unavailable_reason": d.unavailable_reason if not file_exists else None,
    }


@router.get("/shell/{shell_id}/files")
def list_shell_files(shell_id: int, db: Session = Depends(get_db)):
    """List all original source files linked to a shell for checkbox selection."""
    shell = db.query(Shell).filter(Shell.id == shell_id).first()
    if not shell:
        raise HTTPException(status_code=404, detail="Shell not found")

    filters = [Document.shell_id == shell.id]
    if shell.job_number:
        filters.append(Document.job_number == shell.job_number)
    docs = db.query(Document).filter(or_(*filters)).all()

    files = [_build_doc_file_info(d) for d in docs]

    return {
        "shell_id": shell.id,
        "job_number": shell.job_number,
        "shell_name": shell.shell_name,
        "lot_number": shell.lot_number,
        "material_standard": shell.material_standard,
        "total_files": len(files),
        "available_files": sum(1 for f in files if f["is_available"]),
        "files": files,
    }


@router.get("/job/{job_number}/files")
def list_job_files(job_number: str, db: Session = Depends(get_db)):
    """List all original source files linked to a specific Job Number."""
    shell = db.query(Shell).filter(Shell.job_number == job_number).first()
    query_filters = [Document.job_number == job_number]
    if shell:
        query_filters.append(Document.shell_id == shell.id)

    docs = db.query(Document).filter(or_(*query_filters)).all()
    files = [_build_doc_file_info(d) for d in docs]

    return {
        "job_number": job_number,
        "shell_id": shell.id if shell else None,
        "shell_name": shell.shell_name if shell else None,
        "lot_number": shell.lot_number if shell else None,
        "material_standard": shell.material_standard if shell else None,
        "total_files": len(files),
        "available_files": sum(1 for f in files if f["is_available"]),
        "files": files,
    }


@router.post("/download-selected")
def download_selected_files(
    request: DownloadSelectionRequest,
    db: Session = Depends(get_db),
):
    """
    Download selected document files. If only 1 file is selected and no dossier requested,
    returns the original file directly. If multiple files (or dossier included), returns a ZIP bundle.
    """
    if not request.doc_ids and not request.include_dossier:
        raise HTTPException(status_code=400, detail="No document IDs or dossier requested")

    docs = db.query(Document).filter(Document.id.in_(request.doc_ids)).all() if request.doc_ids else []
    available_docs = [d for d in docs if d.file_path and Path(d.file_path).exists()]

    if not available_docs and not request.include_dossier:
        raise HTTPException(status_code=404, detail="None of the selected files are available on disk")

    job_label = request.job_number or (available_docs[0].job_number if available_docs else "JOB")
    clean_job = str(job_label).replace("/", "_").replace("\\", "_").replace(" ", "_")

    # Single file without dossier — return original file directly
    if len(available_docs) == 1 and not request.include_dossier:
        d = available_docs[0]
        file_path = Path(d.file_path)
        suffix = file_path.suffix.lower()
        media_types = {
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".pdf": "application/pdf",
            ".csv": "text/csv",
        }
        highlighted = f"[JOB_{clean_job}]_{file_path.name}"
        return FileResponse(
            path=str(file_path),
            filename=highlighted,
            media_type=media_types.get(suffix, "application/octet-stream"),
            headers={"Content-Disposition": f'attachment; filename="{highlighted}"'},
        )

    # Multiple files or dossier requested — return ZIP bundle
    shell = db.query(Shell).filter(Shell.job_number == job_label).first()

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # Include Dossier if requested or multiple files
        if request.include_dossier or len(available_docs) > 1:
            dossier_text = [
                "=" * 70,
                f" INDUSTRIAL SHELL FOUNDRY INTELLIGENCE DOSSIER",
                f" TARGET JOB NUMBER: {job_label}",
                "=" * 70,
                "",
                "1. IDENTIFICATION & BLUEPRINT:",
                f"   - Job Number:         {job_label}",
                f"   - Shell Name:         {shell.shell_name if shell else 'N/A'}",
                f"   - Piece Number:       {shell.piece_number if shell else 'N/A'}",
                f"   - Shell Type:         {shell.shell_type if shell else 'N/A'}",
                f"   - Alloy Standard:     {shell.material_standard if shell else 'N/A'}",
                f"   - Drawing Number:     {shell.drawing_number if shell else 'N/A'}",
                f"   - Lot Number:         #{shell.lot_number if shell else 'N/A'}",
                f"   - Data Year:          {shell.data_year if shell else 'N/A'}",
                "",
                "2. DIMENSIONAL MATRIX (mm):",
                f"   - Target Finish:      OD {shell.od if shell else '—'} mm | ID {shell.id_dim if shell else '—'} mm | L {shell.length if shell else '—'} mm",
                f"   - As-Cast Raw Stock:  OD {shell.cast_od if shell else '—'} mm | ID {shell.cast_id if shell else '—'} mm | L {shell.cast_length if shell else '—'} mm",
                "",
                "3. CASTING WEIGHT & TRACKING:",
                f"   - Actual Cast Weight: {shell.actual_weight if shell else '—'} kg",
                f"   - Job Card Weight:    {shell.job_card_weight or (shell.weight if shell else None) or '—'} kg",
                f"   - Weight Difference:  {shell.weight_diff if shell else '—'} kg",
                f"   - Cast Date:          {shell.cast_date if shell else '—'}",
                f"   - Molding Process:    {shell.mold_process if shell else 'Alpha Set'}",
                "",
                "4. INCLUDED SOURCE FILES:",
            ]
            for i, d in enumerate(available_docs, 1):
                dossier_text.append(f"   [{i}] {d.doc_type}: {Path(d.file_path).name} (Sheet: {d.sheet_name or 'Master'})")
            zf.writestr(f"[JOB_{clean_job}]_INTELLIGENCE_DOSSIER.txt", "\n".join(dossier_text))

        # Add each original file
        added_names = set()
        for d in available_docs:
            src_path = Path(d.file_path)
            doc_kind = d.doc_type.replace("QDR_", "QDR_").replace("CASTING_LOG", "CastingLog")
            archive_name = f"[JOB_{clean_job}]_{doc_kind}_{src_path.name}"
            if archive_name in added_names:
                archive_name = f"[JOB_{clean_job}]_{doc_kind}_{d.id}_{src_path.name}"
            added_names.add(archive_name)
            zf.write(src_path, arcname=archive_name)

    zip_buffer.seek(0)
    bundle_name = f"[JOB_{clean_job}]_Selected_Files.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{bundle_name}"'},
    )



@router.get("/{doc_id}/info")
def document_info(doc_id: int, db: Session = Depends(get_db)):
    """Return full metadata and defect report details for a document."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in database")

    file_exists = Path(doc.file_path).exists() if doc.file_path else False

    return {
        "id": doc.id,
        "shell_id": doc.shell_id,
        "doc_type": doc.doc_type,
        "doc_number": doc.doc_number,
        "file_path": doc.file_path,
        "file_name": Path(doc.file_path).name if doc.file_path else None,
        "sheet_name": doc.sheet_name,
        "job_number": doc.job_number,
        "piece_number": doc.piece_number,
        "customer_name": doc.customer_name,
        "part_name": doc.part_name,
        "drawing_number": doc.drawing_number,
        "doc_date": doc.doc_date,
        "defect_description": doc.defect_description,
        "defect_judgment": doc.defect_judgment,
        "detected_at": doc.detected_at,
        "detected_by": doc.detected_by,
        "responsibility": doc.responsibility,
        "status": doc.status,
        "data_year": doc.data_year,
        "is_available": file_exists,
        "unavailable_reason": doc.unavailable_reason if not file_exists else None,
    }


@router.get("/{doc_id}/download")
@router.get("/{doc_id}/open")
def download_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Stream and download the original .xls / .xlsx document from disk.
    Gracefully handles missing or rollover files.
    """
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in database")

    if not doc.file_path:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "No file path associated with this document record",
                "doc_type": doc.doc_type,
                "job_number": doc.job_number,
            },
        )

    file_path = Path(doc.file_path)
    if not file_path.exists():
        reason = doc.unavailable_reason or "File not found on disk"
        raise HTTPException(
            status_code=404,
            detail={
                "message": reason,
                "file_path": str(file_path),
                "doc_type": doc.doc_type,
                "job_number": doc.job_number,
                "is_rollover": "2024 Rollover" in (doc.unavailable_reason or ""),
            },
        )

    suffix = file_path.suffix.lower()
    media_types = {
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".xls": "application/vnd.ms-excel",
        ".pdf": "application/pdf",
        ".csv": "text/csv",
    }
    media_type = media_types.get(suffix, "application/octet-stream")

    job_prefix = f"[JOB_{doc.job_number}]_" if doc.job_number else ""
    highlighted_filename = f"{job_prefix}{file_path.name}"

    return FileResponse(
        path=str(file_path),
        filename=highlighted_filename,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{highlighted_filename}"'},
    )


@router.get("/job/{job_number}/download-bundle")
@router.get("/shell/{shell_id}/download-bundle")
def download_job_bundle(
    job_number: str | None = None,
    shell_id: int | None = None,
    db: Session = Depends(get_db),
):
    """
    Download a ZIP bundle containing all engineering documents and an intelligence dossier
    for a specific Job Number or Shell ID, with the Job Number highlighted across all filenames.
    """
    shell = None
    if shell_id:
        shell = db.query(Shell).filter(Shell.id == shell_id).first()
    if not shell and job_number:
        shell = db.query(Shell).filter(Shell.job_number == job_number).first()

    target_job = (shell.job_number if shell else job_number) or "UNKNOWN_JOB"
    clean_job = str(target_job).replace("/", "_").replace("\\", "_").replace(" ", "_")

    # Find all documents linked to shell or job_number
    query_filters = []
    if shell:
        query_filters.append(Document.shell_id == shell.id)
    if target_job:
        query_filters.append(Document.job_number == target_job)

    docs = db.query(Document).filter(or_(*query_filters)).all() if query_filters else []

    # Create in-memory zip bundle
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Add Job Dossier Summary text file
        summary_text = [
            "=" * 70,
            f" INDUSTRIAL SHELL FOUNDRY INTELLIGENCE DOSSIER",
            f" TARGET JOB NUMBER: {target_job}",
            "=" * 70,
            "",
            "1. IDENTIFICATION & BLUEPRINT:",
            f"   - Job Number:         {target_job}",
            f"   - Shell Name:         {shell.shell_name if shell else 'N/A'}",
            f"   - Piece Number:       {shell.piece_number if shell else 'N/A'}",
            f"   - Shell Type:         {shell.shell_type if shell else 'N/A'}",
            f"   - Alloy Standard:     {shell.material_standard if shell else 'N/A'}",
            f"   - Drawing Number:     {shell.drawing_number if shell else 'N/A'}",
            f"   - IDM Number:         {shell.idm_number if shell else 'N/A'}",
            f"   - Foundry Lot Number: #{shell.lot_number if shell else 'N/A'}",
            f"   - Serial Number:      #{shell.serial_number if shell else 'N/A'}",
            f"   - Data Year:          {shell.data_year if shell else 'N/A'}",
            "",
            "2. DIMENSIONAL MATRIX (mm):",
            f"   - Target Finish:      OD {shell.od if shell else '—'} mm | ID {shell.id_dim if shell else '—'} mm | L {shell.length if shell else '—'} mm | Wall {shell.wall_thickness if shell else '—'} mm",
            f"   - As-Cast Raw Stock:  OD {shell.cast_od if shell else '—'} mm | ID {shell.cast_id if shell else '—'} mm | L {shell.cast_length if shell else '—'} mm | Wall {shell.cast_wall_thickness if shell else '—'} mm",
            f"   - Machining Cuts:     OD Cut: +{((shell.cast_od - shell.od)/2.0):.1f} mm/side | ID Cut: +{((shell.id_dim - shell.cast_id)/2.0):.1f} mm/side" if (shell and shell.cast_od and shell.od and shell.id_dim and shell.cast_id) else "   - Machining Cuts:     Standard allowance",
            "",
            "3. CASTING WEIGHT & FOUNDRY PARAMETERS:",
            f"   - Actual Cast Weight: {shell.actual_weight if shell else '—'} kg",
            f"   - Job Card Weight:    {shell.job_card_weight or (shell.weight if shell else None) or '—'} kg",
            f"   - Weight Variance:    {shell.weight_diff if shell else '—'} kg",
            f"   - Cast / Shift Date:  {shell.cast_date if shell else '—'} (Month: {shell.month if shell else '—'})",
            f"   - Molding Process:    {shell.mold_process if shell else 'Alpha Set'}",
            f"   - Core Process:       {shell.core_process if shell else 'Alpha Set'}",
            f"   - Technology/Riser:   {shell.technology if shell else 'Standard'}",
            "",
            "4. CHEMICAL COMPOSITION (% Weight):",
            f"   - %C:  {shell.c_pct if shell and shell.c_pct else '3.30'} | %Si: {shell.si_pct if shell and shell.si_pct else '1.90'} | %Mn: {shell.mn_pct if shell and shell.mn_pct else '0.70'} | %P: {shell.p_pct if shell and shell.p_pct else '0.05'}",
            f"   - %S:  {shell.s_pct if shell and shell.s_pct else '0.04'} | %Cr: {shell.cr_pct if shell and shell.cr_pct else '0.40'} | %Ni: {shell.ni_pct if shell and shell.ni_pct else '0.50'} | %Mo: {shell.mo_pct if shell and shell.mo_pct else '0.25'}",
            "",
            "5. MECHANICAL TESTING PROPERTIES:",
            f"   - Hardness:           {shell.hardness_bhn if shell and shell.hardness_bhn else 225} BHN",
            f"   - Tensile Strength:   {shell.tensile_strength if shell and shell.tensile_strength else 300} MPa",
            f"   - Yield Strength:     {shell.yield_strength if shell and shell.yield_strength else 210} MPa",
            f"   - Elongation:         {shell.elongation_pct if shell and shell.elongation_pct else 0.8}%",
            "",
            "6. LINKED ENGINEERING DOCUMENTS & QUALITY TICKETS:",
        ]

        if not docs:
            summary_text.append("   (No separate workbook documents were linked to this job record)")
        else:
            for i, d in enumerate(docs, 1):
                summary_text.append(f"   [{i}] Type: {d.doc_type} | Doc #: {d.doc_number or d.sheet_name or 'N/A'}")
                if d.defect_judgment:
                    summary_text.append(f"       Judgment:    {d.defect_judgment}")
                if d.defect_description:
                    summary_text.append(f"       Description: {d.defect_description}")
                if d.detected_at:
                    summary_text.append(f"       Detected At: {d.detected_at}")
                if d.customer_name:
                    summary_text.append(f"       Customer:    {d.customer_name}")
                summary_text.append(f"       File Disk:   {'Available' if (d.file_path and Path(d.file_path).exists()) else 'Archived / Rollover'}")
                summary_text.append("")

        zf.writestr(f"[JOB_{clean_job}]_FOUNDRY_INTELLIGENCE_DOSSIER.txt", "\n".join(summary_text))

        # 2. Add actual document files with [JOB_XXX] prefix
        added_names = set()
        for d in docs:
            if d.file_path and Path(d.file_path).exists():
                src_path = Path(d.file_path)
                doc_kind = d.doc_type.replace("QDR_", "QDR_").replace("CASTING_LOG", "CastingLog")
                archive_filename = f"[JOB_{clean_job}]_{doc_kind}_{src_path.name}"
                if archive_filename in added_names:
                    archive_filename = f"[JOB_{clean_job}]_{doc_kind}_{d.id}_{src_path.name}"
                added_names.add(archive_filename)
                zf.write(src_path, arcname=archive_filename)

    zip_buffer.seek(0)
    bundle_filename = f"[JOB_{clean_job}]_Complete_Engineering_Bundle.zip"

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{bundle_filename}"'},
    )


@router.get("/{doc_id}/launch")
def launch_document(doc_id: int, db: Session = Depends(get_db)):
    """Open document in the default local operating system application (Excel/PDF reader)."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.file_path:
        raise HTTPException(status_code=404, detail="No file path associated with document")

    file_path = Path(doc.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=doc.unavailable_reason or "File not found on disk",
        )

    try:
        if sys.platform == "win32":
            os.startfile(str(file_path))
        else:
            subprocess.Popen(["xdg-open", str(file_path)])
        return {"status": "launched", "file": file_path.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to launch file locally: {e}")
