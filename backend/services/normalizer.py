"""
Job Number, Piece Number, and Drawing Code Normalization Service.

Provides heuristics for extracting, cleaning, tokenizing, and matching
cross-workbook identifiers across M&Q and QDAR data files.
"""
import re

ROLLOVER_PREFIXES = ("SE24-", "SL24-", "QG24-", "CL24-", "GL24-", "SE23-", "SL23-", "SE22-", "SL22-")


def clean_alphanumeric(val: str | None) -> str:
    """Strip all non-alphanumeric characters and convert to uppercase."""
    if not val:
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(val).upper())


def normalize_job_number(raw: str | None) -> str | None:
    """
    Standardize job number string.
    - Strips whitespace
    - Uppercases
    - Removes trailing .0 float artifacts
    - Eliminates spaces around hyphens (e.g. 'E23- SUBO' -> 'E23-SUBO')
    - Consolidates internal whitespace
    """
    if not raw:
        return None
    s = str(raw).strip().upper()
    if s.endswith(".0"):
        s = s[:-2]
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s if s else None


def extract_base_job(raw: str | None) -> str | None:
    """
    Extract canonical 3-segment base job identifier.
    Example: 'SE24-BSCM-0025-1-1' -> 'SE24-BSCM-0025'
    """
    if not raw:
        return None
    s = str(raw).strip().upper()
    parts = s.split("-")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    return s


def normalize_piece_number(raw: str | None) -> str | None:
    """
    Normalize piece numbers.
    Example: '01/01' -> '1/1', '02-04' -> '2/4', '1/2' -> '1/2'
    """
    if not raw:
        return None
    s = str(raw).strip().replace("-", "/")
    if "/" in s:
        parts = s.split("/")
        try:
            parts = [str(int(p)) for p in parts]
            return "/".join(parts)
        except ValueError:
            pass
    return s


def extract_all_job_tokens(raw_job: str | None, filename: str | None = None) -> list[str]:
    """
    Extract all candidate job tokens from job string and filename.
    Handles joint numbers like 'SE24-CAGS-0013 & 0014' and revisions like '#01-01 (04-01-2025)'.
    """
    text_to_search = f"{raw_job or ''} {filename or ''}".upper()
    tokens = set()

    # Standard full pattern: SE24-CAGS-0013, SL25-JDW1-0711, E23-STRI-0083
    full_matches = re.findall(r"([A-Z]{1,2}\d{2}-[A-Z0-9]{2,6}-\d{3,5})", text_to_search)
    tokens.update(full_matches)

    # Core sequence pattern: CAGS-0013, BSCM-0025
    short_matches = re.findall(r"([A-Z]{3,6}-\d{3,5})", text_to_search)
    tokens.update(short_matches)

    # Multi-number pattern: SE24-CAGS-0013 & 0014 or SE24-CAGS-0013  0014
    amp_matches = re.findall(r"([A-Z]{1,2}\d{2}-[A-Z0-9]+)-(\d+)\s*(?:&|and|,|\s+)\s*(\d+)", text_to_search)
    for prefix, num1, num2 in amp_matches:
        tokens.add(f"{prefix}-{num1}")
        tokens.add(f"{prefix}-{num2}")

    return list(tokens)


def is_rollover_job(job_number: str | None, filename: str | None = None) -> bool:
    """Check if job or filename originated in an earlier year batch."""
    combined = f"{job_number or ''} {filename or ''}".upper()
    return any(combined.startswith(p) or f" {p}" in combined or f"-{p}" in combined for p in ROLLOVER_PREFIXES)
