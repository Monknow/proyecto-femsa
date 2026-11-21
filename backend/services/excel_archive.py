import asyncio
from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Optional

ARCHIVE_DIR = Path("uploaded_excels")


def _sanitize_filename(name: str) -> str:
    """Strip directory paths and unsafe characters from an uploaded filename."""
    clean_name = Path(name).name
    return re.sub(r"[^a-zA-Z0-9._-]", "_", clean_name)


def _write_bytes_sync(target_path: Path, data: bytes) -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(data)


async def archive_uploaded_excel(
    file_bytes: bytes,
    original_filename: str,
    *,
    server_count: Optional[int] = None,
    vuln_count: Optional[int] = None,
    tag: Optional[str] = None,
) -> Path:
    """
    Save an uploaded Excel file into `uploaded_excels/` with a UTC timestamp
    and summary metadata embedded in the filename.

    Example output filename:
        20261120_161800__srv-14_vuln-285__inventario_nov.xlsx
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_original = _sanitize_filename(original_filename or "upload.xlsx")

    # Build metadata tags so you can identify what is inside without opening Excel
    meta_parts: list[str] = []
    if tag:
        meta_parts.append(_sanitize_filename(tag))
    if server_count is not None:
        meta_parts.append(f"srv-{server_count}")
    if vuln_count is not None:
        meta_parts.append(f"vuln-{vuln_count}")

    meta_segment = f"__{'_'.join(meta_parts)}" if meta_parts else ""
    archived_name = f"{timestamp}{meta_segment}__{safe_original}"
    target_path = ARCHIVE_DIR / archived_name

    await asyncio.to_thread(_write_bytes_sync, target_path, file_bytes)
    return target_path