"""
SQLAlchemy ORM models for the Industrial Shell Portal.

Models:
- Shell: Manufactured casting shell with dimensional, metallurgical, and mechanical properties.
- Document: Linked engineering documents (M&Q plans, QDR reports, QAD sheets) with defect logs.
- IngestionBatch: Archive upload & batch ETL execution history.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, Index
)
from sqlalchemy.orm import relationship
from database.db import Base


class Shell(Base):
    """Manufactured casting shell with dimensional, chemical, and mechanical data."""
    __tablename__ = "shells"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Identifiers
    job_number = Column(String(100), nullable=False, index=True)
    piece_number = Column(String(50), nullable=True)
    shell_name = Column(String(255), nullable=True)
    shell_type = Column(String(100), nullable=True, index=True)
    material_standard = Column(String(100), nullable=True, index=True)
    drawing_number = Column(String(100), nullable=True, index=True)
    idm_number = Column(String(100), nullable=True, index=True)
    lot_number = Column(Integer, nullable=True, index=True)
    serial_number = Column(Integer, nullable=True)
    data_year = Column(Integer, nullable=False, default=2025, index=True)
    # Weight tracking (kg)
    weight = Column(Float, nullable=True, index=True)              # Job card allowable weight
    actual_weight = Column(Float, nullable=True, index=True)       # Measured as-cast weight
    job_card_weight = Column(Float, nullable=True)                 # Job card allowable weight
    calculated_weight = Column(Float, nullable=True)               # Calculated weight from dimensions
    weight_diff = Column(Float, nullable=True)                     # Weight difference (Actual - Job Card)

    # Finish (machined target) dimensions in mm
    od = Column(Float, nullable=True, index=True)           # Outer Diameter
    id_dim = Column(Float, nullable=True, index=True)       # Inner Diameter
    length = Column(Float, nullable=True, index=True)       # Length
    wall_thickness = Column(Float, nullable=True, index=True)  # (OD - ID) / 2

    # Casted (as-cast raw stock) dimensions in mm
    cast_od = Column(Float, nullable=True, index=True)
    cast_id = Column(Float, nullable=True, index=True)
    cast_length = Column(Float, nullable=True, index=True)
    cast_wall_thickness = Column(Float, nullable=True, index=True)  # (Cast OD - Cast ID) / 2

    # Foundry / Pattern / Tooling Parameters
    pattern_size_ca = Column(Float, nullable=True)          # Size with Contraction Allowance (mm)
    core_box = Column(Float, nullable=True)                 # Core box size (mm)
    mold_process = Column(String(100), nullable=True)       # Mold method (e.g. Alpha Set)
    core_process = Column(String(100), nullable=True)       # Core method (e.g. Alpha Set, Dolomite)
    riser_pct = Column(Float, nullable=True)                # Riser percentage (%)
    technology = Column(String(255), nullable=True)         # Foundry technology / riser setup
    simulation_path = Column(Text, nullable=True)           # Simulation file path
    shaft_fitting = Column(String(100), nullable=True)      # Shaft fitting info
    month = Column(String(50), nullable=True, index=True)   # Casting month

    # Metallurgy / Chemical Composition (%)
    c_pct = Column(Float, nullable=True)    # Carbon %
    si_pct = Column(Float, nullable=True)   # Silicon %
    mn_pct = Column(Float, nullable=True)   # Manganese %
    p_pct = Column(Float, nullable=True)    # Phosphorus %
    s_pct = Column(Float, nullable=True)    # Sulfur %
    cr_pct = Column(Float, nullable=True)   # Chromium %
    ni_pct = Column(Float, nullable=True)   # Nickel %
    mo_pct = Column(Float, nullable=True)   # Molybdenum %

    # Mechanical Testing Properties
    hardness_bhn = Column(Float, nullable=True)      # Hardness (Brinell / BHN)
    tensile_strength = Column(Float, nullable=True)  # Tensile Strength (MPa / N/mm²)
    yield_strength = Column(Float, nullable=True)    # Yield Strength (MPa)
    elongation_pct = Column(Float, nullable=True)    # Elongation (%)

    # Casting operation tracking
    heat_number = Column(String(100), nullable=True)
    cast_date = Column(String(50), nullable=True, index=True)      # Actual Shifting / Casting Date
    status = Column(String(50), nullable=False, default="COMPLETE", index=True)

    # Relationships
    documents = relationship("Document", back_populates="shell", cascade="all, delete-orphan")

    def __repr__(self):
        return (
            f"<Shell(id={self.id}, job={self.job_number}, piece={self.piece_number}, "
            f"od={self.od}, id={self.id_dim}, len={self.length}, wt={self.wall_thickness})>"
        )


class Document(Base):
    """Linked document (M&Q plan, QDR report, QAD sheet) with quality & defect data."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    shell_id = Column(Integer, ForeignKey("shells.id"), nullable=True, index=True)

    # Document classification
    doc_type = Column(String(20), nullable=False, index=True)  # MQ, CASTING_LOG, QDR_EXTERNAL, QDR_INTERNAL, QAD
    doc_number = Column(String(100), nullable=True, index=True)

    # File location
    file_path = Column(Text, nullable=True)
    sheet_name = Column(String(100), nullable=True)

    # Linking & Order metadata
    job_number = Column(String(100), nullable=True, index=True)
    piece_number = Column(String(50), nullable=True)
    customer_name = Column(String(255), nullable=True, index=True)
    part_name = Column(String(255), nullable=True)
    drawing_number = Column(String(100), nullable=True, index=True)
    doc_date = Column(String(50), nullable=True)

    # Defect intelligence
    defect_description = Column(Text, nullable=True)
    defect_judgment = Column(String(100), nullable=True)   # Reject, Rework able, Concession
    detected_at = Column(String(255), nullable=True)       # Detection stage / location
    detected_by = Column(String(100), nullable=True)       # Inspector name
    responsibility = Column(String(100), nullable=True)    # Dept / Process responsible

    # Availability & Linking status
    is_available = Column(Boolean, nullable=False, default=True)
    unavailable_reason = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="LINKED", index=True)  # LINKED, UNLINKED, PARTIAL_ROLLOVER

    # Multi-year support
    data_year = Column(Integer, nullable=False, default=2025, index=True)

    # Relationships
    shell = relationship("Shell", back_populates="documents")

    def __repr__(self):
        return (
            f"<Document(id={self.id}, type={self.doc_type}, job={self.job_number}, "
            f"status={self.status}, available={self.is_available})>"
        )


class IngestionBatch(Base):
    """Tracks full-year archive uploads and background ETL executions."""
    __tablename__ = "ingestion_batches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer, nullable=False, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    filename = Column(String(255), nullable=True)
    total_shells = Column(Integer, default=0)
    total_documents = Column(Integer, default=0)
    status = Column(String(50), default="PROCESSING", index=True)  # PROCESSING, COMPLETED, FAILED
    log_output = Column(Text, nullable=True)

    def __repr__(self):
        return f"<IngestionBatch(id={self.id}, year={self.year}, status={self.status})>"
